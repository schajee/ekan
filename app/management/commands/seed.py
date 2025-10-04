from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from django.db import transaction
from app.factories import (
    create_users, create_licenses, create_topics, create_formats,
    create_organisations, create_datasets, create_resources
)
from app.models import Organisation, License, Topic, Dataset, Format, Resource


class Command(BaseCommand):
    help = 'Generate synthetic data for EKAN development and testing'

    def add_arguments(self, parser):
        parser.add_argument(
            '--users',
            type=int,
            default=15,
            help='Number of users to create (default: 15)'
        )
        parser.add_argument(
            '--organisations',
            type=int,
            default=12,
            help='Number of organisations to create (default: 12)'
        )
        parser.add_argument(
            '--datasets',
            type=int,
            default=50,
            help='Number of datasets to create (default: 50)'
        )
        parser.add_argument(
            '--resources',
            type=int,
            default=200,
            help='Number of resources to create (default: 200)'
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing data before seeding (DESTRUCTIVE!)'
        )
        parser.add_argument(
            '--quick',
            action='store_true',
            help='Quick seed with minimal data for testing'
        )

    def handle(self, *args, **options):
        if options['quick']:
            # Quick mode with minimal data
            options['users'] = 5
            options['organisations'] = 6
            options['datasets'] = 20
            options['resources'] = 60

        if options['clear']:
            self.stdout.write(
                self.style.WARNING('⚠️  This will DELETE all existing data!')
            )
            confirm = input('Are you sure you want to continue? (yes/no): ')
            if confirm.lower() != 'yes':
                self.stdout.write(self.style.ERROR('Operation cancelled.'))
                return
            
            self.clear_data()

        try:
            with transaction.atomic():
                self.seed_data(
                    users_count=options['users'],
                    orgs_count=options['organisations'],
                    datasets_count=options['datasets'],
                    resources_count=options['resources']
                )
            
            self.stdout.write(
                self.style.SUCCESS('✅ Seeding completed successfully!')
            )
            self.print_summary()
            
        except Exception as e:
            raise CommandError(f'Seeding failed: {str(e)}')

    def clear_data(self):
        """Clear existing data (except superusers)"""
        self.stdout.write('🗑️  Clearing existing data...')
        
        # Delete in correct order to avoid foreign key issues
        Resource.objects.all().delete()
        Dataset.objects.all().delete()
        Organisation.objects.all().delete()
        Topic.objects.all().delete()
        Format.objects.all().delete()
        License.objects.all().delete()
        
        # Delete regular users (keep superusers)
        User.objects.filter(is_superuser=False).delete()
        
        self.stdout.write(self.style.SUCCESS('✅ Data cleared.'))

    def seed_data(self, users_count, orgs_count, datasets_count, resources_count):
        """Seed the database with synthetic data"""
        
        self.stdout.write('🌱 Starting data seeding...')
        
        # Create base data first
        self.stdout.write('📝 Creating licenses...')
        licenses = create_licenses()
        self.stdout.write(f'   Created {len(licenses)} licenses')
        
        self.stdout.write('🏷️  Creating topics...')
        topics = create_topics()
        self.stdout.write(f'   Created {len(topics)} topics')
        
        self.stdout.write('📄 Creating formats...')
        formats = create_formats()
        self.stdout.write(f'   Created {len(formats)} formats')
        
        # Create users
        self.stdout.write(f'👥 Creating {users_count} users...')
        users = create_users(users_count)
        self.stdout.write(f'   Created {len(users)} users')
        
        # Create organisations
        self.stdout.write(f'🏛️  Creating {orgs_count} organisations...')
        organisations = create_organisations(users, orgs_count)
        self.stdout.write(f'   Created {len(organisations)} organisations')
        
        # Create datasets
        self.stdout.write(f'📊 Creating {datasets_count} datasets...')
        datasets = create_datasets(organisations, licenses, users, topics, datasets_count)
        self.stdout.write(f'   Created {len(datasets)} datasets')
        
        # Create resources
        self.stdout.write(f'📁 Creating {resources_count} resources...')
        resources = create_resources(datasets, formats, resources_count)
        self.stdout.write(f'   Created {len(resources)} resources')

    def print_summary(self):
        """Print a summary of created data"""
        self.stdout.write('\n📈 Data Summary:')
        self.stdout.write('-' * 50)
        
        users_count = User.objects.count()
        staff_count = User.objects.filter(is_staff=True).count()
        
        self.stdout.write(f'👥 Users: {users_count} (Staff: {staff_count})')
        self.stdout.write(f'🏛️  Organisations: {Organisation.objects.count()}')
        self.stdout.write(f'📊 Datasets: {Dataset.objects.count()}')
        self.stdout.write(f'   └─ Published: {Dataset.objects.filter(is_published=True).count()}')
        self.stdout.write(f'   └─ Featured: {Dataset.objects.filter(is_featured=True).count()}')
        self.stdout.write(f'📁 Resources: {Resource.objects.count()}')
        self.stdout.write(f'🏷️  Topics: {Topic.objects.count()}')
        self.stdout.write(f'📄 Formats: {Format.objects.count()}')
        self.stdout.write(f'📝 Licenses: {License.objects.count()}')
        
        self.stdout.write('\n🚀 Ready to go!')
        self.stdout.write('Visit http://127.0.0.1:8000 to see your data')
        self.stdout.write('Admin panel: http://127.0.0.1:8000/admin')
        
        # Show some sample data
        sample_datasets = Dataset.objects.filter(is_published=True)[:3]
        if sample_datasets:
            self.stdout.write('\n📋 Sample Published Datasets:')
            for dataset in sample_datasets:
                self.stdout.write(f'   • {dataset.title} ({dataset.organisation.title})')