from django.contrib import admin

from core.models import VirtualAgeToken, Pdf


@admin.register(VirtualAgeToken)
class VirtualAgeTokenAdmin(admin.ModelAdmin):
    fields = ('code', 'date')


@admin.register(Pdf)
class PdfAdmin(admin.ModelAdmin):
    readonly_fields = ['url_tag']
    fieldsets = [("PDF", {'fields': ['name']}), ("Link", {'fields': ['file']})]
