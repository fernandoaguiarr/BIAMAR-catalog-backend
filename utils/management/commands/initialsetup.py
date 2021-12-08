from decouple import config
from django.contrib.auth.models import Permission, User
from django.contrib.contenttypes.models import ContentType
from django.core.management import BaseCommand, call_command

from image.models import Category
from utils.models import ExportFor


class Command(BaseCommand):

    @staticmethod
    def create_permissions():
        Permission.objects.get_or_create(
            codename='can_view_sku_availability',
            name='Can view sku availability',
            content_type=ContentType.objects.get(app_label='item', model='sku')
        )

        Permission.objects.get_or_create(
            codename='can_view_item_price',
            name='Can view item price',
            content_type=ContentType.objects.get(app_label='item', model='item')
        )

        Permission.objects.get_or_create(
            codename='can_view_all_photos',
            name='Can view all photos',
            content_type=ContentType.objects.get(app_label='image', model='photo')
        )

    @staticmethod
    def create_crontab_jobs():
        pass

    @staticmethod
    def create_photo_categories():
        objects = [
            {"name": "Técnica (frente)"},
            {"name": "Técnica (detalhe)"},
            {"name": "conceito"},
            {"name": "lookbook"},
            {"name": "e-commerce"},
            {"name": "blogueira"},
            {"name": "estampa"},
        ]

        for obj in objects:
            Category.objects.get_or_create(*obj)

    @staticmethod
    def create_root_user():
        if not User.objects.filter(username='root').exists():
            User.objects.create_superuser(
                username=config('DJANGO_SUPERUSER_USERNAME'),
                email=config('DJANGO_SUPERUSER_EMAIL'),
                password=config('DJANGO_SUPERUSER_PASSWORD')
            )

    @staticmethod
    def create_exportation_values():
        objects = [
            {"name": "VTEX", "category": 1},
            {"name": "Catálogo", "category": 1},
            {"name": "PrestaShop", "category": 1},
        ]

        for obj in objects:
            ExportFor.objects.get_or_create(*obj)

    def handle(self, *args, **options):
        self.create_root_user()
        self.create_permissions()
        self.create_photo_categories()
        self.create_exportation_values()
