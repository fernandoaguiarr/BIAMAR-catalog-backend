from djongo import models
from django.utils import timezone


# Create your models here.

class Token(models.Model):
    objects = models.DjongoManager()
    _id = models.ObjectIdField()  # This is used to avoid calling makemigrations/migrate every changes

    token = models.TextField()
    date = models.DateTimeField(verbose_name='Data')

    def __str__(self):
        return str(self.date)
