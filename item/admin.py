from functools import partial

from django import forms
from django.contrib import admin
from django.urls import resolve

from .models import (Size, Color, TypeItem, Brand, Season, Photo, Item, Sku, TypePhoto, Group)

# Register your models here.
admin.site.register([Size, TypeItem, Brand, Season, Sku, TypePhoto])


class SkuInline(admin.TabularInline):
    model = Sku
    readonly_fields = ['id', 'ean', 'weight', 'color', 'size']
    extra = 0


class PhotoInline(admin.TabularInline):
    model = Photo
    max_num = 10
    extra = 1

    readonly_fields = ['image_tag']
    ordering = ['type', 'order']
    fieldsets = [(None, {'fields': ['type', 'color', 'path', 'order', '', 'image_tag', 'preview']})]

    def get_formset(self, request, obj=None, **kwargs):
        kwargs['formfield_callback'] = partial(self.formfield_for_dbfield, request=request, obj=obj)
        return super().get_formset(request, obj, **kwargs)

    def formfield_for_dbfield(self, db_field, **kwargs):
        obj = kwargs.pop('obj', None)
        formfield = super().formfield_for_dbfield(db_field, **kwargs)
        if db_field.name == "color" and obj:
            formfield.queryset = Color.objects.filter(sku_color__item__id__icontains=obj).distinct()
        return formfield


class ItemInline(admin.TabularInline):
    model = Item
    extra = 0


@admin.register(Photo)
class PhotoAdmin(admin.ModelAdmin):
    model = Photo
    search_fields = ['group__id']
    list_display = ['group', 'type', 'color']
    list_filter = ['type']


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    search_fields = ['id']
    list_filter = ['item_group__genre', 'item_group__brand', 'item_group__type', 'item_group__season']

    fieldsets = [(None, {'fields': ['id']}), ]
    readonly_fields = ['id']
    inlines = [ItemInline, PhotoInline]


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    readonly_fields = ['id']
    fieldsets = [(None, {'fields': ['id', 'group', 'type', 'brand', 'season']}), ]
    inlines = [SkuInline]

    list_filter = ['genre', 'brand', 'type', 'season']
    list_display = ['id', 'brand', 'type', 'season', 'genre']
    search_fields = ['id']


@admin.register(Color)
class ColorAdmin(admin.ModelAdmin):
    readonly_fields = ['id', 'name']
    fieldsets = [(None, {'fields': ['id', 'name']})]

    search_fields = ['name']
    list_display = ['id', 'name']
