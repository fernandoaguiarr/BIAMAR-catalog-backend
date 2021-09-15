from rest_framework import viewsets, status
from rest_framework.response import Response

from item.models import Group, Color
from image.models import Photo, Category
from utils.interfaces import CustomViewSet
from image.serializers import PhotoSerializer


# Create your views here.
class PhotoViewSet(viewsets.ViewSet, CustomViewSet):

    def __init__(self, **kwargs):
        filters = {
            'group': {'klass': Group, 'query_key': 'code'},
            'color': {'klass': Color, 'query_key': 'ERP_id'},
            'category': {'klass': Category, 'query_key': 'id'},
        }
        super().__init__(filters=filters, **kwargs)

    @staticmethod
    def get_queryset():
        return Photo.objects.all()

    def list(self, request, *args, **kwargs):
        query_params = request.query_params.copy()
        queryset = self.get_queryset()

        if query_params:
            queryset = queryset.filter(**self.get_filter_object(query_params))

        serializer = PhotoSerializer(queryset, many=True)
        return Response(status=status.HTTP_200_OK, data=serializer.data)
