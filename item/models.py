from djongo import models


# ABSTRACT MODELS
# ITEM ABSTRACT MODELS
class Brand(models.Model):
    id = models.IntegerField()
    name = models.CharField(verbose_name="Nome", max_length=32)

    class Meta:
        abstract = True

    def __str__(self):
        return str(self.id)


class Collection(models.Model):
    id = models.IntegerField()
    season = models.CharField(max_length=255, verbose_name="Período")

    class Meta:
        abstract = True

    def __str__(self):
        return str(self.id)


class Type(models.Model):
    id = models.IntegerField()
    name = models.CharField(max_length=255, verbose_name="Nome")

    class Meta:
        abstract = True

    def __str__(self):
        return str(self.id)


class Genre(models.Model):
    id = models.IntegerField()
    name = models.CharField(max_length=32, verbose_name="Nome")

    class Meta:
        abstract = True

    def __str__(self):
        return str(self.id)

class Sku(models.Model):
    class Color(models.Model):
        id = models.CharField(max_length=64)
        name = models.CharField(max_length=64, verbose_name="nome")

        class Meta:
            abstract = True

        def __str__(self):
            return str(self.id)

    class AdditionalField(models.Model):
        id = models.IntegerField()
        title = models.CharField(max_length=64, verbose_name="nome")
        description = models.CharField(max_length=64, verbose_name="descrição")

        class Meta:
            abstract = True
            verbose_name_plural = "Campos Adicionais"

        def __str__(self):
            return str(self.id)

    id = models.CharField(max_length=255)
    sku = models.IntegerField()
    price = models.CharField(max_length=8, verbose_name="preço")
    weight = models.CharField(max_length=8, verbose_name="Peso")
    size = models.CharField(max_length=64, verbose_name="numeração")

    color = models.EmbeddedModelField(model_container=Color, verbose_name="Cor")
    additional_field = models.ArrayModelField(model_container=AdditionalField, verbose_name="campo adicional")

    class Meta:
        abstract = True

    def __str__(self):
        return str(self.id)


class Specs(models.Model):
    id = models.IntegerField()
    id_description = models.IntegerField(verbose_name="id descrição")
    name = models.CharField(max_length=64, verbose_name="nome")
    description = models.CharField(max_length=64, verbose_name="descrição")

    class Meta:
        abstract = True

    def __str__(self):
        return str(self.id)


# PHOTO ABSTRACT MODELS

# class Url(models.Model):
#     path =

# NON ABSTRACT MODELS
class Item(models.Model):
    _id = models.ObjectIdField()  # This is used to avoid calling makemigrations/migrate every changes
    id = models.CharField(max_length=64, verbose_name="Referência")
    price = models.DecimalField(max_digits=6, decimal_places=2, verbose_name="Preço")

    brand = models.EmbeddedModelField(model_container=Brand, verbose_name="Marca")
    collection = models.EmbeddedModelField(model_container=Collection, verbose_name="Coleção")
    type = models.EmbeddedModelField(model_container=Type, verbose_name="Tipo")
    genre = models.EmbeddedModelField(model_container=Genre, verbose_name="Genero")

    sku = models.ArrayModelField(model_container=Sku)
    specs = models.ArrayModelField(model_container=Specs, verbose_name="Classificação")

    objects = models.DjongoManager()

    class Meta:
        verbose_name_plural = "Itens"

    def __str__(self):
        return self.id


class Photo(models.Model):
    _id = models.ObjectIdField()  # This is used to avoid calling makemigrations/migrate every changes
    id = models.CharField(max_length=32)
    photos = models.ListField(null=True, blank=True)

    objects = models.DjongoManager()

    def __str__(self):
        return self.id
