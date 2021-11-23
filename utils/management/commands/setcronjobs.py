from crontab import CronTab
from django.core.management import BaseCommand


class Command(BaseCommand):
    def handle(self, *args, **options):
        with CronTab(user='django') as cron:
            cron.new(command="echo hello there").minute.every(1)