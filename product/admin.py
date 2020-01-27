from django.contrib import admin
from django.db.models import Q

from .models import Item, Photo, Type


# Register your models here.
# admin.site.register([Item])


class FrontPhotoListFilter(admin.SimpleListFilter):
    title = 'Foto frente'
    parameter_name = 'has_frontPhoto'

    def lookups(self, request, model_admin):
        return (
            ('sim', 'Sim'), ('não', 'Não'),)

    def queryset(self, request, queryset):
        if self.value() == 'sim':
            return queryset.filter(front_photo__isnull=False).exclude(front_photo='')
        if self.value() == 'não':
            return queryset.filter(Q(front_photo__isnull=True) | Q(front_photo__exact=''))


class DetailPhotoListFilter(admin.SimpleListFilter):
    title = 'Foto detalhes'
    parameter_name = 'has_detailPhoto'

    def lookups(self, request, model_admin):
        return (
            ('sim', 'Sim'), ('não', 'Não'),)

    def queryset(self, request, queryset):
        if self.value() == 'sim':
            return queryset.filter(detail_photo__isnull=False).exclude(detail_photo='')
        if self.value() == 'não':
            return queryset.filter(Q(detail_photo__isnull=True) | Q(detail_photo__exact=''))


class ConceptPhotoListFilter(admin.SimpleListFilter):
    title = 'Foto conceito'
    parameter_name = 'has_conceptPhoto'

    def lookups(self, request, model_admin):
        return (
            ('sim', 'Sim'), ('não', 'Não'),)

    def queryset(self, request, queryset):
        if self.value() == 'sim':
            return queryset.filter(concept_photo__isnull=False).exclude(concept_photo='')
        if self.value() == 'não':
            return queryset.filter(Q(concept_photo__isnull=True) | Q(concept_photo__exact=''))


class LookbookPhotoListFilter(admin.SimpleListFilter):
    title = 'Foto lookbook'
    parameter_name = 'has_lookbookPhoto'

    def lookups(self, request, model_admin):
        return (
            ('sim', 'Sim'), ('não', 'Não'),)

    def queryset(self, request, queryset):
        if self.value() == 'sim':
            return queryset.filter(lookbook_photo__isnull=False).exclude(lookbook_photo='')
        if self.value() == 'não':
            return queryset.filter(Q(lookbook_photo__isnull=True) | Q(lookbook_photo__exact=''))


class AdditionalPhotoListFilter(admin.SimpleListFilter):
    title = 'Foto adicional'
    parameter_name = 'has_additionalPhoto'

    def lookups(self, request, model_admin):
        return (
            ('sim', 'Sim'), ('não', 'Não'),)

    def queryset(self, request, queryset):
        if self.value() == 'sim':
            return queryset.filter(additional_photo__isnull=False).exclude(additional_photo='')
        if self.value() == 'não':
            return queryset.filter(Q(additional_photo__isnull=True) | Q(additional_photo__exact=''))


@admin.register(Photo)
class PhotoAdmin(admin.ModelAdmin):
    list_display = ('id', 'front_photo', 'concept_photo', 'detail_photo', 'lookbook_photo')
    search_fields = ['id']
    list_filter = (FrontPhotoListFilter, ConceptPhotoListFilter, DetailPhotoListFilter, LookbookPhotoListFilter,
                   AdditionalPhotoListFilter)


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'price')
    search_fields = ['id']
