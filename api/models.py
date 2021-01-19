# third-party
from rest_framework.authtoken.models import Token

# Django
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from django.db import models


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)


class VirtualAgeToken(models.Model):
    code = models.TextField(
        null=False,
        blank=False
    )

    version = models.CharField(
        null=False,
        blank=True,
        max_length=8
    )

    date = models.DateTimeField(
        null=False,
        blank=False,
    )

    def __str__(self):
        return "Token {}".format(self.id)

    class Meta:
        app_label = "api"
        db_table = "api_token_virtual_age"
        verbose_name = "Token Virtual Age"
        verbose_name_plural = "Tokens Virtual Age"
