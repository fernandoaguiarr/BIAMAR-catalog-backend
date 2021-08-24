# standard library
import json

# third-party
import numpy as np
import pandas as pd

# django
from django.core.cache import cache
from django.core.management import BaseCommand
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned

# local Django
from vtex.models import ExportSku
from item.serializers import PhotoSerializer
from item.models import Sku, Color, Group, Photo
from vtex.exceptions import UnsupportedDataType


def get_base_sku(group, color):
    try:
        return ExportSku.objects.get(group=group, color=color).base_sku.id
    except ObjectDoesNotExist:
        return np.NAN


def get_photos(group, color):
    return PhotoSerializer(Photo.objects.filter(group=group, color=color, export_ecommerce=True), many=True).data


def set_base_sku(sku, group, color):
    try:
        ExportSku.objects.get(base_sku=sku, group=group, color=color)
        return sku
    except MultipleObjectsReturned:
        return np.NAN
    except ObjectDoesNotExist:
        ExportSku(
            base_sku=Sku.objects.get(id=sku),
            group=Group.objects.get(id=group),
            color=Color.objects.get(id=color)
        ).save()
        return sku


class Command(BaseCommand):

    def __init__(self):
        self.supportedTypes = (InMemoryUploadedFile, list)
        self.supportedFileType = 'csv'
        self.fileHeader = 'sku'
        self.dataframe = None

        super().__init__()

    def add_arguments(self, parser):
        parser.add_argument('cache_id', help='provide later some description.')

    def handle(self, *args, **options):
        value = cache.get(options['cache_id'])
        try:
            expr = isinstance(value, self.supportedTypes)
            if expr:
                self.dataframe = pd.DataFrame(value) if isinstance(value, list) else pd.read_csv(value, sep=";")
                if self.fileHeader in self.dataframe.columns.to_list():
                    raise UnsupportedDataType(message="Required header (${}) not found.".format(self.fileHeader))

                queryset = Sku.objects.filter(pk__in=self.dataframe['id'].to_list()).values('id', 'item', 'color')

                for item in queryset:
                    self.dataframe.loc[(self.dataframe.id.astype(str) == item['id']), 'color'] = item['color']
                    self.dataframe.loc[self.dataframe.id.astype(str) == item['id'], 'item'] = item['item']

                return self.handle_dataframe()
            else:
                raise UnsupportedDataType(message="Data provided doesn't match with supported types.")

        except UnsupportedDataType as exception:
            return exception.message

    def handle_dataframe(self):
        self.dataframe.loc[:, 'photos'] = np.nan
        self.dataframe.loc[:, 'group'] = self.dataframe.item.str.replace(r"[0-9]{2} [0-9]{2} ", "", regex=True)
        self.dataframe.loc[:, 'base_sku'] = np.vectorize(get_base_sku, otypes=[float])(
            self.dataframe['group'],
            self.dataframe['color']
        )

        not_exported_df = self.dataframe.loc[
            self.dataframe.base_sku.isnull() |
            (self.dataframe.forceUpdate & self.dataframe.id.astype(np.float64).isin(self.dataframe.base_sku))
            ].groupby(by=['color', 'group'],
                      as_index=False).first()

        self.dataframe.loc[self.dataframe.id.isin(not_exported_df.id), 'base_sku'] = np.vectorize(set_base_sku,
                                                                                                  otypes=[float])(
            not_exported_df['id'],
            not_exported_df['group'],
            not_exported_df['color'],
        )

        self.dataframe.loc[
            self.dataframe.id.isin(not_exported_df.id), 'photos'] = np.vectorize(get_photos,
                                                                                 otypes=[list])(
            not_exported_df['group'],
            not_exported_df['color']
        )

        add_df = self.dataframe.loc[~self.dataframe.photos.isnull()]

        for item in add_df.loc[:, ['id', 'group', 'color']].to_dict('records'):
            self.dataframe.loc[
                (self.dataframe.group == item['group']) & (self.dataframe.color == item['color']),
                'base_sku'] = item['id']

        copy_df = self.dataframe.loc[
            self.dataframe.photos.isnull() &
            ~self.dataframe.id.astype(np.float64).isin(self.dataframe.base_sku)
            ]

        return json.dumps({
            'add': add_df.loc[:, ['id', 'photos']].to_dict(orient='records'),
            'copy': copy_df.loc[:, ['id', 'base_sku']].to_dict(orient='records'),
            'error': self.dataframe.loc[self.dataframe.base_sku.isnull(), ['id']].to_dict(orient='records')
        })
