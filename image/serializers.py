from rest_framework import serializers


class PhotoSerializer(serializers.Serializer):
    url = serializers.ImageField(source='file', use_url=True)
