from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.exceptions import NotFound

from django.core.exceptions import ObjectDoesNotExist

from item.models import Group, Color
from image.models import Photo, Category
from image.serializers import PhotoSerializer


# Create your views here.
class PhotoViewSet(viewsets.ViewSet):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.filters = {
            'group': {'klass': Group, 'query_key': 'code'},
            'color': {'klass': Color, 'query_key': 'ERP_id'},
            'category': {'klass': Category, 'query_key': 'id'},
        }

    @staticmethod
    def get_queryset():
        return Photo.objects.all()

    def get_filter_object(self, query_params: dict):
        queryset_filter = {}
        for obj in query_params.items():
            if obj[0] in self.filters:
                try:
                    query = {self.filters[obj[0]]['query_key']: obj[1]}
                    queryset_filter[obj[0]] = self.filters[obj[0]]['klass'].objects.get(**query)
                except ObjectDoesNotExist:
                    raise NotFound()
        return queryset_filter

    def list(self, request, *args, **kwargs):
        query_params = request.query_params.copy()
        queryset = self.get_queryset()

        if query_params:
            queryset = queryset.filter(**self.get_filter_object(query_params))

        serializer = PhotoSerializer(queryset, many=True)
        return Response(status=status.HTTP_200_OK, data=serializer.data)
