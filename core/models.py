from django.db import models

# Create your models here.
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
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
