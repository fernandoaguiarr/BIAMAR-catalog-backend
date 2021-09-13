import uuid

from django import forms
from django.contrib.postgres.fields import ArrayField
from django.utils.translation import gettext_lazy as _
from django.db import models

# Create your models here.
from item.models import Group, Color


class ExportForChoiches(models.TextChoices):
    VTEX = '1', _('VTEX')
    PRESTASHOP = '2', _('PrestaShop')
    CATALOGO = '3', _('Catálogo')


def get_export_for_default():
    return [ExportForChoiches.PRESTASHOP, ExportForChoiches.CATALOGO]


class Category(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=32)


class Photo(models.Model):
    id = models.BigAutoField(primary_key=True)
    code = models.UUIDField(default=uuid.uuid4)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    color = models.ForeignKey(Color, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    file = models.ImageField(width_field=1332, height_field=1767, max_length=128)
    export_to = ArrayField(
        models.CharField(blank=True, null=True, max_length=32),
        choices=ExportForChoiches.choices,
        default=get_export_for_default
    )
