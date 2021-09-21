import random

from django.core.cache import cache
from django.core.management import BaseCommand

from image.models import Photo
from image.serializers import PhotoSerializer
from item.models import Item, Category
from item.serializers import CategorySerializer


class Command(BaseCommand):

    def __init__(self):
        super().__init__()

    @staticmethod
    def get_object(arr, keys: tuple, value):
        for obj in arr:
            if obj[keys[0]] == value:
                return obj[keys[1]]
        return None

    def handle(self, *args, **options):
        items = Item.objects.filter(group__group_has_photos__isnull=False).order_by('category', 'group'). \
            distinct('category').values('group', 'category')

        categories = Category.objects.all()
        res = []

        for category in categories.values():
            obj = category
            group = self.get_object(items, ('category', 'group'), category['id'])
            if group:
                obj = {
                    **obj,
                    **PhotoSerializer(random.choice(Photo.objects.filter(group=group)), many=False).data
                }
            res.append(CategorySerializer(obj, many=False).data)

        cache.set('categories', res, 86400)
