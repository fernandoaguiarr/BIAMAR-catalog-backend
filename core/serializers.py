from rest_framework import serializers

from core.models import VirtualAgeToken


class VirtualAgeTokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = VirtualAgeToken
        fields = '__all__'
