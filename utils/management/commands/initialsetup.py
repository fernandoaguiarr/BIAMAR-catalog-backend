from decouple import config
from django.contrib.auth.models import Permission, User
from django.contrib.contenttypes.models import ContentType
from django.core.management import BaseCommand

from image.models import Category
from utils.models import ExportFor


def generate_permissions_values(model_name, action_name, extra):
    return {
        'codename': f'{action_name}_{model_name}{"_" if extra else ""}{"_".join(extra)}',
        'name': f'Can {action_name} {model_name}{" " if extra else ""} {" ".join(extra)}'
    }


class Command(BaseCommand):

    @staticmethod
    def create_permissions():
        objects = [
            {
                **generate_permissions_values('sku', 'get', ['api']),
                **{'content_type': ContentType.objects.get(app_label='item', model='sku')}
            },
            {
                **generate_permissions_values('sku', 'get', ['api', 'availability', 'field']),
                **{'content_type': ContentType.objects.get(app_label='item', model='sku')}
            },
            {
                **generate_permissions_values('item', 'get', ['api']),
                **{'content_type': ContentType.objects.get(app_label='item', model='item')}
            },
            {
                **generate_permissions_values('item', 'get', ['api', 'price', 'field']),
                **{'content_type': ContentType.objects.get(app_label='item', model='item')}
            },
            {
                **generate_permissions_values('group', 'get', ['api']),
                **{'content_type': ContentType.objects.get(app_label='item', model='group')}
            },
            {
                **generate_permissions_values('category', 'get', ['api']),
                **{'content_type': ContentType.objects.get(app_label='item', model='category')}
            },
            {
                **generate_permissions_values('brand', 'get', ['api']),
                **{'content_type': ContentType.objects.get(app_label='item', model='brand')}
            },
            {
                **generate_permissions_values('season', 'get', ['api']),
                **{'content_type': ContentType.objects.get(app_label='item', model='season')}
            },
            {
                **generate_permissions_values('photo', 'get', ['api']),
                **{'content_type': ContentType.objects.get(app_label='image', model='photo')}
            },
            {
                **generate_permissions_values('photo', 'get', ['api', 'categories']),
                **{'content_type': ContentType.objects.get(app_label='image', model='photo')}
            },
        ]

        for obj in objects:
            Permission.objects.get_or_create(**obj)

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
            Category.objects.get_or_create(**obj)

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
            ExportFor.objects.get_or_create(**obj)

    def handle(self, *args, **options):
        self.create_root_user()
        self.create_permissions()
        self.create_photo_categories()
        self.create_exportation_values()
