from django.contrib import admin

from utils.forms import ExportForForm
from utils.models import MailNotification, ExportFor


# Register your models here.
@admin.register(MailNotification)
class MailNotificationAdmin(admin.ModelAdmin):
    fieldsets = (
        ('Query code', {'fields': ('code',)}),
        ("Notification's info", {'fields': ('name', 'description')}),
        ('Send to', {'fields': ('users',)})
    )

    readonly_fields = ('code',)
    search_fields = ('code', 'name')
    list_display = ('name',)


@admin.register(ExportFor)
class ExportForAdmin(admin.ModelAdmin):
    search_fields = ('name',)
    list_display = ('name', 'category')
    form = ExportForForm
