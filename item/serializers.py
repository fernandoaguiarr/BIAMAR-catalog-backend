from rest_framework import serializers
from .models import Item, Photo, Brand, Type, Season, TypePhoto, Sku, Group


class PhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Photo
        fields = ('id', 'group', 'type', 'color', 'path', 'preview')


class GroupSerializer(serializers.ModelSerializer):
    photo_group__path = serializers.CharField()

    class Meta:
        model = Group
        fields = ('id', 'photo_group__path')


class ItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = '__all__'


class SkuSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sku
        fields = '__all__'


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
