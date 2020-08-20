from django.contrib import admin

from core.models import VirtualAgeToken


@admin.register(VirtualAgeToken)
class VirtualAgeTokenAdmin(admin.ModelAdmin):
    fields = ('code', 'date')
