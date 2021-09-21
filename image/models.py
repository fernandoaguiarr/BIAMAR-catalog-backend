import uuid

from django.db import models
from django.dispatch import receiver
from django.db.models import UniqueConstraint
from django.db.models.signals import pre_save

from utils.models import ExportFor
from item.models import Group, Color
from image.constants import constants


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
        filename.split('.')[-1]
    )


class Photo(models.Model):
    id = models.BigAutoField(primary_key=True)
    code = models.UUIDField(default=uuid.uuid4)
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='group_has_photos')
    color = models.ForeignKey(Color, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    file = models.ImageField(max_length=128, upload_to=set_file_path)
    export_to = models.ManyToManyField(ExportFor)

    def __str__(self):
        return "{} - {}".format(self.group, self.code)

    class Meta:
        constraints = [
            UniqueConstraint(fields=['code'], name='unique_photo_code')
        ]


@receiver(pre_save, sender=Photo)
def delete_previous_handler(sender, instance, **kwargs):
    instance.file.storage.delete(set_file_path(instance, instance.file.name))
