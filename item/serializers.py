from rest_framework import serializers

from .models import Item, Photo


class PhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Photo
        fields = ('id', 'path', 'preview', 'type', 'items')
