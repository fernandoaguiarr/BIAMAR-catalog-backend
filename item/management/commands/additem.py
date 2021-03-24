import io
import json
import requests
import pandas as pd
from django.core.exceptions import ValidationError, ObjectDoesNotExist

from django.core.management import BaseCommand, call_command, CommandError
from django.utils import timezone, dateformat
from django.utils.dateparse import parse_date
from django.db import IntegrityError
from requests import HTTPError

from item.models import Item, Color, Size, Season, Brand, TypeItem, Group, Sku


def get_products(start_date, end_date, page_index=0):
    """
    Request to the API products that has some changed fields in a period.
    :param start_date: date. The start date
    :param end_date: date. The limit date
    :param page_index: number;
    :return: Return a dict(response)
    """
    token = io.StringIO()
    call_command('gettoken', 'v2', stdout=token)

    token = token.getvalue().replace("\n", "")
    url = 'https://www30.bhan.com.br:9443/api/totvsmoda/product/v2/references/search'

    header = {
        'Authorization': token,
        'Accept': 'aplication/json',
        'Content-Type': 'application/json'
    }

    body = {
        'filter': {
            'change': {
                'startDate': start_date,
                'endDate': end_date,
                'inBranchInfo': True,
                'branchInfoCodeList': [1]
            },
            "classifications": [
                {
                    "type": 33,
                    "codeList": [
                        "1"
                    ]
                }
            ]
        },
        'option': {
            'branchInfoCode': 1
        },
        'expand': 'classifications,additionalFields',
        'page': page_index,
        'pageSize': 100
    }

    response = requests.post(url=url, headers=header, data=json.dumps(body))
    try:
        if response.status_code != 200:
            raise HTTPError(response.status_code)
        else:
            return json.loads(response.content)
    except HTTPError as error:
        raise CommandError("Something went wrong with the request. The request status: {}".format(error))


def dataframe_column_is_valid(df, column, pattern):
    """
    Run regex full match search in dataframe column.
    :param df: Pandas dataframe
    :param column: str. Dataframe column name that will be made regex search
    :param pattern: str. Regex expression. Eg.: r'[0-9]{2} [0-9]{2} (0{2}[0-9]{4})'
    :return: Dataframe with column regex match status
    """
    series = pd.Series(data=df[column].values, dtype='string').str.fullmatch(pattern)

    return pd.concat(
        [pd.Series(data=df[column].values, dtype='string'), series],
        ignore_index=True,
        axis=1
    )


def filter_dataframe(data, key, values):
    """
    Transform the dict into a dataframe and filter this dataframe in the column selected returning a dataframe of
    the values provided.
    :param data: dict. Data that will be transformed in df and filtered
    :param key: str. The Dataframe column name
    :param values: list. A list of values to be returned
    :return: Dataframe of the filtered values
    """
    df = pd.DataFrame(data=data)
    return df.loc[df[key].isin(values)]


def command_date_is_valid(start=None, end=None):
    """
    Parse the string to date instances. If the params was not provided set\n
    start date: current date - 1 day
    \nend date :to the current date
    :param start: str.The start date
    :param end: str. The limit date
    :return: Dict with these serialized dates
    """
    try:
        start = parse_date(start) if start else (timezone.now() - timezone.timedelta(days=1))
        end = parse_date(end) if end else timezone.now()
    except ValueError:
        raise CommandError("The given date is well formatted but not a valid date.")

    return {'start': dateformat.format(start, 'c'), 'end': dateformat.format(end, 'c')}


def insert_model(df, df_columns, klass, klass_fields=None, additional_fields=None, force_update=True):
    """
    Change the dataframe columns names to klass_fields and convert to the dict.
    After that iter the dict and insert it in the database
    :param klass: model class. Only the class reference not instance. Eg.: insert_model(klass=Group,...)
    :param klass_fields: list. A List of the model class fields
    :param additional_fields:Dict. A Dict with additional fields that will be inserted
     on the first insertion of the model object
    :param force_update: Boolean. Value to allow queryset update
    :param df: dataframe. Dataframe with the data that will be inserted in database
    :param df_columns: list. A List of dataframe columns
    """

    if additional_fields is None:
        additional_fields = {}
    if klass_fields is not None:
        df = df.rename(columns=dict(zip(df_columns, klass_fields)))

    for _ in df.to_dict(orient='records'):
        try:
            queryset = klass.objects.filter(**_)
            if not queryset.first():
                raise ObjectDoesNotExist
            elif force_update:
                queryset.update(**_)
        except ObjectDoesNotExist:
            # Creating model class instance and saving it to the database
            # {**_, **aditional_fields} -> joining values
            klass(**({**_, **additional_fields})).save()


class Command(BaseCommand):
    help = 'Request product data from API v2.x and insert in DB.'

    def __init__(self):
        super().__init__()

        self._pages = 1
        self._total_items = 0
        self._total_page_items = 0
        self._total_errored_items = 0
        self._total_page_treated_items = 0

        self._errored_items = None

    def add_arguments(self, parser):
        parser.add_argument(
            '--start',
            help='Set a start date to search products changes. If none is passed the start date is setted'
                 ' to the last day. The pattern date is Y-m-d. Eg.: 2020-09-29'
        )

        parser.add_argument(
            '--end',
            help='Set a end date to search products changes. If none is passed the end date is setted'
                 ' to the current date. The pattern date is Y-m-d. Eg.: 2020-09-29',
        )

    def handle(self, *args, **options):
        next_page = True
        classifications_list = [1, 112, 110, 111, 7]

        dates = command_date_is_valid(options['start'], options['end'])

        while next_page:
            response = get_products(start_date=dates['start'], end_date=dates['end'], page_index=self._pages)

            # If the response has been paginated
            next_page = response['hasNext']

            # Transform the response in DF and  after that make a regex search to exclude wrong items codes
            # from the dataframe
            df = pd.DataFrame(data=response['items'])
            validated_df = dataframe_column_is_valid(df, 'ReferenceCode',
                                                     r'[0-9]{2} [0-9]{2} 0{2}[0-9]{4}')
            validated_df = validated_df.loc[validated_df[1]]

            # Convert the dataframe to a dict to be able to iter
            items = df[df['ReferenceCode'].isin(validated_df[0])].to_dict(orient='records')
            # Every while loop reset values of _total_page_items, _total_page_treated_items and the insertion statistics
            self._total_page_items = len(items)
            self._total_page_treated_items = 0
            self.stdout.write("")

            for item in items:
                try:
                    # Filter all sku classifications from item and get only classifications with codes
                    # that are in classifications_list
                    classifications_df = filter_dataframe(
                        data=pd.json_normalize(item['colors'], ['products', ['classifications']]),
                        key='typeCode',
                        values=classifications_list
                    )

                    # Drop duplicates dataframe values because the SKUs classifications may be the same,
                    # this step is done to prevent double or more database insert tries
                    classifications_df = classifications_df.drop_duplicates()

                    sku_df = pd.json_normalize(item['colors'], ['products'], ['code'], meta_prefix='_')

                    # Filter classifications_df to get brand, group, season, type and genre in separately dataframes
                    # to make the database insertion more simple and easily
                    group_df = pd.DataFrame(filter_dataframe(classifications_df, 'typeCode', [112]))[['code']]
                    brand_df = pd.DataFrame(filter_dataframe(classifications_df, 'typeCode', [111]))[['code', 'name']]
                    season_df = pd.DataFrame(filter_dataframe(classifications_df, 'typeCode', [7]))[['code', 'name']]
                    type_df = pd.DataFrame(filter_dataframe(classifications_df, 'typeCode', [110]))[['code', 'name']]
                    genre_df = filter_dataframe(classifications_df, 'typeCode', [1])[['name']]

                    # Raise IndexError if some of the previous dataframe is empty. If this condicition is True
                    # go to the next item
                    if group_df.empty or brand_df.empty or season_df.empty or type_df.empty:
                        raise IndexError
                    else:
                        # Remove possible space characters in group_df value, after that run regex validation
                        group_df['code'] = group_df['code'].str.rstrip()
                        validated_group_df = dataframe_column_is_valid(group_df, 'code', r'0{2}[0-9]{4}')

                        # if the validations fails ValidationError and go to the next item,
                        # otherwise perfom the insertions
                        if validated_group_df.iloc[0][1]:
                            colors_df = pd.DataFrame(data=item['colors'], columns=['code', 'name'])
                            insert_model(klass=Color, klass_fields=['id', 'name'], df=colors_df,
                                         df_columns=colors_df.columns, force_update=False)

                            sizes_df = pd.DataFrame(data=item['grid'])
                            insert_model(klass=Size, klass_fields=['description'], df=sizes_df,
                                         df_columns=sizes_df.columns, force_update=False)

                            insert_model(klass=Season, klass_fields=['id', 'erp_name'],
                                         additional_fields={'name': season_df.iloc[0]['name']},
                                         df=season_df,
                                         df_columns=season_df.columns, force_update=False)
                            insert_model(klass=Brand, klass_fields=['id', 'erp_name'],
                                         additional_fields={'name': brand_df.iloc[0]['name']},
                                         df=brand_df,
                                         df_columns=brand_df.columns, force_update=False)
                            insert_model(klass=TypeItem, klass_fields=['id', 'erp_name'],
                                         additional_fields={'name': type_df.iloc[0]['name']},
                                         df=type_df,
                                         df_columns=type_df.columns,
                                         force_update=False)
                            insert_model(klass=Group, klass_fields=['id'], df=group_df, df_columns=group_df.columns)

                            # Create a item_dict with the model classes objects because django requires
                            # the foreign keys should be a model class instance.
                            item_dict = {
                                'id': item['ReferenceCode'],
                                'genre': genre_df.iloc[0]['name'] if not genre_df.empty else None,
                                'season': Season.objects.get(id=season_df.iloc[0]['code']),
                                'brand': Brand.objects.get(id=brand_df.iloc[0]['code']),
                                'type': TypeItem.objects.get(id=type_df.iloc[0]['code']),
                                'group': Group.objects.get(id=group_df.iloc[0]['code'])
                            }

                            # Transform item_dict in a dataframe and send it to the database insertion method
                            item_df = pd.DataFrame([item_dict])
                            insert_model(klass=Item, df=item_df, df_columns=item_df.columns)

                            # Create a dict with some columns of the original sku dataframe.
                            # Where _code column is color id
                            sku_dict = sku_df[['code', 'sku', 'isActive', 'size', '_code', 'additionalFields']].to_dict(
                                orient='records')

                            # The sku_dict may have more than one record, so iter the sku_dict and 'serialize'
                            # the columns to the correct values.
                            for sku in sku_dict:
                                sku['ReferenceCode'] = Item.objects.get(id=item['ReferenceCode'])
                                sku['_code'] = Color.objects.get(id=sku['_code'])
                                sku['size'] = Size.objects.get(description=sku['size'])

                                # Filter the sku['additionalFields'] values to get only the weight value
                                # The sku['additionalFields'] may have no values, so the weight, in this conditions,
                                # value will be None
                                weight = None
                                if sku['additionalFields']:
                                    weight = filter_dataframe(sku['additionalFields'], 'code', [3])
                                    weight = weight.iloc[0]['value'] if not weight.empty else None

                                sku['additionalFields'] = weight

                            # Transform the dict into a dataframe and send it to the database insertion method
                            sku_df = pd.DataFrame(sku_dict)
                            insert_model(
                                klass=Sku,
                                klass_fields=['id', 'ean', 'active', 'size', 'color', 'weight', 'item'],
                                df=sku_df,
                                df_columns=sku_df.columns
                            )
                        else:
                            raise ValidationError("Group isn't valid.")

                        # The database insertion runs well, this method has called to print the current insertion status
                        self._progress_status()
                        self._total_items += 1

                except IndexError:
                    # Increment _total_errored_items
                    self._total_errored_items += 1
                except ValidationError:
                    # Increment _total_errored_items
                    self._total_errored_items += 1

            self._pages += 1
        self._progress_status(last_page=True)

    def _progress_status(self, last_page=False):
        """
        Increment _total_page_treated_items every time this method is called and after that print the progress of
        database insertion.
        """
        if not last_page:
            self._total_page_treated_items += 1
            self.stdout.write("Page {}. Treated {}% of {} items.".format(self._pages, int(
                (self._total_page_treated_items * 100) / self._total_page_items), self._total_page_items), ending='\r')
        else:
            self.stdout.write("\n\n{}".format(self._total_items))
