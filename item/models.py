import os
from uuid import uuid4
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.conf import settings
from django.db.models.signals import post_save, pre_save, post_delete
from django.dispatch import receiver
from django.utils.safestring import mark_safe


class Size(models.Model):
    description = models.CharField(
        max_length=16,
        null=False,
    )

    def __str__(self):
        return self.description

    class Meta:
        app_label = "item"


class Color(models.Model):
    readonly_fields = ('id',)

    id = models.CharField(
        primary_key=True,
        auto_created=False,
        max_length=32,
        null=False,
    )

    name = models.CharField(
        max_length=32,
        null=False,
    )

    def __str__(self):
        return self.name

    class Meta:
        app_label = "item"


class Type(models.Model):
    id = models.IntegerField(
        primary_key=True,
        auto_created=False,
        null=False,
    )

    name = models.CharField(
        max_length=64,
        null=False,
    )

    def __str__(self):
        return self.name

    class Meta:
        app_label = "item"
        ordering = ['id']


class Season(models.Model):
    id = models.IntegerField(
        primary_key=True,
        auto_created=False,
        null=False,
    )

    name = models.CharField(
        max_length=64,
        null=False,
    )

    def __str__(self):
        return self.name

    class Meta:
        app_label = "item"
        ordering = ['-id']


class Brand(models.Model):
    id = models.IntegerField(
        primary_key=True,
        auto_created=False,
        null=False,
    )

    name = models.CharField(
        max_length=64,
        null=False,
    )

    def __str__(self):
        return self.name

    class Meta:
        app_label = "item"
        ordering = ['id']


class Group(models.Model):
    id = models.CharField(
        primary_key=True,
        max_length=16,
        null=False,
    )

    def __str__(self):
        return "{}".format(self.id)

    class Meta:
        app_label = "item"
        ordering = ['-id']


class Item(models.Model):
    id = models.CharField(
        primary_key=True,
        max_length=16,
        null=False
    )

    genre = models.CharField(
        max_length=16,
        null=True
    )

    price = models.CharField(max_length=8, null=True, blank=True)
    group = models.ForeignKey(Group, related_name="item_group", on_delete=models.CASCADE)
    type = models.ForeignKey(Type, related_name="item_type", on_delete=models.CASCADE)
    brand = models.ForeignKey(Brand, related_name="brand_type", on_delete=models.CASCADE)
    season = models.ForeignKey(Season, related_name="season_type", on_delete=models.CASCADE)

    def __str__(self):
        return self.id

    class Meta:
        app_label = "item"
        ordering = ['-id']


class Sku(models.Model):
    id = models.CharField(
        primary_key=True,
        max_length=8,
    )

    ean = models.CharField(
        max_length=24,
        null=True,
    )

    weight = models.CharField(
        max_length=16,
        null=False
    )

    active = models.BooleanField()
    color = models.ForeignKey(Color, related_name="sku_color", on_delete=models.CASCADE)
    size = models.ForeignKey(Size, related_name="sku_size", on_delete=models.CASCADE)
    item = models.ForeignKey(Item, related_name="sku_item", on_delete=models.CASCADE)

    def __str__(self):
        return self.id

    class Meta:
        app_label = "item"


class TypePhoto(models.Model):
    name = models.CharField(max_length=32, null=False)

    def __str__(self):
        return self.name

    class Meta:
        app_label = "item"
        db_table = "item_type_photo"
        ordering = ['id']


def upload(instance, filename):
    return "photos/{0}.{1}".format(uuid4().hex, filename.split('.')[-1])


class Photo(models.Model):
    def image_tag(self):
        return mark_safe(
            '<img src="{}/{}" width="100" height="100" />'.format(settings.MEDIA_URL, self.path)) if self.path else ""

    group = models.ForeignKey(Group, related_name="photo_group", on_delete=models.CASCADE)
    type = models.ForeignKey(TypePhoto, related_name="photo_type", on_delete=models.CASCADE)
    color = models.ForeignKey(Color, related_name="photo_color", on_delete=models.CASCADE)
    path = models.ImageField(upload_to=upload)
    preview = models.BooleanField()
    order = models.IntegerField(blank=True, null=True)

    image_tag.short_description = 'Image preview'

    def __str__(self):
        return "{} / {} - {}".format(self.group.id, self.color, self.type.name)

    class Meta:
        app_label = "item"
        ordering = ['-id']


@receiver(pre_save, sender=Photo)
def save_old_photo(sender, instance, **kwargs):
    try:
        instance.old_path = (Photo.objects.get(id=instance.id)).path.path
    except ObjectDoesNotExist:
        return False


@receiver(post_save, sender=Photo)
def delete_old_photo(sender, instance, **kwargs):
    if hasattr(instance, 'old_path'):
        if not instance.old_path == instance.path.path:
            if os.path.isfile(instance.old_path):
                os.remove(instance.old_path)
    return False


@receiver(post_delete, sender=Photo)
def delete_old_photo(sender, instance, **kwargs):
    if os.path.isfile(instance.path.path):
        os.remove(instance.path.path)
    return False
