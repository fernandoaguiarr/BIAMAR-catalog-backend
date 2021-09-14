from functools import partial

from django.contrib import admin

from item.models import Color
from image.forms import PhotoForm
from image.models import Photo, Category

# Register your models here.
class PhotoTabularInline(admin.TabularInline):
    def get_formset(self, request, obj=None, **kwargs):
        kwargs['formfield_callback'] = partial(self.formfield_for_dbfield, request=request, obj=obj)
        return super().get_formset(request, obj, **kwargs)

    def formfield_for_dbfield(self, db_field, **kwargs):
        obj = kwargs.pop('obj', None)
        formfield = super().formfield_for_dbfield(db_field, **kwargs)
        if db_field.name == "color" and obj:
            formfield.queryset = Color.objects.filter(color_set__item__code__icontains=obj.code).distinct()
        return formfield

    extra = 1
    model = Photo
    form = PhotoForm


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    fieldsets = (
        ('Object Properties', {'fields': ('name',)}),
    )
