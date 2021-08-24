# standard library
import io
import json
import re

# third-party
import uuid

import pandas as pd
import numpy as np
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

# Django
from django.db.models import Q, F
from django.core.cache import cache
from django.core.management import call_command, CommandError
from django.core.exceptions import ObjectDoesNotExist

# local Django
from api.exceptions import RequiredParam, UnsupportedFileType
from api.models import VirtualAgeToken
from api.permissions import (
    GroupViewSetPermission, PhotoViewSetPermission, DefaultViewSetPermission, ExportPhotosViewSetPermission
)
from api.serializers import VirtualAgeSerializer
from item.models import (
    Photo, Item, Brand, Season, TypeItem, Group, Sku, Color
)
from item.serializers import (
    PhotoSerializer, ItemSerializer, SkuSerializer, ItemPropertiesSerializer
)

from vtex.models import ExportSku


# ITEM APP VIEWSETS
def group_is_valid(value, expr):
    regex = re.compile(expr)

    if bool(regex.fullmatch(value)):
        return True
    else:
        return False


def str_to_boolean(value):
    if value.lower() == 'true':
        return True
    elif value.lower() == 'false':
        return False
    else:
        return None


def retrieve_param_value(obj, key):
    try:
        return str_to_boolean(obj[key])
    except KeyError:
        return None


def serialize_params(params, fields):
    serialized = {}

    for param in params:
        try:
            key = next(filter(lambda k: param in k, fields))
            serialized = {**serialized, **{key: params[param]}}
        except StopIteration:
            pass

    return serialized


def file_is_valid(value, extensions):
    ext = value.split(".")[-1]
    if ext not in extensions:
        raise UnsupportedFileType(message="These file types are supported: {}; Your file type: {}".format(
            ",".join(extensions),
            ext
        ))


class GroupViewSet(viewsets.ViewSet):

    def get_permissions(self):
        return [IsAuthenticated(), GroupViewSetPermission()]

    def get_queryset(self, value=None):
        if value:
            return Group.objects.all()
        else:
            return Photo.objects.all()

    def list(self, request):

        def __group_by__(data):
            res = {}
            for obj in data:
                res.setdefault(obj['group'], []).append(
                    {'preview': obj['preview'], 'path': obj['path'],
                     'type': obj['photo_type'] if 'photo_type' in obj else 'type'})

            grouped_data = []
            for key in res.keys():
                paths = res[key]
                if paths[0]['preview'] is None and paths[0]['path'] is None:
                    paths.pop(0)

                grouped_data.append({'id': key, 'photos': paths})

            return grouped_data

        query_params = request.query_params.copy()

        filters = {}
        include = retrieve_param_value(query_params, 'include')

        if include:
            del query_params['include']

            field_list = ['id__icontains', 'item_group__brand', 'item_group__season', 'item_group__type']
            filters = serialize_params(query_params, field_list)

            queryset = self.get_queryset(include)
            queryset = queryset.filter(**filters).annotate(
                group=F('id'),
                path=F('photo_group__path'),
                preview=F('photo_group__preview'),
                photo_type=F('photo_group__type')
            ).values('group', 'path', 'preview', 'photo_type')

            return Response(status=status.HTTP_200_OK, data=__group_by__(queryset))

        else:
            field_list = [
                'group__icontains', 'group__item_group__type', 'group__item_group__brand',
                'group__item_group__season'
            ]
            filters = serialize_params(query_params, field_list)

            queryset = self.get_queryset(include)
            q = Q(type=1) | Q(type=2)

            queryset = queryset.exclude(q).filter(**filters)

            return Response(status=status.HTTP_200_OK, data=__group_by__(
                queryset.values('group', 'path', 'preview', 'order', 'export_ecommerce', 'color', 'type')))


class PhotoViewSet(viewsets.ViewSet):

    def get_permissions(self):
        return [IsAuthenticated(), PhotoViewSetPermission()]

    def get_queryset(self):
        return Photo.objects.all()

    def list(self, request):
        query_params = request.query_params.copy()
        field_list = ['group__id__icontains', 'type', 'color', 'preview', 'include']
        filters = serialize_params(query_params, field_list)
        queryset = self.get_queryset()

        include = retrieve_param_value(query_params, 'include')
        if include:
            del filters['include']

        if not include:
            q1 = Q(type=1) | Q(type=2)
            queryset = queryset.exclude(q1)

        queryset = queryset.filter(**filters)
        serializer = PhotoSerializer(queryset, many=True)
        return Response(status=status.HTTP_200_OK, data=serializer.data)


class ItemViewSet(viewsets.ViewSet):
    def get_permissions(self):
        return [IsAuthenticated(), DefaultViewSetPermission()]

    def get_queryset(self):
        return Item.objects.all()

    def retrieve(self, request, pk=None):
        queryset = self.get_queryset()

        try:
            if not group_is_valid(pk, "^([0-9]{2} [0-9]{2} 0{2}[0-9]{4})"):
                raise ObjectDoesNotExist

            queryset = queryset.get(id=pk)
            serializer = ItemSerializer(queryset, many=True)
            return Response(status=status.HTTP_200_OK, data=serializer.data)
        except ObjectDoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    def list(self, request):

        def __remove_not_allowed_params__(params, keys):
            for key in keys:
                if key in params:
                    del params[key]

            return params

        query_params = __remove_not_allowed_params__(request.query_params.copy(), ['item'])
        field_list = ['group', 'brand', 'season', 'type']
        filters = serialize_params(query_params, field_list)

        queryset = self.get_queryset()
        queryset = queryset.filter(**filters)
        serializer = ItemSerializer(queryset, many=True)

        return Response(status=status.HTTP_200_OK, data=serializer.data)


class SkuViewSet(viewsets.ViewSet):
    def get_permissions(self):
        return [IsAuthenticated(), DefaultViewSetPermission()]

    def get_queryset(self):
        return Sku.objects.all()

    def retrieve(self, request, pk=None):
        queryset = self.get_queryset()

        try:
            queryset = queryset.get(id=pk)
            serializer = SkuSerializer(queryset, many=False)
            return Response(status=status.HTTP_200_OK, data=serializer.data)
        except ObjectDoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    def list(self, request):
        query_params = request.query_params.copy()
        field_list = ['color', 'item', 'item__group']
        filters = serialize_params(query_params, field_list)

        queryset = self.get_queryset()
        queryset = queryset.filter(**filters)
        serializer = SkuSerializer(queryset, many=True)

        return Response(status=status.HTTP_200_OK, data=serializer.data)


class BrandViewSet(viewsets.ReadOnlyModelViewSet):
    def get_permissions(self):
        return [IsAuthenticated(), DefaultViewSetPermission()]

    queryset = Brand.objects.all()
    serializer_class = ItemPropertiesSerializer


class SeasonViewSet(viewsets.ReadOnlyModelViewSet):
    def get_permissions(self):
        return [IsAuthenticated(), DefaultViewSetPermission()]

    queryset = Season.objects.all()
    serializer_class = ItemPropertiesSerializer


class ItemTypeViewSet(viewsets.ReadOnlyModelViewSet):
    def get_permissions(self):
        return [IsAuthenticated(), DefaultViewSetPermission()]

    queryset = TypeItem.objects.all()
    serializer_class = ItemPropertiesSerializer


# API APP VIEWSETS
class VirtualAgeViewSet(viewsets.ViewSet):
    def get_permissions(self):
        return [IsAuthenticated(), DefaultViewSetPermission()]

    def get_queryset(self):
        return VirtualAgeToken.objects.all()

    def list(self, request):
        token = io.StringIO()
        call_command('gettoken', 'v2', stdout=token)
        seriazlier = VirtualAgeSerializer({'code': token.getvalue().replace("\n", "")}, many=False)

        return Response(status=status.HTTP_200_OK, data=seriazlier.data)


class ExportPhotosViewSet(viewsets.ViewSet):
    def get_permissions(self):
        return [
            IsAuthenticated(), ExportPhotosViewSetPermission()
        ]

    def get_queryset(self):
        return Sku.objects.all()

    @action(detail=False, methods=['POST'], url_path='vtex')
    def vtex(self, request):

        allowed_params = ['value']
        params = request.data.copy()

        try:
            for param in params:
                if param not in allowed_params:
                    raise RequiredParam(message="This param isn't allowed: {}".format(param),
                                        status=status.HTTP_400_BAD_REQUEST
                                        )

            cache_id = uuid.uuid4()  # Set a random cache ID
            cache.set(cache_id, params['value'])  # Save data on a temporary cache

            command_stoud = io.StringIO()  # Initialize StringIO class to be possible to get command stdout
            call_command('export_photos', cache_id, stdout=command_stoud)
            data = json.loads(command_stoud.getvalue())

            if isinstance(data, dict):
                return Response(status=status.HTTP_200_OK, data=data)

            return Response(status=status.HTTP_400_BAD_REQUEST, data=data)

        except RequiredParam as exception:
            return Response(data=exception.message, status=exception.status)
