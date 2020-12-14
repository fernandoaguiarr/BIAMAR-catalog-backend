# standard library
import os

# Djanfo
from django.core.files.storage import FileSystemStorage
from django.db import models
from django.conf import settings
from django.db.models.signals import post_delete
from django.dispatch import receiver
from django.utils.safestring import mark_safe


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
        app_label = "manager"
        verbose_name = "PDF"
        verbose_name_plural = "PDFs"

        ordering = ['-year']


@receiver(post_delete, sender=Pdf)
def delete_old_photo(sender, instance, **kwargs):
    if os.path.isfile(instance.file.path):
        os.remove(instance.file.path)
    return False
