import uuid

from django.contrib.postgres.fields import ArrayField
from django.db import models

from django.contrib.auth.models import User


# Create your models here.
class MailNotification(models.Model):
    id = models.BigAutoField(primary_key=True)
    code = models.UUIDField(default=uuid.uuid4())
    name = models.CharField(max_length=32)
    description = models.TextField()
    users = models.ManyToManyField(User)
