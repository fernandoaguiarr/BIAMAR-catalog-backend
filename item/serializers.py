from rest_framework import serializers

from .models import Item, Photo


class GenericSerializer(serializers.Serializer):
    id = serializers.CharField()
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
    genre = GenericSerializer()
    collection = CollectionSerializer()

    sku = serializers.ListField(child=SkuSerializer())
    specs = serializers.ListField(child=SpecsSerializer())

    class Meta:
        model = Item
        fields = ('id', 'price', 'brand', 'genre', 'collection', 'type', 'sku', 'specs')


class GenericItemSerializer(serializers.ModelSerializer):
    brand = GenericSerializer()
    collection = CollectionSerializer()
    type = GenericSerializer()
    genre = GenericSerializer()

    class Meta:
        model = Item
        fields = ('id', 'brand', 'collection', 'type', 'genre')


class PhotoSerializer(serializers.ModelSerializer):
    photos = serializers.ListField(child=serializers.CharField(max_length=128), allow_empty=True)

    class Meta:
        model = Photo
        fields = ('id', 'photos')
