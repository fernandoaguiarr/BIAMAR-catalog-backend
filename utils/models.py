import uuid

from django.db import models
from django.db.models import UniqueConstraint
from django.contrib.postgres.fields import ArrayField
from django.utils.translation import gettext_lazy as _


# Create your models here.
class MailNotification(models.Model):
    id = models.BigAutoField(primary_key=True)
    code = models.UUIDField(default=uuid.uuid4)
    name = models.CharField(max_length=32)
    description = models.TextField()
    users = ArrayField(
        models.CharField(max_length=64)
    )

    class Meta:
        constraints = [
            UniqueConstraint(fields=['code'], name='unique_notification_code')
        ]


class ExportForTypes(models.IntegerChoices):
    IMAGE = (1, _('Imagens'))
    SKU = (2, _('Sku'))


class ExportFor(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=32)
    category = models.IntegerField(choices=ExportForTypes.choices)

    def __str__(self):
        return self.name