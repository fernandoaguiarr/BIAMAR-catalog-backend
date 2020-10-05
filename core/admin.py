from django.contrib import admin

from core.models import VirtualAgeToken, Pdf


@admin.register(VirtualAgeToken)
class VirtualAgeTokenAdmin(admin.ModelAdmin):
    fieldsets = [(None, {'fields': ('code', 'version', 'date')})]


@admin.register(Pdf)
class PdfAdmin(admin.ModelAdmin):
    readonly_fields = ['url_tag']
    fieldsets = [("PDF", {'fields': ['name', 'year', 'file']}), ("Link", {'fields': ['url_tag']})]

    list_display = ['year', 'name']
    search_fields = ['name', 'year']
