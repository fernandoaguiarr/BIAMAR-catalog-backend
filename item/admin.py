import re
import json

import requests
from decouple import config

from django.urls import path
from django.contrib import admin
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.core.exceptions import ObjectDoesNotExist

from utils.models import ExportFor
from image.admin import PhotoTabularInline
from image.models import ExportedPhoto, Photo
from item.constants import DEFAULT_LIST_PER_PAGE
from item.models import Group, Item, Sku, Size, Color, Category, Season, Brand, Gender


@admin.register(Color)
class ColorAdmin(admin.ModelAdmin):
    fieldsets = (
        ('Internal use', {'fields': ('ERP_id', 'ERP_name')}),
        ('External use', {'fields': ('name',)})
    )

    readonly_fields = ('ERP_id', 'ERP_name')
    search_fields = ['name', 'ERP_name', 'ERP_id']
    list_display = ('ERP_id', 'name')
    list_per_page = DEFAULT_LIST_PER_PAGE


@admin.register(Size)
class SizeAdmin(admin.ModelAdmin):
    fieldsets = (
        ('Object Properties', {'fields': ('name',)}),
        ('Display Properties', {'fields': ('order',)})
    )

    readonly_fields = ('name',)
    search_fields = ['name', 'order']
    list_display = ('name', 'order')
    ordering = ('order',)
    list_per_page = DEFAULT_LIST_PER_PAGE


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    fieldsets = [
        ('Internal use', {'fields': ('ERP_id', 'ERP_name')}),
        ('External use', {'fields': ('name',)}),
        ('Display Properties', {'fields': ('order',)})
    ]

    readonly_fields = ('ERP_id', 'ERP_name')
    search_fields = ['name', 'ERP_name', 'ERP_id']
    list_display = ['ERP_id', 'name', 'order']
    ordering = ('order',)
    list_per_page = DEFAULT_LIST_PER_PAGE


@admin.register(Brand)
class BrandCategoryAdmin(admin.ModelAdmin):
    fieldsets = [
        ('Internal use', {'fields': ('ERP_id', 'ERP_name')}),
        ('External use', {'fields': ('name',)}),
        ('Display Properties', {'fields': ('order', 'logo')})
    ]

    readonly_fields = ('ERP_id', 'ERP_name')
    search_fields = ['name', 'ERP_name', 'ERP_id']
    list_display = ['ERP_id', 'name', 'order']
    ordering = ('order',)
    list_per_page = DEFAULT_LIST_PER_PAGE


@admin.register(Gender)
class GenderAdmin(admin.ModelAdmin):
    fieldsets = (
        ('Internal use', {'fields': ('ERP_name',)}),
        ('External use', {'fields': ('name',)})
    )

    readonly_fields = ('ERP_name',)
    search_fields = ('name', 'ERP_name')
    list_display = ('name',)
    list_per_page = DEFAULT_LIST_PER_PAGE


@admin.register(Season)
class SeasonAdmin(admin.ModelAdmin):
    fieldsets = (
        ('Internal use', {'fields': ('ERP_id', 'ERP_name',)}),
        ('External use', {'fields': ('name',)}),
    )

    readonly_fields = ('ERP_id', 'ERP_name')
    search_fields = ['name', 'ERP_name', 'ERP_id']
    list_display = ('ERP_id', 'name')
    list_per_page = DEFAULT_LIST_PER_PAGE


@admin.register(Sku)
class SkuAdmin(admin.ModelAdmin):
    fieldsets = (
        ('Status', {'fields': ('active',)}),
        ('Object properties', {'fields': ['code', 'item', 'color', 'size']})
    )

    readonly_fields = ['code', 'item', 'color', 'size', 'active']
    search_fields = ('code',)
    list_display = ['code', 'item', 'color']
    list_per_page = DEFAULT_LIST_PER_PAGE


class SkuTabularInline(admin.TabularInline):
    model = Sku
    readonly_fields = fields = ['color', 'size', 'active']
    can_delete = False
    extra = 0


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    fieldsets = (
        ('Object Properties', {'fields': ('code',)}),
        ("Code classifications", {'fields': ('category', 'brand', 'group')}),
        ('Other classifications', {'fields': ('season', 'gender')})
    )

    readonly_fields = ['code', 'category', 'brand', 'group', 'season', 'gender']
    search_fields = ('code',)
    list_display = ['code', 'category', 'brand']
    list_per_page = DEFAULT_LIST_PER_PAGE
    list_filter = ('brand', 'gender')
    inlines = (SkuTabularInline,)


class ItemTabularInline(admin.TabularInline):
    model = Item
    fields = readonly_fields = ['category', 'brand', 'group', 'season', 'gender']
    can_delete = False
    extra = 0


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):

    @staticmethod
    def join_request_values(values, queryset):
        if values[0] != '' and values[1] != '':
            values = [value.split(';')[1:] for value in values]

        keys = ['code', 'active']
        for i, obj in enumerate(queryset):
            _obj, _keys = {}, list(obj.keys())
            for j, key in enumerate(_keys):
                _obj[keys[j]] = obj[_keys[j]]

            for k, value in enumerate(values[0]):
                if values[0][k] == _obj['code']:
                    _obj['status'] = values[1][k]
                    break

            queryset[i] = _obj

        return queryset

    def get_urls(self):
        urls = super().get_urls()
        urls = [
                   path('<path:object_id>/vtex/', self.admin_site.admin_view(self.vtex_view), name="item_group_vtex"),
                   path('<path:object_id>/vtex/change/', self.admin_site.admin_view(self.change_vtex_files_view),
                        name="item_group_vtex_change"),
               ] + urls
        return urls

    def vtex_view(self, request, object_id):
        match = re.search(r'\d+', str(object_id))
        group = Group.objects.get(id=int(match.group()))
        photo = Photo.objects.get(code=request.GET.get('file'))
        queryset = Sku.objects.filter(item__code__icontains=group.code, color_id=int(request.GET.get('color')))

        allow_delete_photos = ExportedPhoto.objects.filter(
            sku__in=queryset.values_list('id', flat=True),
            photo=photo,
            active=True
        )

        status = (request.GET.get('skus', ''), request.GET.get('status', ''))
        status = self.join_request_values(status, list(allow_delete_photos.values('sku__code', 'active')))

        return render(
            request=request,
            template_name='item/upload_to_vtex.html',
            context={
                'group': group,
                'status': status,
                'allow_delete': ','.join(
                    [obj['code'] for obj in status if ('status' in obj.keys() and obj['status'] == 'OK') or (obj['active'])]),
                'results': queryset.values('code', 'color__name', 'size__name'),
                'result_headers': ('code', 'color', 'size', 'status'),
                'actions': (('Upload', 1, True), ('Delete', 0, False)),
                'file': photo.code,
                'current_url': f'{request.path}?color={request.GET.get("color")}&file={request.GET.get("file")}',
                'opts': Item._meta,
                'is_popup': True,
                'add': False,
                'change': True,
                'save_as': False,
                'show_save': True,
                'show_close': True,
                'show_delete_link': True,
                'has_delete_permission': False,
                'has_add_permission': False,
                'has_change_permission': False,
                'has_view_permission': True,
                'has_editable_inline_admin_formsets': False,
            }
        )

    @staticmethod
    def change_vtex_files_view(request, object_id):
        headers = {
            'X-VTEX-API-AppKey': config("VTEX_APP_KEY"),
            'X-VTEX-API-AppToken': config("VTEX_TOKEN"),
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        status = ['', '']

        action = int(request.POST.get('_selected_action'))

        for sku in request.POST.getlist('_selected_sku'):
            response = None
            photo = Photo.objects.get(code=request.POST.get('_selected_file').split('.')[0])
            body = {
                'label': 'Biamar',
                'isMain': request.POST.get('_selected_main_photo', False),
                'name': str(photo.code),
                'url': f'https://api.biamar.com.br{photo.file.url}'
            }

            if action:
                response = requests.post(
                    f'{config("VTEX_ENDPOINT")}catalog/pvt/stockkeepingunit/{sku}/file/',
                    headers=headers,
                    data=json.dumps(body)
                )

                if response.status_code == 200:
                    content = json.loads(response.content)
                    try:
                        exported_photo = ExportedPhoto.objects.get(sku__code=sku, photo=photo)

                        exported_photo.active = True
                        exported_photo.code = int(content['Id'])
                        exported_photo.save()
                    except ObjectDoesNotExist:
                        ExportedPhoto(
                            sku=Sku.objects.get(code=sku),
                            photo=photo,
                            exportedTo=ExportFor.objects.get(name="VTEX"),
                            active=True,
                            code=int(content['Id'])
                        ).save()

                status[0], status[1] = f'{status[0]};{response.status_code}', f'{status[1]};{sku}'

            else:
                exported_photo = ExportedPhoto.objects.get(sku__code=sku, photo=photo)
                response = requests.delete(
                    f'{config("VTEX_ENDPOINT")}catalog/pvt/stockkeepingunit/{sku}/file/{exported_photo.code}',
                    headers=headers
                )

                if response.status_code == 200:
                    exported_photo.active = False
                    exported_photo.save()

                status[0], status[1] = f'{status[0]};{response.status_code}', f'{status[1]};{sku}'

        return HttpResponseRedirect(f'{request.POST.get("_current_url")}&skus={status[1]}&status={status[0]}', '/')

    ordering = ('-code',)
    list_display = ('code',)
    search_fields = ('code',)
    readonly_fields = ('code',)
    list_per_page = DEFAULT_LIST_PER_PAGE
    inlines = (ItemTabularInline, PhotoTabularInline)
    fieldsets = (('Object properties', {'fields': ('code',)}),)
