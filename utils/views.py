from django.core.cache import cache
from django.core.management import call_command

from rest_framework import viewsets, status
from rest_framework.response import Response


class ERPToken(viewsets.ViewSet):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.cache_key = 'ERP_token'
        self.token = cache.get(self.cache_key)

    def set_token(self):
        call_command('gettoken', 'ERP_token')
        self.token = cache.get('ERP_token')

    def list(self, request):
        if not self.token:
            self.set_token()

        return Response(status=status.HTTP_200_OK, data={'token': self.token})
