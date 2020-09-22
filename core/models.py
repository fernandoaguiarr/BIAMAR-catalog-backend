import os

from django.core.exceptions import ObjectDoesNotExist
from django.core.files.storage import FileSystemStorage
from django.db import models

# Create your models here.
from django.conf import settings
from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver
from django.utils.safestring import mark_safe
from rest_framework.authtoken.models import Token


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)


class VirtualAgeToken(models.Model):
    code = models.TextField(
        null=False,
        blank=False
    )

    date = models.DateTimeField(
        null=False,
        blank=False,
    )

    def __str__(self):
        return "Token {}".format(self.id)

    class Meta:
        app_label = "core"
        db_table = "core_token_virtual_age"
        verbose_name = "Token Virtual Age"
        verbose_name_plural = "Tokens Virtual Age"


def upload(instance, filename):
    return "pdf/{0}.{1}".format('_'.join(instance.name.split(' ')), filename.split('.')[-1])


class OverwriteStorage(FileSystemStorage):
    def get_available_name(self, name, **kwargs):
        if self.exists(name):
            os.remove(os.path.join(settings.MEDIA_ROOT, name))
        return name


class Pdf(models.Model):
    def url_tag(self):
        return mark_safe(
            '<span>{}{}<span/>'.format('https://biamar.com.br/', self.file.name)) if self.file else ""

    name = models.CharField(max_length=256, null=False, blank=False)
    file = models.FileField(upload_to=upload, storage=OverwriteStorage)
    url_tag.short_description = 'Url'

    def __str__(self):
        return self.name

    class Meta:
        app_label = "core"
        verbose_name = "PDF"
        verbose_name_plural = "PDFs"
