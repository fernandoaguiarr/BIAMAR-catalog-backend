import os

from django.core.exceptions import ObjectDoesNotExist
from django.db.models.signals import post_save, pre_save, post_delete
from django.dispatch import receiver

from item.models import Photo


@receiver(pre_save, sender=Photo)
def save_old_photo(sender, instance, **kwargs):
    try:
        instance.old_path = (Photo.objects.get(id=instance.id)).path.path
    except ObjectDoesNotExist:
        return False


@receiver(post_save, sender=Photo)
def delete_old_photo(sender, instance, **kwargs):
    if hasattr(instance, 'old_path'):
        if not instance.old_path == instance.path.path:
            if os.path.isfile(instance.old_path):
                os.remove(instance.old_path)
    return False


@receiver(post_delete, sender=Photo)
def delete_old_photo(sender, instance, **kwargs):
    if os.path.isfile(instance.path.path):
        os.remove(instance.path.path)
    return False
