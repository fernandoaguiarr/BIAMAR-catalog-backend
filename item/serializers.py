from rest_framework import serializers


class SeasonSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    ERP_id = serializers.IntegerField()
    name = serializers.CharField()


class CategorySerializer(serializers.Serializer):
    id = serializers.IntegerField()
    ERP_id = serializers.IntegerField()
    name = serializers.CharField()
    url = serializers.CharField(allow_null=True)


class BrandSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    ERP_id = serializers.IntegerField()
    name = serializers.CharField()
    logo = serializers.CharField()


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
    price = serializers.IntegerField(allow_null=True)
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
    location = serializers.ListSerializer(child=serializers.CharField(), allow_empty=True, allow_null=True)
    available = serializers.IntegerField(allow_null=True)


class BannerItemSerializer(serializers.Serializer):
    id = serializers.CharField(source='group')
    url = serializers.FileField(source='file', use_url=True)


class BannerSerializer(serializers.Serializer):
    name = serializers.CharField()
    groups = BannerItemSerializer(many=True)
