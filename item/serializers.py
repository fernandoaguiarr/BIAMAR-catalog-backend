from rest_framework import serializers

from .models import Item, Photo, Sku, Color, Size


class ItemPropertiesSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    erp_name = serializers.CharField(allow_null=True)
    name = serializers.CharField()


class ColorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Color
        fields = '__all__'


class SizeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Size
        fields = '__all__'


class PhotoSerializer(serializers.ModelSerializer):
    color = ColorSerializer()

    class Meta:
        model = Photo
        fields = ['group', 'path', 'preview', 'order', 'export_ecommerce', 'color', 'type']


class GroupSerializer(serializers.Serializer):
    group = serializers.CharField()
    path = serializers.CharField()
    preview = serializers.BooleanField()
    photo_type = serializers.CharField()

    class Meta:
        fields = ('group', 'path', 'preview', 'photo_type')


class ItemSerializer(serializers.ModelSerializer):
    brand = ItemPropertiesSerializer()
    type = ItemPropertiesSerializer()
    season = ItemPropertiesSerializer()

    class Meta:
        model = Item
        fields = ('id', 'genre', 'group', 'type', 'brand', 'season')


class SkuSerializer(serializers.ModelSerializer):
    size = SizeSerializer()
    color = ColorSerializer()

    class Meta:
        model = Sku
        fields = ('id', 'ean', 'weight', 'color', 'size', 'item', 'active')
