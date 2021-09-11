import uuid

from django.db import models

# Create your models here.
from item.models import Group, Color


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
