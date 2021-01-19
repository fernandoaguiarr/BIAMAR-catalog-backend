from django.contrib import admin

from utils.models import Pdf


@admin.register(Pdf)
class PdfAdmin(admin.ModelAdmin):
    readonly_fields = ['url_tag']
    fieldsets = [("PDF", {'fields': ['name', 'year', 'file']}), ("Link", {'fields': ['url_tag']})]

    list_display = ['year', 'name']
    search_fields = ['name', 'year']
