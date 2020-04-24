import os

from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.utils.deconstruct import deconstructible
from djongo import models
from django.db.models import Q


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

    color = models.EmbeddedField(model_container=Color, verbose_name="cor")
    additional_field = models.ArrayField(model_container=AdditionalField, verbose_name="campo adicional")

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


class Item(models.Model):
    objects = models.DjongoManager()
    _id = models.ObjectIdField()  # This is used to avoid calling makemigrations/migrate every changes

    id = models.CharField(max_length=64, verbose_name="Referência")
    price = models.DecimalField(max_digits=6, decimal_places=2, verbose_name="Preço")

    brand = models.EmbeddedField(model_container=Brand, verbose_name="Marca")
    collection = models.EmbeddedField(model_container=Collection, verbose_name="Coleção")
    type = models.EmbeddedField(model_container=Type, verbose_name="Tipo")

    sku = models.ArrayField(model_container=Sku)
    specs = models.ArrayField(model_container=Specs, verbose_name="Classificação")

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
class ConceptPhoto(object):

    def __init__(self, path):
        self.sub_path = path

    def __call__(self, instance, filename):
        ext = filename.split('.')[-1]
        return os.path.join(self.sub_path, '{}_conceito.{}'.format(instance.id, ext))


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
class SocialPhoto(object):

    def __init__(self, path):
        self.sub_path = path

    def __call__(self, instance, filename):
        ext = filename.split('.')[-1]
        return os.path.join(self.sub_path, '{}_social.{}'.format(instance.id, ext))


@deconstructible
class AdditionalPhoto(object):

    def __init__(self, path):
        self.sub_path = path

    def __call__(self, instance, filename):
        ext = filename.split('.')[-1]
        return os.path.join(self.sub_path, '{}_adicional.{}'.format(instance.id, ext))


@deconstructible
class EcommercePhoto(object):

    def __init__(self, path):
        self.sub_path = path

    def __call__(self, instance, filename):
        ext = filename.split('.')[-1]
        return os.path.join(self.sub_path, '{}_ecommerce.{}'.format(instance.id, ext))


class Photo(models.Model):
    objects = models.DjongoManager()
    _id = models.ObjectIdField()  # This is used to avoid calling makemigrations/migrate every changes

    id = models.CharField(max_length=64, verbose_name="referência")
    front_photo = models.FileField(upload_to=FrontPhoto('photo/'), storage=OverwriteStorage(), verbose_name="frente",
                                   blank=True, null=True)
    detail_photo = models.FileField(upload_to=DetailPhoto('photo/'), storage=OverwriteStorage(), verbose_name="detalhe",
                                    blank=True, null=True)

    concept_photo = models.FileField(upload_to=ConceptPhoto('photo/'), storage=OverwriteStorage(),
                                     verbose_name="Conceito",
                                     blank=True, null=True)

    lookbook_photo = models.FileField(upload_to=LookbookPhoto('photo/'), storage=OverwriteStorage(),
                                      verbose_name="Lookbook", blank=True, null=True)

    social_photo = models.FileField(upload_to=SocialPhoto('photo/'), storage=OverwriteStorage(),
                                    verbose_name="Mídias Sociais", blank=True, null=True)

    ecommerce_photo = models.FileField(upload_to=EcommercePhoto('photo/'), storage=OverwriteStorage(),
                                       verbose_name="E-commerce", blank=True, null=True)

    additional_photo = models.FileField(upload_to=AdditionalPhoto('photo/'), storage=OverwriteStorage(),
                                        verbose_name="Outra", blank=True, null=True)

    class Meta:
        verbose_name = "Foto"
        verbose_name_plural = "Fotos"

    def __str__(self):
        return str(self.id)
