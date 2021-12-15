import uuid

from django.db import models
from django.conf import settings
from django.dispatch import receiver
from django.db.models import UniqueConstraint
from django.db.models.signals import pre_save
from django.utils.safestring import mark_safe

from image import constants
from utils.models import ExportFor
from item.models import Group, Color, Sku


# Create your models here.
class Category(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=32)

    def __str__(self):
        return self.name


def set_file_path(instance, filename):
    return '{}{}.{}'.format(
        constants.UPLOAD_FOLDER,
        instance.code,
        filename.split('.')[-1].lower()
    )


class Photo(models.Model):
    id = models.BigAutoField(primary_key=True)
    code = models.UUIDField(default=uuid.uuid4)
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='group_has_photos')
    color = models.ForeignKey(Color, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    file = models.ImageField(max_length=128, upload_to=set_file_path)
    export_to = models.ManyToManyField(ExportFor)

    def show_file_preview(self):
        return mark_safe(
            '<img src="%s%s" width="100" height="125" />' % (settings.MEDIA_URL, self.file) if self.file else ""
        )

    def __str__(self):
        return "{} - {}".format(self.group, self.code)

    class Meta:
        constraints = [
            UniqueConstraint(fields=['code'], name='unique_photo_code')
        ]


@receiver(pre_save, sender=Photo)
def delete_previous_handler(sender, instance, **kwargs):
    instance.file.storage.delete(set_file_path(instance, instance.file.name))


class ExportedPhoto(models.Model):
    id = models.BigAutoField(primary_key=True)
    code = models.IntegerField()
    active = models.BooleanField(default=True)
    sku = models.ForeignKey(to=Sku, on_delete=models.CASCADE)
    photo = models.ForeignKey(to=Photo, on_delete=models.CASCADE)
    exportedTo = models.ForeignKey(to=ExportFor, on_delete=models.CASCADE)
