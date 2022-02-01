from django.core.exceptions import ObjectDoesNotExist

from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError, NotFound

from utils.models import ExportFor
from item.models import Group, Color
from image.models import Photo, Category
from utils.interfaces import CustomViewSet
from image.serializers import PhotoSerializer
from image.permissions import ImageViewSetPermission


class PhotoViewSet(viewsets.ViewSet, CustomViewSet):

    def __init__(self, **kwargs):
        filters = {
            'group': {'klass': Group, 'query_key': 'code'},
            'color': {'klass': Color, 'query_key': 'ERP_id'},
            'category': {'klass': Category, 'query_key': 'id'},
        }
        CustomViewSet.__init__(self, filters=filters)

    @staticmethod
    def get_queryset():
        return Photo.objects.all()

    def get_permissions(self):
        return [IsAuthenticated(), ImageViewSetPermission()]

    def list(self, request, *args, **kwargs):
        query_params = request.query_params.copy()
        queryset = self.get_queryset()

        if query_params:
            queryset = queryset.filter(**self.get_filter_object(query_params))
            if not request.user.has_perm('image.get_photo_api_categories'):
                queryset = queryset.exclude(export_to__isnull=True)

        serializer = PhotoSerializer(queryset, many=True, context={"request": request})
        return Response(status=status.HTTP_200_OK, data=serializer.data)

    def create(self, request):
        required_params = ['group', 'color', 'category', 'file', 'export_to']
        params = request.data

        missing = [param for param in required_params if param not in params.keys()]
        if missing:
            raise ValidationError({'detail': f'missing this params {missing}'})

        for key in [key for key in params.keys() if key not in required_params]:
            del params[key]
        params.update()
        params = {
            'group': get_object_or_404(Group.objects.all(), **{'code': int(params['group'])}),
            'color': get_object_or_404(Color.objects.all(), **{'ERP_id': params['color']}),
            'category': get_object_or_404(Category.objects.all(), **{'id': params['category']}),
            'file': params['file']
        }

        export_to = []
        for value in request.data['export_to']:
            try:
                obj = ExportFor.objects.get(id=int(value))
                export_to.append(obj)
            except ObjectDoesNotExist:
                raise NotFound(detail='Export location not found')
        photo = Photo(**params)
        photo.save()

        photo.export_to.add(*export_to)

        return Response(status=status.HTTP_200_OK)
