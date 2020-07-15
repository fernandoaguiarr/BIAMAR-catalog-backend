from django.contrib import admin

from .models import Size, Color, Type, Brand, Season, Photo, Item, Sku, TypePhoto

# Register your models here.
admin.site.register([Size, Color, Type, Brand, Season, Photo, Item, Sku, TypePhoto])
