# Create your views here.
import copy

from rest_framework import viewsets, permissions, status
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Item, Photo
from .serializers import PhotoSerializer, ItemSerializer


class PhotoModelPermission(permissions.DjangoModelPermissions):

    def __init__(self):
        self.perms_map = copy.deepcopy(self.perms_map)  # from EunChong's answer
        self.perms_map['GET'] = ['%(app_label)s.view_%(model_name)s']
        self.perms_map['POST'] = []
        self.perms_map['PUT'] = []
        self.perms_map['DELETE'] = []

        print(self.perms_map)


class PhotoViewSet(viewsets.ViewSet):

    def get_permissions(self):
        return [IsAuthenticated(), PhotoModelPermission()]

    def get_queryset(self):
        return Photo.objects.all()

    def list(self, request):
        queryset = Item.objects.all()
        query_params = request.query_params

        if query_params:
            query_filter = {el: {'id': int(query_params[el])} for el in list(query_params.keys())}
            if 'id' in query_filter:
                del query_filter['id']

            queryset = queryset.filter(**query_filter).values('id')
            items = []
            if 'id' in query_params:
                for item in queryset:
                    ref = item['id'].split(" ")[2]
                    if (query_params['id']) and (query_params['id'] in ref):
                        items.append(ref)

            else:
                for item in queryset:
                    ref = item['id'].split(" ")[2]
                    items.append(ref)

            queryset = self.get_queryset().filter(id__in=items).order_by('-id')
            if not queryset:
                return Response(status=status.HTTP_404_NOT_FOUND)

        else:
            queryset = self.get_queryset().order_by('-id')[:20]

        serializer = PhotoSerializer(queryset, many=True)
        return Response(data=serializer.data)

    def retrieve(self, request, pk=None):
        queryset = Photo.objects.all()
        serializer = PhotoSerializer(get_object_or_404(queryset, id=pk))
        return Response(status=status.HTTP_200_OK, data=serializer.data)

    def partial_update(self, request, pk=None):
        return Response()


class ItemViewSet(viewsets.ViewSet):
    def get_permissions(self):
        return [IsAuthenticated(), CustomDjangoModelPermission()]

    def get_queryset(self):
        return Item.objects.all()

    def retrieve(self, request, pk=None):
        queryset = self.get_queryset()
        queryset = queryset.filter(id__contains=pk)

        if not queryset:
            return Response(status=status.HTTP_404_NOT_FOUND)

        serializer = ItemSerializer(queryset, many=True)
        return Response(status=status.HTTP_200_OK, data=serializer.data)
