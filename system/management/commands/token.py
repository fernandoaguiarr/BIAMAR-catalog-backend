import requests
import json

from django.core.management import BaseCommand
from django.utils import timezone

from ...models import Token


class Command(BaseCommand):
    help = 'Check if token exist, if false request a new token'

    @staticmethod
    def get_token():
        header = {'Usuario': 'biamarws', 'Senha': '147258', 'Content-Type': 'aplication/json'}
        response = requests.post('https://www30.bhan.com.br:9443/api/v1/autorizacao/token', headers=header)
        response = json.loads(response.content)
        return response['cdToken']

    def handle(self, *args, **options):

        token = Token.objects.last()
        if token and token.date > timezone.now():
            return token.token
        else:
            t = Token(token=self.get_token(), date=timezone.now() + timezone.timedelta(days=1))
            t.save()
            return t.token
