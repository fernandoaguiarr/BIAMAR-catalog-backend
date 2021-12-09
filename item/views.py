import re
import json

import requests
import pandas as pd
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import NotFound, ValidationError

from django.core.cache import cache
from django.db.models import CharField
from django.db.models.functions import Cast
from django.utils import dateformat, timezone
from django.core.serializers.json import DjangoJSONEncoder

from image.models import Photo
from item.constants import ITEM_REGEX
from item.permissions import DefaultViewSetPermission
from utils.interfaces import CustomViewSet, ERPViewSet
from item.paginations import GroupPagination, SkuPagination
from item.models import Group, Category, Brand, Season, Item, Sku
from item.serializers import GroupSerializer, ItemSerializer, SkuSerializer, BrandSerializer, SeasonSerializer, \
    BannerSerializer


class GroupViewSet(viewsets.ViewSet, CustomViewSet):

    def __init__(self, **kwargs):
        filters = {
            'category': {'klass': Category, 'query_key': 'id', 'prefix': 'group_set__'},
            'brand': {'klass': Brand, 'query_key': 'id', 'prefix': 'group_set__'},
            'season': {'klass': Season, 'query_key': 'id', 'prefix': 'group_set__'},
        }
        CustomViewSet.__init__(self, filters=filters)

    @staticmethod
    def get_queryset():
        return Group.objects.order_by('-code')

    def get_permissions(self):
        return [IsAuthenticated(), DefaultViewSetPermission()]

    def list(self, request):
        query_params = request.query_params.copy()
        queryset = self.get_queryset()
        code = {}
        if query_params:
            if 'code' in query_params:
                code['as_char__contains'] = query_params['code']
                del query_params['code']
            filters = self.get_filter_object(query_params)
            queryset = queryset.annotate(as_char=Cast('code', CharField())).filter(**{**filters, **code}).distinct()

        paginator = GroupPagination()
        page = paginator.paginate_queryset(queryset, request)
        serializer = GroupSerializer(page, many=True)

        if serializer.data:
            return paginator.get_paginated_response(serializer.data)
        raise NotFound()


class ItemViewSet(viewsets.ViewSet, CustomViewSet, ERPViewSet):
    def __init__(self, **kwargs):
        filters = {
            'group': {'klass': Group, 'query_key': 'code'}
        }

        CustomViewSet.__init__(self, filters)
        ERPViewSet.__init__(self)

    @staticmethod
    def get_queryset():
        return Item.objects.all()

    def get_permissions(self):
        return [IsAuthenticated(), DefaultViewSetPermission()]

    def get_price(self, items, page):
        body = {
            'filter': {
                'referenceCodeList': items,
                'hasPrice': True,
                'branchPriceCodeList': [1],
                'priceCodeList': [10]
            },
            'option': {
                'prices': [
                    {
                        'branchCode': 1,
                        'priceCodeList': [10],
                        'isPromotionalPrice': True
                    }
                ]
            },
            'page': page,
            'pageSize': 50
        }
        try:
            response = requests.post(f'{self.erp_endpoint}prices/search/', data=json.dumps(body, cls=DjangoJSONEncoder),
                                     headers=self.erp_headers)
            if response.status_code == 200:
                return json.loads(response.content)
            else:
                print(response.status_code)
                raise requests.HTTPError()
        except requests.HTTPError:
            return None

    @staticmethod
    def append_digit(value):
        if re.search(r'^(([0-9]{2}\s){2})([0-9]{4})$', value):
            values = list(value)
            values[6] = f'00{values[6]}'
            value = "".join(values)
        return value

    def retrieve(self, request, pk):
        if bool(re.fullmatch(ITEM_REGEX, pk)):
            serializer = ItemSerializer(get_object_or_404(self.get_queryset(), **{'code': pk}))
            obj_copy = serializer.data

            if request.user.has_perm('item.get_item_api_price_field'):
                page = 1
                condition = True
                item_id = self.append_digit(obj_copy['id'])

                while condition:
                    data = self.get_price([item_id], 1)
                    if data:
                        df = pd.DataFrame(data=data['items'])

                        if not df.empty:
                            arr = df.loc[df.referenceCode == item_id, 'prices']
                            if not arr.empty:
                                arr = arr.iloc[0]
                                obj_copy['price'] = arr[0]['promotionalPrice'] if arr[0]['promotionalPrice'] else \
                                    arr[0]['price']
                                break

                            page += 1
                            condition = data['hasNext']

                    else:
                        break

            return Response(status=status.HTTP_200_OK, data=obj_copy)
        NotFound()

    def list(self, request):
        query_params = request.query_params.copy()
        queryset = self.get_queryset()

        if query_params:
            queryset = queryset.filter(**self.get_filter_object(query_params))
            serializer = ItemSerializer(queryset, many=True)

            if request.user.has_perm('item.get_item_api_price_field'):
                page = 1
                condition = True
                not_found = items = [self.append_digit(item['id']) for item in serializer.data]

                while condition:
                    data = self.get_price(items, page)
                    if data:
                        df = pd.DataFrame(data=data['items'])
                        if not df.empty:
                            for obj in serializer.data:
                                item_id = self.append_digit(obj['id'])
                                arr = df.loc[df.referenceCode == item_id, 'prices']
                                if not arr.empty and not obj['price']:
                                    arr = arr.iloc[0]
                                    not_found.pop(not_found.index(item_id))
                                    obj['price'] = arr[0]['promotionalPrice'] if arr[0]['promotionalPrice'] else arr[0][
                                        'price']

                        if not not_found:
                            break

                        page += 1
                        condition = data['hasNext']

                    else:
                        break

            return Response(status=status.HTTP_200_OK, data=serializer.data)

        raise ValidationError({'detail': 'Missing GROUP as query param.'})


class SkuViewSet(viewsets.ViewSet, CustomViewSet, ERPViewSet):
    def __init__(self, **kwargs):
        filters = {
            'item': {'klass': Item, 'query_key': 'code', 'suffix': '_id'}
        }

        CustomViewSet.__init__(self, filters)
        ERPViewSet.__init__(self)

    @staticmethod
    def get_queryset():
        return Sku.objects.filter(active=True)

    def get_permissions(self):
        return [IsAuthenticated(), DefaultViewSetPermission()]

    def get_inventory(self, skus, page):
        body = {
            "filter": {
                "change": {
                    "startDate": "2015-08-29T10:48:30.870490+00:00",
                    "endDate": dateformat.format(timezone.now(), 'c'),
                    "inStock": True,
                    "branchStockCodeList": [1],
                    "stockCodeList": [1]
                },
                "productCodeList": skus
            },
            "option": {
                "balances": [
                    {"branchCode": 1, "stockCodeList": [1], "isTransaction": True}
                ]
            },
            "expand": "locations",
            "pageSize": 10,
            "page": page
        }
        try:
            response = requests.post('https://www30.bhan.com.br:9443/api/totvsmoda/product/v2/balances/search',
                                     data=json.dumps(body, cls=DjangoJSONEncoder),
                                     headers=self.erp_headers)

            if response.status_code == 200:
                return json.loads(response.content)
            else:
                raise requests.HTTPError()
        except requests.HTTPError:
            return None

    def list(self, request):
        query_params = request.query_params.copy()
        queryset = self.get_queryset()

        if query_params:
            queryset = queryset.filter(**self.get_filter_object(query_params))

            paginator = SkuPagination()
            page = paginator.paginate_queryset(queryset, request)
            serializer = SkuSerializer(page, many=True)

            if request.user.has_perm('item.get_sku_api_availability_field'):
                page = 1
                condition = True
                skus = [int(d['id']) for d in serializer.data]

                while condition:
                    data = self.get_inventory(skus, page)
                    if not data:
                        break

                    for obj in data['items']:
                        for sku in serializer.data:
                            if int(sku['id']) == obj['productCode']:
                                sku.update({
                                    'available': obj['balances'][0]['stock'],
                                    'location': [location['locationCode'] for location in obj['locations']]
                                })
                                break
                    page += 1
                    condition = data['hasNext']

            return paginator.get_paginated_response(serializer.data)
        raise ValidationError({'detail': 'Missing ITEM as query param.'})

    def retrieve(self, request, pk):
        serializer = SkuSerializer(get_object_or_404(self.get_queryset(), **{'code': pk}), many=False)
        obj_copy = serializer.data

        if request.user.has_perm('item.get_sku_api_availability_field'):
            data = self.get_inventory([int(serializer.data['id'])], 1)

            for obj in data['items']:
                if int(serializer.data['id']) == obj['productCode']:
                    obj_copy = serializer.data
                    obj_copy['available'] = obj['balances'][0]['stock']
                    obj_copy['location'] = [location['locationCode'] for location in obj['locations']]
                    break
        return Response(status=status.HTTP_200_OK, data=obj_copy)


class CategoryViewSet(viewsets.ViewSet):
    @staticmethod
    def get_queryset():
        return Category.objects.all()

    def list(self, request):
        return Response(status=status.HTTP_200_OK, data=cache.get('categories', []))


class BrandViewSet(viewsets.ViewSet):
    @staticmethod
    def get_queryset():
        return Brand.objects.all().order_by('order')

    def list(self, request):
        serializer = BrandSerializer(self.get_queryset(), many=True)
        return Response(status=status.HTTP_200_OK, data=serializer.data)


class SeasonViewSet(viewsets.ViewSet):
    @staticmethod
    def get_queryset():
        return Season.objects.all()

    def list(self, request):
        serializer = SeasonSerializer(self.get_queryset(), many=True)
        return Response(status=status.HTTP_200_OK, data=serializer.data)


class BannerViewSet(viewsets.ViewSet):

    @staticmethod
    def serialize_banner(items):
        banner = []
        for item in items:
            obj = {
                'group': Group.objects.get(id=item['id']).code,
                'file': Photo.objects.get(id=item['photo']).file
            }
            banner.append(obj)
        return banner

    def list(self, request):
        daily_item = cache.get('dailyitem')
        print(daily_item)
        popular_items = {
            'name': 'os mais visitados',
            'groups': self.serialize_banner(cache.get('popularitems')[0:4])
        }

        return Response(BannerSerializer(popular_items, many=False).data)
