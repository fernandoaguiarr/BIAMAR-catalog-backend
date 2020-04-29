from django.contrib import admin

from .models import Item, Photo

# Register your models here.
admin.site.register([Item, Photo])
