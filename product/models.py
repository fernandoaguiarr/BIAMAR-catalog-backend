import os

from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.utils.deconstruct import deconstructible
from djongo import models


class Brand(models.Model):
    id = models.IntegerField()
    name = models.CharField(verbose_name="Nome", max_length=32)

    class Meta:
        abstract = True


class Collection(models.Model):
    id = models.IntegerField()
    season = models.CharField(max_length=255, verbose_name="Período")

    class Meta:
        abstract = True


class Type(models.Model):
    id = models.IntegerField()
    name = models.CharField(max_length=255, verbose_name="Nome")

    class Meta:
        abstract = True


class Sku(models.Model):
    class Color(models.Model):
        id = models.CharField(max_length=64)
        color = models.CharField(max_length=64, verbose_name="nome")

        class Meta:
            abstract = True

    class AdditionalField(models.Model):
        id = models.IntegerField()
        title = models.CharField(max_length=64, verbose_name="nome")
        description = models.CharField(max_length=64, verbose_name="descrição")

        class Meta:
            abstract = True
            verbose_name_plural = "Campos Adicionais"

    id = models.IntegerField()
    sku = models.IntegerField()
    price = models.CharField(max_length=8, verbose_name="preço")
    weight = models.CharField(max_length=8, verbose_name="Peso")
    size = models.CharField(max_length=64, verbose_name="numeração")

    color = models.EmbeddedField(model_container=Color, verbose_name="cor")
    additional_field = models.ArrayField(model_container=AdditionalField, verbose_name="campo adicional")

    class Meta:
        abstract = True


class Especs(models.Model):
    id = models.IntegerField()
    id_description = models.IntegerField(verbose_name="id descrição")
    name = models.CharField(max_length=64, verbose_name="nome")
    description = models.CharField(max_length=64, verbose_name="descrição")

    class Meta:
        abstract = True


class Item(models.Model):
    objects = models.DjongoManager()
    _id = models.ObjectIdField()  # This is used to avoid calling makemigrations/migrate every changes

    id = models.CharField(max_length=64, verbose_name="Referência")
    price = models.DecimalField(max_digits=6, decimal_places=2, verbose_name="Preço")

    brand = models.EmbeddedField(model_container=Brand, verbose_name="Marca")
    collection = models.EmbeddedField(model_container=Collection, verbose_name="Coleção")
    type = models.EmbeddedField(model_container=Type, verbose_name="Tipo")

    sku = models.ArrayField(model_container=Sku)
    especs = models.ArrayField(model_container=Especs, verbose_name="Classificação")

    class Meta:
        verbose_name_plural = "Itens"

    def __str__(self):
        return self.id


class OverwriteStorage(FileSystemStorage):
    def get_available_name(self, name, **kwargs):
        if self.exists(name):
            os.remove(os.path.join(settings.MEDIA_ROOT, name))
        return name


@deconstructible
class FrontPhoto(object):

    def __init__(self, path):
        self.sub_path = path

    def __call__(self, instance, filename):
        ext = filename.split('.')[-1]
        return os.path.join(self.sub_path, '{}_frente.{}'.format(instance.id, ext))


@deconstructible
class BackPhoto(object):

    def __init__(self, path):
        self.sub_path = path

    def __call__(self, instance, filename):
        ext = filename.split('.')[-1]
        return os.path.join(self.sub_path, '{}_costas.{}'.format(instance.id, ext))


@deconstructible
class DetailPhoto(object):

    def __init__(self, path):
        self.sub_path = path

    def __call__(self, instance, filename):
        ext = filename.split('.')[-1]
        return os.path.join(self.sub_path, '{}_detalhe.{}'.format(instance.id, ext))


@deconstructible
class LookbookPhoto(object):

    def __init__(self, path):
        self.sub_path = path

    def __call__(self, instance, filename):
        ext = filename.split('.')[-1]
        return os.path.join(self.sub_path, '{}_lookbook.{}'.format(instance.id, ext))


@deconstructible
class AdditionalPhoto(object):

    def __init__(self, path):
        self.sub_path = path

    def __call__(self, instance, filename):
        ext = filename.split('.')[-1]
        return os.path.join(self.sub_path, '{}_adicional.{}'.format(instance.id, ext))


class Photo(models.Model):
    objects = models.DjongoManager()
    _id = models.ObjectIdField()  # This is used to avoid calling makemigrations/migrate every changes

    id = models.CharField( max_length=64, verbose_name="referência")
    front_photo = models.FileField(upload_to=FrontPhoto('photo/'), storage=OverwriteStorage(), verbose_name="frente",
                                   blank=True, null=True)
    back_photo = models.FileField(upload_to=BackPhoto('photo/'), storage=OverwriteStorage(), verbose_name="costas",
                                  blank=True, null=True)
    detail_photo = models.FileField(upload_to=DetailPhoto('photo/'), storage=OverwriteStorage(), verbose_name="detalhe",
                                    blank=True, null=True)
    lookbook_photo = models.FileField(upload_to=LookbookPhoto('photo/'), storage=OverwriteStorage(),
                                      verbose_name="lookbook", blank=True, null=True)
    additional_photo = models.FileField(upload_to=AdditionalPhoto('photo/'), storage=OverwriteStorage(),
                                        verbose_name="outra", blank=True, null=True)

    class Meta:
        verbose_name = "Foto"
        verbose_name_plural = "Fotos"

    def __str__(self):
        return str(self.id)
