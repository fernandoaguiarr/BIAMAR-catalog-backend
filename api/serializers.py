# third-party
from rest_framework import serializers

# local Django
from api.models import VirtualAgeToken


class VirtualAgeTokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = VirtualAgeToken
        fields = '__all__'
