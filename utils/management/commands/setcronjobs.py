from crontab import CronTab

from django.utils import timezone
from django.core.management import BaseCommand


class Command(BaseCommand):
    def handle(self, *args, **options):
        with CronTab(user='django') as cron:
            cron.new(
                command="~/server/photos-backend/venv/lib/python ~/server/photos-backend/manage.py gettoken ERP_token",
                comment="Initial ERP API token setup"
            ).schedule(timezone.now())

            cron.new(
                command="~/server/photos-backend/venv/lib/python ~/server/photos-backend/manage.py gettoken ERP_token",
                comment=""
            ).hour.every(22)

            cron.new(
                command="~/server/photos-backend/venv/lib/python ~/server/photos-backend/manage.py gettoken additem",
                comment=""
            ).hour.on(12)
