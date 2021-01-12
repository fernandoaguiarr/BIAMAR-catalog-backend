from django.contrib import admin

from api.models import VirtualAgeToken


@admin.register(VirtualAgeToken)
class VirtualAgeTokenAdmin(admin.ModelAdmin):
    fieldsets = [(None, {'fields': ('code', 'version', 'date')})]
