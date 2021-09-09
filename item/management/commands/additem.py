import gc
import json
import re

import requests
import numpy as np
import pandas as pd

from django.conf import settings
from django.core.cache import cache
from django.core.mail import send_mail
from django.utils.dateparse import parse_date
from django.utils import timezone, dateformat
from django.template.loader import render_to_string
from django.core.exceptions import ObjectDoesNotExist
from django.core.serializers.json import DjangoJSONEncoder
from django.core.management import BaseCommand, CommandError

from item.models import Group, Item, Season, Category, Brand, Color, Size, Gender, Sku


def camel_case(value):
    return re.sub(r'\w+', lambda m: m.group(0).capitalize(), value)


def get_items(start_date, end_date, index=0):
    token = cache.get('totvs')
    url = 'https://www30.bhan.com.br:9443/api/totvsmoda/product/v2/references/search'
    header = {'Authorization': token, 'Accept': 'aplication/json', 'Content-Type': 'application/json'}
    body = {
        'filter': {
            'change': {'startDate': start_date, 'endDate': end_date, 'inBranchInfo': True, 'branchInfoCodeList': [1]},
            "classifications": [{"type": 33, "codeList": ["1"]}]
        },
        'option': {'branchInfoCode': 1},
        'expand': 'classifications,additionalFields',
        'page': index,
        'pageSize': 100
    }

    try:
        response = requests.post(url=url, headers=header, data=json.dumps(body, cls=DjangoJSONEncoder))
        if response.status_code != 200:
            raise requests.HTTPError(response.status_code)
        return json.loads(response.content)
    except requests.HTTPError as exception:
        raise CommandError(exception)


def find(arr, parent_key, parent_value, child_key):
    for value in arr:
        if value[parent_key] == parent_value:
            return value[child_key]

    return 'error'


def insert_group(group):
    Group.objects.update_or_create(code=group)
    return False


def insert_gender(erp_name: str):
    try:
        Gender.objects.get(ERP_name=erp_name)
    except ObjectDoesNotExist:
        Gender(ERP_name=erp_name, name=erp_name.capitalize()).save()

    return False


def insert_size(name):
    try:
        Size.objects.get(name=name)
    except ObjectDoesNotExist:
        Size(name=name).save()
    return False


def insert_brand(erp_id, erp_name: str):
    try:
        Brand.objects.get(ERP_id=erp_id)
    except ObjectDoesNotExist:
        Brand(ERP_id=erp_id, ERP_name=erp_name, name=erp_name.capitalize()).save()

    return False


def insert_season(erp_id, erp_name: str):
    try:
        Season.objects.get(ERP_id=erp_id)
    except ObjectDoesNotExist:
        Season(ERP_id=erp_id, ERP_name=erp_name, name=camel_case(erp_name)).save()

    return False


def insert_color(erp_id, erp_name: str):
    try:
        Color.objects.get(ERP_id=erp_id)
    except ObjectDoesNotExist:
        Color(ERP_id=erp_id, ERP_name=erp_name, name=erp_name).save()

    return False


def insert_category(erp_id, erp_name: str):
    try:
        Category.objects.get(ERP_id=erp_id)
    except ObjectDoesNotExist:
        Category(ERP_id=erp_id, ERP_name=erp_name, name=camel_case(erp_name)).save()
    return False


def insert_sku(code, active, item, color, size):
    try:
        Sku.objects.update_or_create(
            code=code,
            active=active,
            item=Item.objects.get(code=item),
            color=Color.objects.get(ERP_id=color),
            size=Size.objects.get(name=size)
        )
        return False
    except ObjectDoesNotExist:
        return True


def insert_item(code, group, category, brand, season, gender):
    try:
        Item.objects.update_or_create(
            code=code,
            group=Group.objects.get(code=group),
            category=Category.objects.get(ERP_id=int(category)),
            brand=Brand.objects.get(ERP_id=brand),
            season=Season.objects.get(ERP_id=season),
            gender=Gender.objects.get(ERP_name=gender)
        )
        return False
    except ObjectDoesNotExist:
        return True


class Command(BaseCommand):

    def __init__(self):
        super().__init__()
        self.errors = {'specs': [], 'items': [], 'skus': []}

        self.group_regex = r'[0-9]{4,}$'
        self.item_regex = r'(([0-9]{2}\s){2})([0-9]{4,})'

        self.emails = ['faguiar@biamar.com.br']
        self.allow_send_email = False

        self.dates = [timezone.now() - timezone.timedelta(1), timezone.now()]

    def add_arguments(self, parser):
        parser.add_argument('--startdate')
        parser.add_argument('--enddate')

    def handle(self, *args, **options):
        self.date_is_valid([options['startdate'], options['enddate']])
        print(self.dates)
        condition = True
        index = 1

        while condition:
            print(index)
            data = get_items(self.dates[0], self.dates[1], index)
            df = pd.json_normalize(data['items'], ['colors', 'products', ['classifications']])
            df = df.loc[df.typeCode.isin([1, 7, 110, 111, 112]), ['typeCode', 'code', 'name']]

            # Get first occurrence of all items' specifications. Specifications may be duplicated
            df = df.groupby(by=['typeCode', 'code'], as_index=False).first()

            # Prepare group values to insert into database
            df.loc[df.typeCode == 112, ['code']] = df.code.str.replace(r'^00', '', regex=True)
            df.loc[(df.typeCode == 112) & ~(df.code.str.contains(self.group_regex, regex=True)), 'error'] = True
            sentence = (df.typeCode == 112) & (df.error.isnull())
            df.loc[sentence, 'error'] = np.vectorize(insert_group, otypes=[bool])(df.loc[sentence, 'code'])

            # Prepare brand' values to insert into database
            sentence = (df.typeCode == 111)
            df.loc[sentence, 'error'] = np.vectorize(insert_brand)(
                df.loc[sentence, 'code'],
                df.loc[sentence, 'name']
            )

            # Prepare categories' values to insert into database
            sentence = (df.typeCode == 110)
            df.loc[sentence, 'error'] = np.vectorize(insert_category, otypes=[bool])(
                df.loc[sentence, 'code'],
                df.loc[sentence, 'name'],
            )

            # Prepare seasons' values to insert into database
            sentence = (df.typeCode == 7)
            df.loc[sentence, 'error'] = np.vectorize(insert_season, otypes=[bool])(
                df.loc[sentence, 'code'],
                df.loc[sentence, 'name'],
            )

            # Prepare genders' values to insert into database
            sentence = (df.typeCode == 1)
            df.loc[sentence, 'error'] = np.vectorize(insert_gender, otypes=[bool])(df.loc[sentence, 'name'])
            self.errors['specs'] = [*self.errors['specs'], *df.loc[df.error, ['typeCode', 'code']].to_dict('records')]

            # Prepare sizes' values to insert into database
            sizes = pd.json_normalize(data['items'], 'grid')
            sizes = sizes.groupby(by=[0], as_index=False).first()
            sizes.loc[:, 'error'] = np.vectorize(insert_size, otypes=[str])(sizes[0])

            # free memory
            del sentence, sizes, df
            gc.collect()

            meta = ['ReferenceCode', ['colors', 'code'], ['colors', 'name']]
            columns = ['ReferenceCode', 'code', 'isActive', 'colors.code', 'colors.name', 'size', 'specs']
            df = pd.json_normalize(data['items'], ['colors', ['products']], meta)
            df = df.rename(columns={'classifications': 'specs'})
            df = df.loc[:, columns]
            df.loc[:, 'ReferenceCode'] = df.ReferenceCode.str.replace(r' 00', ' ', regex=True)

            # Prepare colors' values to insert into database
            colors = df.loc[:, ['colors.code', 'colors.name']]
            colors = colors.groupby(by=['colors.code'], as_index=False).first()
            colors.loc[:, 'error'] = np.vectorize(insert_color, otypes=[bool])(
                colors['colors.code'],
                colors['colors.name']
            )

            # Prepare items' values to insert into database
            items = df.groupby(by=['ReferenceCode'], as_index=False).first()
            items.loc[:, 'group'] = items.ReferenceCode.str.replace(r'[0-9]{2} ', '', regex=True)
            items.loc[~(items.group.str.contains(self.group_regex, regex=True)), 'group'] = 'error'
            items.loc[:, 'gender'] = np.vectorize(find, otypes=[str])(items['specs'], 'typeCode', 1, 'name')
            items.loc[:, 'season'] = np.vectorize(find, otypes=[str])(items['specs'], 'typeCode', 7, 'code')
            items.loc[:, 'brand'] = np.vectorize(find, otypes=[str])(items['specs'], 'typeCode', 111, 'code')
            items.loc[:, 'category'] = np.vectorize(find, otypes=[str])(items['specs'], 'typeCode', 110, 'code')
            items.loc[:, 'error'] = False
            items.loc[~items.ReferenceCode.str.contains(self.item_regex), 'error'] = True
            sentence = (
                    ~items.group.str.contains('error') &
                    ~items.brand.str.contains('error') &
                    ~items.season.str.contains('error') &
                    ~items.gender.str.contains('error') &
                    ~items.category.str.contains('error') &
                    ~items.error
            )

            valid = items.loc[sentence, ['group', 'brand', 'category', 'season', 'gender', 'ReferenceCode']]
            items.loc[sentence, 'error'] = np.vectorize(insert_item, otypes=[bool])(
                valid.ReferenceCode,
                valid.group,
                valid.category,
                valid.brand,
                valid.season,
                valid.gender
            )
            items.loc[~sentence, 'error'] = True

            # Prepare  Skus' values to insert into database
            columns = ['code', 'isActive', 'ReferenceCode', 'colors.code', 'size']
            skus = df.loc[df.ReferenceCode.isin(items.ReferenceCode), columns]
            skus.loc[:, 'error'] = np.vectorize(insert_sku, otypes=[bool])(
                skus.code,
                skus.isActive,
                skus.ReferenceCode,
                skus['colors.code'],
                skus['size']
            )

            # Append inserting errors
            columns = ['id', 'categoria', 'marca', 'ref. último nível', 'coleção', 'gênero']
            errors = items.loc[
                items.error,
                ['ReferenceCode', 'category', 'brand', 'group', 'season', 'gender']
            ]
            errors = errors.rename(columns=dict(zip(errors.columns, columns)))
            self.errors['items'] = [*self.errors['items'], *errors.to_dict('records')]

            del columns, meta, sentence, df, colors, items, skus
            condition = data['hasNext']
            index += 1

        self.prepare_errors()
        if self.allow_send_email:
            self.send_email()

    def prepare_errors(self):
        for key, arr in self.errors.items():
            if arr:
                self.allow_send_email = True
                break

        self.errors = [
            {'display_name': 'classificações', 'description': None, 'values': self.errors['specs']},
            {'display_name': 'referências', 'description': None, 'values': self.errors['items']},
        ]

    def send_email(self):
        html = render_to_string('item/database_sync_error.html',
                                {'default_error_text': 'Classificação não encontrada', 'items': self.errors}
                                )
        send_mail('Incoerências ao importar produtos', from_email=settings.DEFAULT_FROM_EMAIL, message='',
                  recipient_list=self.emails,
                  fail_silently=False,
                  html_message=html
                  )

    def date_is_valid(self, dates):
        try:
            for index, date in enumerate(dates):
                if date:
                    date = date.replace("/", "-")
                    date = parse_date(date)
                    self.dates[index] = date
                else:
                    self.dates[index] = self.dates[index].replace(hour=0, minute=0, second=0, microsecond=0)
                self.dates[index] = dateformat.format(self.dates[index], 'c')
        except ValueError:
            raise CommandError("input is well formatted but not a valid date.")
