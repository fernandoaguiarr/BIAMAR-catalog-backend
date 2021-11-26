import requests

import json
import random

from django.core.cache import cache
from django.utils import timezone, dateformat
from django.core.serializers.json import DjangoJSONEncoder
from django.core.management import BaseCommand, CommandError

from item.models import Group
from image.models import Photo
from image.serializers import PhotoSerializer


class Command(BaseCommand):

    def __init__(self):
        super().__init__()
        self.token = cache.get('totvs')
        self.queryset = Group.objects.all()

    def get_item_availability(self, group, index=0):
        url = 'https://www30.bhan.com.br:9443/api/totvsmoda/product/v2/balances/search/'

        start_date = dateformat.format(
            (timezone.now()).replace(year=2015, month=1, day=1, hour=0, minute=0, second=0, microsecond=0), 'c')
        end_date = dateformat.format(timezone.now(), 'c')

        header = {'Authorization': self.token, 'Accept': 'aplication/json', 'Content-Type': 'application/json'}
        body = {
            "filter": {
                "change": {
                    "startDate": start_date,
                    "endDate": end_date,
                    "inProduct": True,
                    "inStock": True,
                    "branchStockCodeList": [1],
                    "stockCodeList": [1]
                },
                "groupCodeList": [group if len(group) > 4 else "00{}".format(group)]
            },
            "option": {"balances": [{"branchCode": 1, "stockCodeList": [1]}]},
            "page": 1
        }
        try:
            response = requests.post(url=url, headers=header, data=json.dumps(body, cls=DjangoJSONEncoder))
            if response.status_code != 200:
                raise requests.HTTPError(response.status_code)
            return json.loads(response.content)
        except requests.HTTPError as exception:
            raise CommandError(exception)

    def get_queryset(self):
        queryset = self.queryset.filter(
            group_has_photos__isnull=False,
            group_has_photos__export_to__isnull=False
        ).distinct()
        return random.choice(queryset)

    def handle(self, *args, **options):
        repeat_queryset_search = condition = True
        group = self.get_queryset()
        index = 1

        print(group)
        while repeat_queryset_search:
            total = 0
            condition = True
            while condition:
                data = self.get_item_availability(str(group.code), index)
                if data['items']:
                    for obj in data['items']:
                        total += obj['balances'][0]['stock']

                condition = data['hasNext']
                index += 1
            if total != 0:
                break

            group = self.get_queryset()
            serializer = PhotoSerializer(random.choice(Photo.objects.filter(group=group.id)), many=False)
        cache.set('dailyitem', {'group': group.code, 'photo': serializer.data})
