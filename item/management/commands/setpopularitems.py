import random

from django.utils import timezone
from django.core.cache import cache
from django.core.management import BaseCommand
from django.core.exceptions import ObjectDoesNotExist

from item.models import Group
from image.models import Photo


class Command(BaseCommand):

    def __init__(self):
        super().__init__()
        self.cache_key = 'popularitems'
        self.items = []

    def add_arguments(self, parser):
        parser.add_argument('group')

    def get_index(self, group):
        for i, item in enumerate(self.items):
            if item['group'] == group:
                return i

        return -1

    def update_ranking(self, group, photo):
        index = self.get_index(group)
        if index != -1:
            self.items[index]['entries'] += 1
            self.items[index]['photo'] = photo
            return

        self.items.append({'id': group, 'entries': 1, 'photo': photo})
        self.items.sort()

    def handle(self, *args, **options):
        self.items = cache.get(self.cache_key, [])
        try:
            group = Group.objects.get(code=options['group'])
            photos = Photo.objects.filter(group=group.id, export_to__isnull=False)

            if photos:
                self.update_ranking(group.id, (random.choice(photos)).id)
                date = (timezone.now().replace(hour=23, minute=59, second=59) - timezone.now()).seconds
                cache.set(self.cache_key, self.items, date)
                return "Ranking updated."
            return "Ranking not updated. Group doesn't have eligible photo."
        except ObjectDoesNotExist:
            return "Cannot update ranking. Group doesn't exist."
