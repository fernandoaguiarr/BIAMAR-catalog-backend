from rest_framework import serializers


class SeasonSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    ERP_id = serializers.IntegerField()
    name = serializers.CharField()


class CategorySerializer(serializers.Serializer):
    id = serializers.IntegerField()
    ERP_id = serializers.IntegerField()
    name = serializers.CharField()


class BrandSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    ERP_id = serializers.IntegerField()
    name = serializers.CharField()


class GenderSerializer(serializers.Serializer):
    name = serializers.CharField()


class SizeSerializer(serializers.Serializer):
    name = serializers.CharField()
    order = serializers.IntegerField(allow_null=True)


class ColorSerializer(serializers.Serializer):
    ERP_id = serializers.CharField()
    name = serializers.CharField()


class GroupSerializer(serializers.Serializer):
    id = serializers.IntegerField(source='code')


class ItemSerializer(serializers.Serializer):
    id = serializers.CharField(source='code')
    group = serializers.CharField()
    gender = serializers.CharField()
    brand = BrandSerializer()
    category = CategorySerializer()
    season = SeasonSerializer()


class SkuSerializer(serializers.Serializer):
    id = serializers.CharField(source='code')
    active = serializers.BooleanField()
    weight = serializers.DecimalField(max_digits=5, decimal_places=2, allow_null=True),
    color = ColorSerializer()
    size = SizeSerializer()
    item = serializers.CharField()
