from django.db import models
from django.contrib.postgres.fields import ArrayField, JSONField


class Size(models.Model):
    description = models.CharField(
        max_length=4,
        null=False,
        verbose_name="Tamanho"
    )

    class Meta:
        verbose_name = "Grade"
        verbose_name_plural = "Grades"

    def __str__(self): return self.description


class Color(models.Model):
    readonly_fields = ('id',)

    id = models.CharField(
        primary_key=True,
        auto_created=False,
        max_length=32,
        null=False,
        verbose_name="Código"
    )

    name = models.CharField(
        max_length=32,
        null=False,
        verbose_name="Nome"
    )

    class Meta:
        verbose_name = "Cor"
        verbose_name_plural = "Cores"

    def __str__(self): return self.name


class Type(models.Model):
    id = models.IntegerField(
        primary_key=True,
        auto_created=False,
        null=False,

        verbose_name="Código"
    )

    name = models.CharField(
        max_length=64,
        null=False,
        verbose_name="Nome"
    )

    class Meta:
        verbose_name = "Tipo de Produto"
        verbose_name_plural = "Tipos de Produtos"
        ordering = ['id']

    def __str__(self): return self.name


class Season(models.Model):
    id = models.IntegerField(
        primary_key=True,
        auto_created=False,
        null=False,

        verbose_name="Código"
    )

    name = models.CharField(
        max_length=64,
        null=False,
        verbose_name="Nome"
    )

    class Meta:
        verbose_name = "Coleção"
        verbose_name_plural = "Coleções"
        ordering = ['-id']

    def __str__(self): return self.name


class Brand(models.Model):
    id = models.IntegerField(
        primary_key=True,
        auto_created=False,
        null=False,

        verbose_name="Código"
    )

    name = models.CharField(
        max_length=64,
        null=False,
        verbose_name="Nome"
    )

    class Meta:
        verbose_name = "Marca"
        verbose_name_plural = "Marcas"
        ordering = ['id']

    def __str__(self): return self.name


class Item(models.Model):
    id = models.CharField(
        primary_key=True,
        max_length=16,
        null=False
    )

    group = models.CharField(
        max_length=16,
        null=False
    )

    genre = models.CharField(
        max_length=16,
        null=True,
    )
    price = models.CharField(max_length=8, null=True)
    type = models.ForeignKey(Type, related_name="item_type", on_delete=models.CASCADE)
    brand = models.ForeignKey(Brand, related_name="brand_type", on_delete=models.CASCADE)
    season = models.ForeignKey(Season, related_name="season_type", on_delete=models.CASCADE)

    class Meta:
        verbose_name = "Item"
        verbose_name_plural = "Itens"
        ordering = ['-id']

    def __str__(self): return self.id


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
        max_length=6,
        null=False
    )

    color = models.ForeignKey(Color, on_delete=models.CASCADE)
    size = models.ForeignKey(Size, on_delete=models.CASCADE)
    id_item = models.ForeignKey(Item, on_delete=models.CASCADE)

    class Meta:
        verbose_name = "SKU"
        verbose_name_plural = "SKUs"

    def __str__(self): return self.id


class TypePhoto(models.Model):
    name = models.CharField(max_length=32, null=False)

    class Meta:
        verbose_name = "Tipo de Foto"
        verbose_name_plural = "Tipos de Fotos"
        ordering = ['id']

    def __str__(self): return self.name


class Photo(models.Model):
    type = models.ForeignKey(TypePhoto, on_delete=models.CASCADE)
    color = models.ForeignKey(Color, on_delete=models.CASCADE)
    path = models.CharField(max_length=56)
    preview = models.BooleanField()

    items = models.ManyToManyField(to=Item, auto_created=True)

    class Meta:
        verbose_name = "Foto"
        verbose_name_plural = "Fotos"
        ordering = ['-id']

    def __str__(self): return "{} - {}".format(self.color, self.type.name)
