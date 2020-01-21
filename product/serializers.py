from abc import ABC

from djongo.models import ObjectIdField
from rest_framework import serializers
from .models import Photo, Item, Specs


class GenericSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()


class SpecsSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    id_description = serializers.IntegerField()
    name = serializers.CharField()
    description = serializers.CharField()


class AdditionalFieldSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    title = serializers.CharField()
    description = serializers.CharField()


class SkuSerializer(serializers.Serializer):
    id = serializers.CharField()
    sku = serializers.IntegerField()
    weight = serializers.CharField()
    size = serializers.CharField()

    color = GenericSerializer()
    additional_field = serializers.ListField(child=AdditionalFieldSerializer())


class CollectionSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    season = serializers.CharField()


class ItemSerializer(serializers.ModelSerializer):
    brand = GenericSerializer()
    type = GenericSerializer()
    collection = CollectionSerializer()

    sku = serializers.ListField(child=SkuSerializer())
    specs = serializers.ListField(child=SpecsSerializer())

    class Meta:
        model = Item
        fields = ('id', 'price', 'brand', 'collection', 'type', 'sku', 'specs')


class PhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Photo
        fields = '__all__'
