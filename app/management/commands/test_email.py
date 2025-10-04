from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.conf import settings


class Command(BaseCommand):
    help = 'Test email configuration'

    def add_arguments(self, parser):
        parser.add_argument(
            '--to',
            type=str,
            help='Email address to send test email to',
        )

    def handle(self, *args, **options):
        to_email = options.get('to')
        
        if not to_email:
            self.stdout.write(
                self.style.ERROR('Please provide a recipient email address using --to')
            )
            return
        
        try:
            send_mail(
                subject='[EKAN] Test Email Configuration',
                message='This is a test email to verify that your EKAN email configuration is working correctly.',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[to_email],
                fail_silently=False,
            )
            
            self.stdout.write(
                self.style.SUCCESS(f'Test email sent successfully to {to_email}')
            )
            self.stdout.write(
                f'Email backend: {settings.EMAIL_BACKEND}'
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Failed to send email: {str(e)}')
            )