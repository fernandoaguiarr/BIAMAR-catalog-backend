import json
import requests

from django.core.management import BaseCommand
from django.utils import timezone
from ...models import VirtualAgeToken as Token


class Command(BaseCommand):
    help = 'Return Virtual age token.'

    @staticmethod
    def get_token():
        header = {'Usuario': 'biamarws', 'Senha': '147258', 'Content-Type': 'aplication/json'}
        response = requests.post('https://www30.bhan.com.br:9443/api/v1/autorizacao/token', headers=header)
        response = json.loads(response.content)
        return response['cdToken']

    def handle(self, *args, **options):
        token = Token.objects.last()
        if token and token.date > timezone.now():
            return token.code
        else:
            t = Token(code=self.get_token(), date=timezone.now() + timezone.timedelta(days=1))
            t.save()
            return t.code
