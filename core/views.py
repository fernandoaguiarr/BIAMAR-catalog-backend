import copy
import json
import requests

from django.core.exceptions import ObjectDoesNotExist
from rest_framework import viewsets, status, permissions
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from core.models import VirtualAgeToken
from django.utils import timezone
from core.serializers import VirtualAgeTokenSerializer


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

    # PhotoModelPermission require this method
    def get_queryset(self):
        return VirtualAgeToken.objects.all()

    def get_token(self):
        header = {'Usuario': 'biamarws', 'Senha': '147258', 'Content-Type': 'aplication/json'}
        response = requests.post('https://www30.bhan.com.br:9443/api/v1/autorizacao/token', headers=header)
        response = json.loads(response.content)
        return response['cdToken']

    def list(self, request):
        queryset = self.get_queryset()

        try:
            if not queryset.exists():
                raise ObjectDoesNotExist
            else:
                queryset = queryset.last()
                if queryset.date > timezone.now():
                    serializer = VirtualAgeTokenSerializer(queryset, many=False)
                    return Response(status=status.HTTP_200_OK, data=serializer.data)
                else:
                    raise ObjectDoesNotExist

        except ObjectDoesNotExist:
            token = VirtualAgeToken(id=self.get_token(), date=(timezone.now() + timezone.timedelta(days=1)))
            token.save()

            serializer = VirtualAgeTokenSerializer(token, many=False)
            return Response(status=status.HTTP_200_OK, data=serializer.data)
