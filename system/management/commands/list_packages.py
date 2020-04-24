import io
import json

import requests
from django.core.management import BaseCommand, call_command
from django.utils import timezone


class Command(BaseCommand):
    help = 'Look for available packages'

    def handle(self, *args, **options):
        token = io.StringIO()
        call_command('token', stdout=token)

        url = "https://www30.bhan.com.br:9443/api/v1/pacote/lista"
        header = {
            'Authorization': 'Bearer {}'.format(token.getvalue().replace("\n", "")),
            'Content-Type': 'application/json'
        }
        body = {
            "cdModPac": "3001",
            "cdDestino": "91037952000135",
            "dtInclusaoInicio": (timezone.now()).strftime("%d/%m/%Y"),
            "dtInclusaoFim": (timezone.now() + timezone.timedelta(days=1)).strftime("%d/%m/%Y")
        }

        response = requests.post(url=url, headers=header, data=json.dumps(body))
        return str(json.loads(response.content))
