import os

from django.core.files.storage import FileSystemStorage
from django.utils.safestring import mark_safe
from django.db import models

from core import settings


def upload(instance, filename):
    return "pdf/{0}_{1}.{2}".format('_'.join(instance.name.split(' ')), instance.year, filename.split('.')[-1])


class OverwriteStorage(FileSystemStorage):
    def get_available_name(self, name, **kwargs):
        if self.exists(name):
            os.remove(os.path.join(settings.MEDIA_ROOT, name))
        return name


class Pdf(models.Model):
    def url_tag(self):
        return mark_safe(
            '<span>{}{}<span/>'.format('https://biamar.com.br/', self.file.name)) if self.file else "Unavailable :("

    name = models.CharField(max_length=256, null=False, blank=False, unique=False)
    year = models.IntegerField(null=False, blank=False, unique=False)
    file = models.FileField(upload_to=upload, storage=OverwriteStorage)
    url_tag.short_description = 'path'

    def __str__(self):
        return self.name

    class Meta:
        app_label = "utils"
        verbose_name = "PDF"
        verbose_name_plural = "PDFs"

        ordering = ['-year']
