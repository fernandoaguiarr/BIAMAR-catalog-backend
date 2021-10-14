import json

import requests

from django.core.cache import cache
from django.core.mail import send_mail
from django.core.management import BaseCommand


class Command(BaseCommand):

    def __init__(self):
        super().__init__()

        # Set API parameters
        self.url = 'https://www30.bhan.com.br:9443/api/totvsmoda/authorization/v2/token'
        self.api_id = 'biamarws'
        self.api_password = '3656878445'
        self.username = 'api'
        self.password = '456'

    def add_arguments(self, parser):
        parser.add_argument('endpoint', type=str)

    def handle(self, *args, **options):
        value = cache.get(options['endpoint'], 'not found')
        if value != 'not found':
            return value

        body = {
            'grant_type': 'password',
            'client_id': self.api_id,
            'client_secret': self.api_password,
            'username': self.username,
            'password': self.password
        }
        try:
            response = requests.post(self.url, data=body)
            if response.status_code != 200:
                raise requests.HTTPError(response.status_code)
            else:
                content = json.loads(response.content)
                token = "{} {}".format(content['token_type'], content['access_token'])
                cache.set(options['endpoint'], token, timeout=82800)
        except requests.HTTPError as exception:
            send_mail(
                'ERROR - Totvs moda token',
                'Some error occurred when we are trying to get the authentication token. HTTP status code: {}'.format(
                    exception),
                recipient_list=['faguiar@biamar.com.br'],
                from_email='',
                fail_silently=False
            )
