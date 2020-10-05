from rest_framework import serializers
from .models import Item, Photo, Brand, Type, Season, TypePhoto, Sku, Group, Color, Size


class GenericSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()


class ColorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Color
        fields = '__all__'


class SizeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Size
        fields = '__all__'


class TypePhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = TypePhoto
        fields = '__all__'


class PhotoSerializer(serializers.ModelSerializer):
    color = ColorSerializer(many=False, read_only=True)
    type = TypePhotoSerializer(many=False, read_only=True)

    class Meta:
        model = Photo
        fields = ('id', 'group', 'type', 'color', 'path', 'preview')


class GroupSerializer(serializers.ModelSerializer):
    photo_group__path = serializers.CharField()

    class Meta:
        model = Group
        fields = ('id', 'photo_group__path')


class ItemSerializer(serializers.ModelSerializer):
    type = GenericSerializer()
    brand = GenericSerializer()
    season = GenericSerializer()

    class Meta:
        model = Item
        fields = ('id', 'genre', 'price', 'group', 'type', 'brand', 'season')


class SkuSerializer(serializers.ModelSerializer):
    color = ColorSerializer(many=False, read_only=True)
    size = SizeSerializer(many=False, read_only=True)

    class Meta:
        model = Sku
        fields = ('id', 'ean', 'weight', 'active', 'color', 'size', 'item')


class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = '__all__'


class TypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Type
        fields = '__all__'


class SeasonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Season
        fields = '__all__'


class TypePhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = TypePhoto
        fields = '__all__'
