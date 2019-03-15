from django.core.management.base import BaseCommand, CommandError
from web import factories
from django.contrib.auth.models import User
from django.utils.text import slugify

class Command(BaseCommand):

    help = 'Generates dummy data for testing'

    def add_arguments(self, parser):
        parser.add_argument('model',
                            type=str,
                            help='The type of model to generate')

        parser.add_argument('--num',
                            default=1,
                            type=int,
                            help='The number of fake items to create.')

    def handle(self, *args, **options):
        if options['model'] == 'user':
            self.create_user(options['num'])
        elif options['model'] == 'admin':
            self.create_admin()
        elif options['model'] == 'topic':
            self.create_topics(options['num'])
        elif options['model'] == 'type':
            self.create_types(options['num'])
        elif options['model'] == 'license':
            self.create_licenses(options['num'])
        elif options['model'] == 'format':
            self.create_formats(options['num'])
        elif options['model'] == 'organisation':
            self.create_organisations(options['num'])
        elif options['model'] == 'dataset':
            self.create_datasets(options['num'])
        elif options['model'] == 'resource':
            self.create_resources(options['num'])
        elif options['model'] == 'dataset_topic':
            self.link_datasets(options['num'])
        else:
            self.create_admin()
            self.create_topics(14)
            self.create_types(3)
            self.create_licenses(4)
            self.create_formats(5)
            self.create_organisations(15)
            self.create_datasets(40)
            self.create_resources(100)
            self.link_datasets(200)

    def create_admin(self):
        user = User.objects.create_user(
            username='admin',
            email='info@example.com',
            password='admin',
            is_superuser=True,
            is_staff=True,
        )
        user.save()
        self.stdout.write(self.style.SUCCESS(
            'Admin created: "%s"' % user.username))

    def create_user(self, num=1):
        for _ in range(num):
            item = factories.UserFactory.create()
            self.stdout.write(self.style.SUCCESS(
                'User created: "%s"' % item.username))

    def create_topics(self, num=1):
        for _ in range(num):
            item = factories.TopicFactory.create()
            self.stdout.write(self.style.SUCCESS(
                'Topic created: "%s"' % item.title))

    def create_types(self, num=1):
        for _ in range(num):
            item = factories.TypeFactory.create()
            self.stdout.write(self.style.SUCCESS(
                'Type created: "%s"' % item.title))

    def create_licenses(self, num=1):
        for _ in range(num):
            item = factories.LicenseFactory.create()
            self.stdout.write(self.style.SUCCESS(
                'License created: "%s"' % item.title))

    def create_formats(self, num=1):
        try:
            for _ in range(num):
                item = factories.FormatFactory.create()
                self.stdout.write(self.style.SUCCESS(
                    'Format created: "%s"' % item.title))
        except:
            pass

    def create_organisations(self, num=1):
        for _ in range(num):
            item = factories.OrganisationFactory.create()
            self.stdout.write(self.style.SUCCESS(
                'Organisation created: "%s"' % item.title))

    def create_datasets(self, num=1):
        for _ in range(num):
            item = factories.DatasetFactory.create()
            self.stdout.write(self.style.SUCCESS(
                'Dataset created: "%s"' % item.title))

    def link_datasets(self, num=1):
        for _ in range(num):
            item = factories.DatasetTopicFactory.create()
            self.stdout.write(self.style.SUCCESS(
                'Dataset linked'))

    def create_resources(self, num=1):
        for _ in range(num):
            item = factories.ResourceFactory.create()
            self.stdout.write(self.style.SUCCESS(
                'Resource created: "%s"' % item.title))
