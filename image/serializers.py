from rest_framework import serializers


class PhotoSerializer(serializers.Serializer):
    url = serializers.SerializerMethodField('get_url')

    def get_url(self, photo):
        request = self.context.get('request')
        return request.build_absolute_uri(photo.file.url)
