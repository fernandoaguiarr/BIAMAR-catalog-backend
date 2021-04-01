# standard library
import io
import json
import re

# third-party

import pandas as pd
import numpy as np
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

# Django
from django.db.models import Q, F
from django.core.management import call_command
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


# ECOMMERCE VIEWSETS

def vec_add_group_column(value, expr):
    return re.search(expr, value).group()


def vec_group_was_exported(color_column, group_column):
    try:
        ExportSku.objects.get(color=color_column, group=group_column)
        return True
    except ObjectDoesNotExist:
        return False


def vec_add_photos_column(color_column, group_column, sku_column):
    photos = Photo.objects.filter(color=color_column, group=group_column, export_ecommerce=True)
    if photos:
        try:
            ExportSku.objects.get(color=color_column, group=group_column)
        except ObjectDoesNotExist:
            pass
        ExportSku(
            base_sku=Sku.objects.get(id=sku_column),
            color=Color.objects.get(id=color_column),
            group=Group.objects.get(id=group_column)
        ).save()
        return json.dumps(PhotoSerializer(photos, many=True).data)
    else:
        return "None"


def required_params(obj, keys):
    for key in obj:
        if key not in keys:
            raise RequiredParam(message="This param is required: {}".format(key))


class ExportPhotosViewSet(viewsets.ViewSet):
    def get_permissions(self):
        return [IsAuthenticated(), ExportPhotosViewSetPermission()]

    def get_queryset(self):
        return Sku.objects.all()

    @staticmethod
    def process_df(df):
        df.loc[:, 'group'] = np.vectorize(vec_add_group_column)(df['item'], r'([0-9]{6}$)')
        df.loc[:, 'base_sku'] = np.nan

        first_occur_df = df.drop_duplicates(subset=['color', 'group'], keep="first",
                                            inplace=False).copy()
        first_occur_df.loc[:, 'group_was_exported'] = np.vectorize(vec_group_was_exported)(
            first_occur_df['color'],
            first_occur_df['group']
        )

        already_exported_df = first_occur_df.loc[first_occur_df['group_was_exported'] == True, :]

        for item in already_exported_df.to_dict(orient="records"):
            df.loc[
                (df.group == item['group']) &
                (df.color == item['color']),
                'base_sku'
            ] = item['id']

        first_export_df = first_occur_df.loc[first_occur_df['group_was_exported'] == False].copy()
        first_export_df.loc[:, 'photos'] = np.vectorize(vec_add_photos_column)(
            first_export_df['color'],
            first_export_df['group'],
            first_export_df['id']
        )

        first_export_sucess_df = first_export_df.loc[~first_export_df['photos'].str.contains('None')]

        for item in first_export_sucess_df.to_dict(orient="records"):
            df.loc[
                (df.group == item['group']) &
                (df.color == item['color']),
                'base_sku'
            ] = item['id']

        add_sku_photos = first_export_sucess_df[['id', 'photos']].to_json(orient="records")
        copy_sku_photos = df[
            ~df['base_sku'].isna() &
            ~df['id'].isin(first_export_sucess_df.id)
            ].to_json(orient="records")

        error_sku_photos = df[df.isnull().any(axis=1)].to_json(orient="records")

        return {
            'add': json.loads(add_sku_photos),
            'copy': json.loads(copy_sku_photos),
            'error': json.loads(error_sku_photos)
        }

    @action(detail=False, methods=['post'], url_path="raw-data")
    def process_raw_data(self, request):
        required = ['skus']
        params = request.data.copy()
        try:
            if params:
                required_params(params, required)
                queryset = self.get_queryset().filter(pk__in=params['skus']).values('id', 'item', 'color')
                response = self.process_df(pd.DataFrame(data=queryset))

                return Response(status=200, data=response)
            else:
                raise RequiredParam("These params are required:{}".format(",".join(required)))

        except RequiredParam as exception:
            return Response(status=status.HTTP_400_BAD_REQUEST, data=exception.message)
