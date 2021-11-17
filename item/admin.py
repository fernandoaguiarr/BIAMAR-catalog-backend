from django.contrib import admin

# Register your models here.
from image.admin import PhotoTabularInline
from item.models import Group, Item, Sku, Size, Color, Category, Season, Brand, Gender

_default_list_per_page = 25


@admin.register(Color)
class ColorAdmin(admin.ModelAdmin):
    fieldsets = (
        ('Internal use', {'fields': ('ERP_id', 'ERP_name')}),
        ('External use', {'fields': ('name',)})
    )

    readonly_fields = ('ERP_id', 'ERP_name')
    search_fields = ['name', 'ERP_name', 'ERP_id']
    list_display = ('ERP_id', 'name')
    list_per_page = _default_list_per_page


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
    list_per_page = _default_list_per_page


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
    list_per_page = _default_list_per_page


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
    list_per_page = _default_list_per_page


@admin.register(Gender)
class GenderAdmin(admin.ModelAdmin):
    fieldsets = (
        ('Internal use', {'fields': ('ERP_name',)}),
        ('External use', {'fields': ('name',)})
    )

    readonly_fields = ('ERP_name',)
    search_fields = ('name', 'ERP_name')
    list_display = ('name',)
    list_per_page = _default_list_per_page


@admin.register(Season)
class SeasonAdmin(admin.ModelAdmin):
    fieldsets = (
        ('Internal use', {'fields': ('ERP_id', 'ERP_name',)}),
        ('External use', {'fields': ('name',)}),
    )

    readonly_fields = ('ERP_id', 'ERP_name')
    search_fields = ['name', 'ERP_name', 'ERP_id']
    list_display = ('ERP_id', 'name')
    list_per_page = _default_list_per_page


@admin.register(Sku)
class SkuAdmin(admin.ModelAdmin):
    fieldsets = (
        ('Status', {'fields': ('active',)}),
        ('Object properties', {'fields': ['code', 'item', 'color', 'size']})
    )

    readonly_fields = ['code', 'item', 'color', 'size', 'active']
    search_fields = ('code',)
    list_display = ['code', 'item', 'color']
    list_per_page = _default_list_per_page


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
    list_per_page = _default_list_per_page
    list_filter = ('brand', 'gender')
    inlines = (SkuTabularInline,)


class ItemTabularInline(admin.TabularInline):
    model = Item
    fields = readonly_fields = ['category', 'brand', 'group', 'season', 'gender']
    can_delete = False
    extra = 0


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    fieldsets = (
        ('Object properties', {'fields': ('code',)}),
    )

    readonly_fields = ('code',)
    search_fields = ('code',)
    list_display = ('code',)
    list_per_page = _default_list_per_page
    inlines = (ItemTabularInline, PhotoTabularInline)
