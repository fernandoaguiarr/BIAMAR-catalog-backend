# third-party
from rest_framework import serializers

# local Django
from api.models import VirtualAgeToken


class VirtualAgeSerializer(serializers.Serializer):
    code = serializers.CharField()

    class Meta:
        fields = 'code'
