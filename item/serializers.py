from rest_framework import serializers
from .models import Item, Photo, Brand, Type, Season, TypePhoto


class PhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Photo
        fields = ('id', 'path', 'preview', 'type', 'group')


class ItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
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
