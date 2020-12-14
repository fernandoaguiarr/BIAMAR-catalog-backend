# standard library
import copy
import io

# third-party
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets, permissions

# Django
from django.core.management import call_command

# local Django
from api.models import VirtualAgeToken


class CustomDjangoModelPermission(permissions.DjangoModelPermissions):

    def __init__(self):
        self.perms_map = copy.deepcopy(self.perms_map)  # you need deepcopy when you inherit a dictionary type
        self.perms_map['GET'] = ['%(app_label)s.view_%(model_name)s']
        self.perms_map['POST'] = []
        self.perms_map['PUT'] = []
        self.perms_map['PATCH'] = []
        self.perms_map['DELETE'] = []


class VirtualAgeTokenViewSet(viewsets.ViewSet):

    def get_permissions(self):
        return [IsAuthenticated(), CustomDjangoModelPermission()]

    # CustomDjangoModelPermission require this method
    def get_queryset(self):
        return VirtualAgeToken.objects.all()

    def list(self, request):
        token = io.StringIO()
        call_command('gettoken', 'v2', stdout=token)
        token = token.getvalue().replace("\n", "")
        return Response(data={'code': token})
