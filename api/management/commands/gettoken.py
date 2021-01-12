import json
import requests

from django.core.exceptions import ObjectDoesNotExist
from django.core.management import BaseCommand
from django.utils import timezone

from ...models import VirtualAgeToken as Token


class Command(BaseCommand):
    """
    This Command deals with Totovs Moda TOKEN API
    Attributes:
    ``help``
        A short description of the command, which will be printed in
        help messages.
    ``api``
        A number; Required argument that select the API version, this argument is required because different API
        versions doesn't allow use same tokens.
    """

    help = 'Store token from the selected API version. Return the stored token.'

    def __init__(self):
        super().__init__()
        self._versions = {
            'v1': {
                'username': 'biamarws',
                'password': '147258',
                'url': 'https://www30.bhan.com.br:9443/api/v1/autorizacao/token'
            },
            'v2': {
                'username': 'biamarws',
                'password': '3656878445',
                'url': 'https://www30.bhan.com.br:9443/api/totvsmoda/authorization/v2/token'
            }
        }

    def add_arguments(self, parser):
        parser.add_argument('api_version', type=str, help='Set API version')

    def handle(self, *args, **options):
        try:
            token = Token.objects.get(date__gte=timezone.now(), version=options['api_version'])
            return token.code

        except ObjectDoesNotExist:
            token = self.get_token(version=options['api_version'])
            if token:
                Token(code=token['code'], date=token['expiration_date'], version=options['api_version']).save()
                return (Token.objects.last()).code
            else:
                return "API version doesn't match"

    def get_token(self, version):
        """
        Request token based on selected API version.
        :param version:  API version. Eg.: v1, v2
        :return: Return a dict with token and expiration date if version exists
        otherwise return None
        """
        try:
            api = self._versions[version]
            if version == 'v1':
                header = {
                    'Usuario': api['username'],
                    'Senha': api['password'],
                    'Content-Type': 'aplication/json'
                }

                response = json.loads((requests.post(api['url'], headers=header)).content)
                return {
                    'code': "Bearer {0}".format(response['cdToken']),
                    'expiration_date': timezone.now() + timezone.timedelta(days=1, minutes=-5)
                }

            elif version == 'v2':
                body = {
                    'grant_type': 'password',
                    'client_id': api['username'],
                    'client_secret': api['password'],
                    'username': 'api',
                    'password': 'api852'

                }

                response = json.loads((requests.post(api['url'], data=body)).content)
                return {
                    'code': "{0} {1}".format(response['token_type'], response['access_token']),
                    'expiration_date': timezone.now() + timezone.timedelta(seconds=response['expires_in'])
                }

        except KeyError:
            return None
