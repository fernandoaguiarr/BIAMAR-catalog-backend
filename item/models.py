from django.db import models
from django.db.models import UniqueConstraint


# Create your models here.
class Gender(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=32)
    ERP_name = models.CharField(max_length=64)

    class Meta:
        constraints = [
            UniqueConstraint(fields=['ERP_name'], name='unique_gender')
        ]

    def __str__(self):
        return self.name


class Brand(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=32)
    ERP_id = models.IntegerField()
    ERP_name = models.CharField(max_length=32)
    order = models.IntegerField(null=True, blank=True)
    logo = models.CharField(max_length=32, null=True, blank=True)

    class Meta:
        constraints = [
            UniqueConstraint(fields=['ERP_id'], name='unique_brand')
        ]

    def __str__(self):
        return self.name


class Season(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=32)
    ERP_id = models.IntegerField()
    ERP_name = models.CharField(max_length=64)

    class Meta:
        constraints = [
            UniqueConstraint(fields=['ERP_id'], name='unique_season')
        ]

    def __str__(self):
        return self.name


class Category(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=32)
    ERP_id = models.IntegerField()
    ERP_name = models.CharField(max_length=32)
    order = models.IntegerField(null=True, blank=True)

    class Meta:
        ordering = ['name']
        constraints = [
            UniqueConstraint(fields=['ERP_id'], name='unique_category')
        ]

    def __str__(self):
        return self.name


class Color(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=32)
    ERP_id = models.CharField(max_length=32)
    ERP_name = models.CharField(max_length=32)

    class Meta:
        constraints = [
            UniqueConstraint(fields=['ERP_id'], name='unique_color')
        ]

    def __str__(self):
        return "{} - {}".format(self.ERP_id, self.name)


class Size(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=32)
    order = models.IntegerField(null=True, blank=True)

    class Meta:
        constraints = [
            UniqueConstraint(fields=['name'], name='unique_size')
        ]

    def __str__(self):
        return self.name


class Group(models.Model):
    id = models.BigAutoField(primary_key=True)
    code = models.IntegerField()

    class Meta:
        constraints = [
            UniqueConstraint(fields=['code'], name='unique_group')
        ]

    def __str__(self):
        return "{}".format(self.code)


class Item(models.Model):
    id = models.BigAutoField(primary_key=True)
    code = models.CharField(max_length=32)
    gender = models.ForeignKey(to=Gender, on_delete=models.CASCADE)
    category = models.ForeignKey(to=Category, on_delete=models.CASCADE, related_name='category_set')
    brand = models.ForeignKey(to=Brand, on_delete=models.CASCADE, related_name='brand_set')
    season = models.ForeignKey(to=Season, on_delete=models.CASCADE, related_name='season_set')
    group = models.ForeignKey(to=Group, on_delete=models.CASCADE, related_name='group_set')

    class Meta:
        constraints = [
            UniqueConstraint(fields=['code'], name='unique_item')
        ]

    def __str__(self):
        return self.code


class Sku(models.Model):
    id = models.BigAutoField(primary_key=True)
    code = models.CharField(max_length=32)
    active = models.BooleanField(default=False)
    weight = models.DecimalField(max_digits=5, decimal_places=2, null=True)
    item = models.ForeignKey(to=Item, on_delete=models.CASCADE, related_name='item_set')
    color = models.ForeignKey(to=Color, on_delete=models.CASCADE, related_name='color_set')
    size = models.ForeignKey(to=Size, on_delete=models.CASCADE)

    class Meta:
        ordering = ['id']
        constraints = [
            UniqueConstraint(fields=['code'], name='unique_sku')
        ]

    def __str__(self):
        return self.code
