from django.contrib.sites.models import Site
from rest_framework import serializers

from item.serializers import ColorSerializer


class PhotoSerializer(serializers.Serializer):
    url = serializers.SerializerMethodField('get_url')
    color = ColorSerializer()

    def get_url(self, photo):
        request = self.context.get('request')
        return request.build_absolute_uri(photo.file.url)


class DefaultPhotoSerializer(serializers.Serializer):
    url = serializers.ImageField(source='file', use_url=True, )

    def get_url(self, photo):
        return f'{Site.objects.get_current().domain}/{photo.file.url}'
