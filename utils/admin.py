from django.contrib import admin
from utils.models import MailNotification


# Register your models here.
# admin.site.register(MailNotification)


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
