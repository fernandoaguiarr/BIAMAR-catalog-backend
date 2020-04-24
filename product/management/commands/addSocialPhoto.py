import os

from django.core.files import File
from django.core.management import BaseCommand, call_command
from ...models import Photo


class Command(BaseCommand):
    help = 'Deal with package and insert it'

    def handle(self, *args, **options):
        dirs = os.listdir('/home/biamar/media/importar_ref')

        for i in range(len(dirs)):
            if Photo.objects.filter(id=(dirs[i].split(".")[0].split("_")[0])).exists():
                photo = Photo.objects.get(id=(dirs[i].split(".")[0].split("_")[0]))
                photo.social_photo.save(dirs[i], File(open('/home/biamar/media/importar_ref/{}'.format(dirs[i]), 'rb')))
                photo.save()


