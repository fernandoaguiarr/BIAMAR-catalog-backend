from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import send_mail
from django.core.management import BaseCommand

from utils.models import MailNotification


class Command(BaseCommand):
    def __init__(self):
        super().__init__()
        self._email_params = ['subject', 'message', 'html_message', 'recipient_list', 'from_email']

    def add_arguments(self, parser):
        parser.add_argument('notification_code', type=str)
        parser.add_argument('subject', type=str)
        parser.add_argument('message', type=str)
        parser.add_argument('html_message', type=str)

    def handle(self, *args, **options):
        try:
            notification = MailNotification.objects.get(code=options['notification_code'])
            params = dict(zip(
                self._email_params,
                [options[param] for param in list(options.keys()) if param in self._email_params]
            ))
            params['recipient_list'] = notification.users
            params['from_email'] = settings.DEFAULT_FROM_EMAIL

            send_mail(**params)

        except ObjectDoesNotExist:
            pass
