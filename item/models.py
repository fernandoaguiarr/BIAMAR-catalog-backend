from django.db import models


# Create your models here.
class Brand(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=32)
    ERP_id = models.IntegerField()
    ERP_name = models.CharField(max_length=32)


class Season(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=32)
    ERP_id = models.IntegerField()
    ERP_name = models.CharField(max_length=64)


class Category(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=32)
    ERP_id = models.IntegerField()
    ERP_name = models.CharField(max_length=32)


class Color(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=32)
    ERP_id = models.IntegerField()
    ERP_name = models.CharField(max_length=32)


class Size(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=32)
    order = models.IntegerField()
    ERP_id = models.IntegerField()


class Group(models.Model):
    id = models.BigAutoField(primary_key=True)
    code = models.IntegerField()


class Item(models.Model):
    id = models.BigAutoField(primary_key=True)
    genre = models.CharField(max_length=32)
    category = models.ForeignKey(to=Category, on_delete=models.CASCADE)
    brand = models.ForeignKey(to=Brand, on_delete=models.CASCADE)
    season = models.ForeignKey(to=Season, on_delete=models.CASCADE)
    group = models.ForeignKey(to=Group, on_delete=models.CASCADE)


class Sku(models.Model):
    id = models.BigAutoField(primary_key=True)
    code = models.CharField(max_length=32)
    active = models.BooleanField(default=False)
    weight = models.DecimalField(max_digits=5, decimal_places=2)
    item = models.ForeignKey(to=Item, on_delete=models.CASCADE)
    color = models.ForeignKey(to=Color, on_delete=models.CASCADE)
    size = models.ForeignKey(to=Size, on_delete=models.CASCADE)
