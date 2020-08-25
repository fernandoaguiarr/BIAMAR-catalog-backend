import io
import json

import requests
from django.core.management import BaseCommand, call_command


class Command(BaseCommand):
    help = 'Return Virtual age token.'

    @staticmethod
    def deactivate(self, token, package_id):
        header = {
            'Authorization': 'Bearer {}'.format(token),
            'Content-Type': 'application/json',
        }

        response = requests.post("https://www30.bhan.com.br:9443/api/v1/pacote/envio", headers=header,
                                 data=json.dumps({'cdPacote': "{}".format(package_id)}))
        response = json.loads(response.content)

        return False if ('dsErro' in response) else True

    def add_arguments(self, parser):
        parser.add_argument('package_id',
                            type=str,
                            help='Set package id')

    def handle(self, *args, **options):
        token = io.StringIO()
        call_command('gettoken', stdout=token)

        return str(self.deactivate(self, token=token.getvalue().replace("\n", ""), package_id=options['package_id']))
