from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from django.db import transaction
from app.factories import (
    create_users, create_topics,
    create_organisations, create_datasets, create_resources
)
from app.models import Organisation, License, Topic, Dataset, Format, Resource


class Command(BaseCommand):
    help = '''Generate synthetic data for EKAN development and testing

Stages:
  basics - Load fixtures (formats, licenses) and create admin user
  demo   - Create demo user and topics  
  full   - Create organizations, datasets, and resources
  all    - Run all stages sequentially

Examples:
  python manage.py seed --stage basics
  python manage.py seed --stage demo
  python manage.py seed --stage full --datasets 30
  python manage.py seed --stage all --quick
'''

    def add_arguments(self, parser):
        parser.add_argument(
            '--stage',
            type=str,
            choices=['basics', 'demo', 'full', 'all'],
            default='all',
            help='Which stage to run: basics (admin + fixtures), demo (demo user + topics), full (organizations + datasets), all (everything)'
        )
        parser.add_argument(
            '--users',
            type=int,
            default=15,
            help='Number of users to create in full stage (default: 15)'
        )
        parser.add_argument(
            '--organisations',
            type=int,
            default=12,
            help='Number of organisations to create in full stage (default: 12)'
        )
        parser.add_argument(
            '--datasets',
            type=int,
            default=50,
            help='Number of datasets to create in full stage (default: 50)'
        )
        parser.add_argument(
            '--resources',
            type=int,
            default=200,
            help='Number of resources to create in full stage (default: 200)'
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
        stage = options['stage']
        
        if options['quick']:
            # Quick mode with minimal data
            options['users'] = 5
            options['organisations'] = 6
            options['datasets'] = 20
            options['resources'] = 60

        if options['clear']:
            self.stdout.write(
                self.style.WARNING('⚠️  Clearing all existing data...')
            )
            self.clear_data()

        try:
            with transaction.atomic():
                if stage == 'basics':
                    self.seed_basics()
                elif stage == 'demo':
                    self.seed_demo()
                elif stage == 'full':
                    self.seed_full(
                        users_count=options['users'],
                        orgs_count=options['organisations'],
                        datasets_count=options['datasets'],
                        resources_count=options['resources']
                    )
                elif stage == 'all':
                    self.seed_basics()
                    self.seed_demo()
                    self.seed_full(
                        users_count=options['users'],
                        orgs_count=options['organisations'],
                        datasets_count=options['datasets'],
                        resources_count=options['resources']
                    )
            
            self.stdout.write(
                self.style.SUCCESS(f'✅ {stage.title()} seeding completed successfully!')
            )
            self.print_summary()
            
        except Exception as e:
            raise CommandError(f'Seeding failed: {str(e)}')

    def clear_data(self):
        """Clear existing data (except superusers and fixtures)"""
        self.stdout.write('🗑️  Clearing existing data...')
        
        # Delete in correct order to avoid foreign key issues
        Resource.objects.all().delete()
        Dataset.objects.all().delete()
        Organisation.objects.all().delete()
        Topic.objects.all().delete()
        
        # Don't delete formats and licenses - they come from fixtures
        # Format.objects.all().delete()
        # License.objects.all().delete()
        
        # Delete regular users (keep superusers)
        User.objects.filter(is_superuser=False).delete()
        
        self.stdout.write(self.style.SUCCESS('✅ Data cleared.'))

    def seed_basics(self):
        """Stage 1: Load essential fixtures and create admin user"""
        self.stdout.write('🔧 Stage 1: Loading basics (admin user + fixtures)...')
        
        from django.core.management import call_command
        
        # Load formats and licenses from fixtures
        self.stdout.write('📄 Loading formats from fixtures...')
        try:
            call_command('loaddata', 'formats', verbosity=0)
            formats_count = Format.objects.count()
            self.stdout.write(f'   ✅ Loaded {formats_count} formats')
            
            # Ensure format colors are properly set for any existing formats
            self.stdout.write('🎨 Setting format colors...')
            self.setup_format_colors()
            self.stdout.write('   ✅ Format colors configured')
            
        except Exception as e:
            self.stdout.write(self.style.WARNING(f'   ⚠️  Could not load formats: {e}'))
        
        self.stdout.write('📝 Loading licenses from fixtures...')
        try:
            call_command('loaddata', 'licenses', verbosity=0)
            licenses_count = License.objects.count()
            self.stdout.write(f'   ✅ Loaded {licenses_count} licenses')
        except Exception as e:
            self.stdout.write(self.style.WARNING(f'   ⚠️  Could not load licenses: {e}'))
        
        # Create admin user (always ensure we have one)
        self.stdout.write('👤 Creating admin user...')
        admin_user, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@example.com',
                'first_name': 'Admin',
                'last_name': 'User',
                'is_staff': True,
                'is_superuser': True,
                'is_active': True
            }
        )
        if created:
            admin_user.set_password('admin')
            admin_user.save()
            self.stdout.write('   ✅ Created admin user (password: admin)')
        else:
            admin_user.set_password('admin')
            admin_user.save()
            self.stdout.write('   ♻️  Admin user exists (password reset to: admin)')

    def seed_demo(self):
        """Stage 2: Create demo user and topics"""
        self.stdout.write('👨‍💻 Stage 2: Creating demo user and topics...')
        
        # Create demo user
        self.stdout.write('👤 Creating demo user...')
        demo_user, created = User.objects.get_or_create(
            username='demo',
            defaults={
                'email': 'demo@example.com',
                'first_name': 'Demo',
                'last_name': 'User',
                'is_staff': False,
                'is_superuser': False,
                'is_active': True
            }
        )
        if created:
            demo_user.set_password('demo')
            demo_user.save()
            self.stdout.write('   ✅ Created demo user (password: demo)')
        else:
            demo_user.set_password('demo')
            demo_user.save()
            self.stdout.write('   ♻️  Demo user exists (password reset to: demo)')
        
        # Create topics
        self.stdout.write('🏷️  Creating topics...')
        topics = create_topics()
        self.stdout.write(f'   ✅ Created {len(topics)} topics')

    def seed_full(self, users_count, orgs_count, datasets_count, resources_count):
        """Stage 3: Create organizations, datasets, and resources"""
        self.stdout.write('🏢 Stage 3: Creating organizations, datasets, and resources...')
        
        # Check for required data from previous stages
        formats = list(Format.objects.all())
        if not formats:
            self.stdout.write(self.style.WARNING('⚠️  No formats found! Run --stage basics first'))
            return
        
        licenses = list(License.objects.all())
        if not licenses:
            self.stdout.write(self.style.WARNING('⚠️  No licenses found! Run --stage basics first'))
            return
        
        topics = list(Topic.objects.all())
        if not topics:
            self.stdout.write(self.style.WARNING('⚠️  No topics found! Run --stage demo first'))
            return
        
        # Get existing users (admin + demo) and create additional ones
        existing_users = list(User.objects.all())
        additional_users_needed = max(0, users_count - len(existing_users))
        
        if additional_users_needed > 0:
            self.stdout.write(f'👥 Creating {additional_users_needed} additional users...')
            new_users = create_users(additional_users_needed)
            # Set password for new users
            for user in new_users:
                if user.username not in ['admin', 'demo']:
                    user.set_password('password')
                    user.save()
            self.stdout.write(f'   ✅ Created {len(new_users)} additional users (password: password)')
        
        # Get all users for organization creation
        all_users = list(User.objects.all())
        
        # Create organisations
        self.stdout.write(f'🏛️  Creating {orgs_count} organisations...')
        organisations = create_organisations(all_users, orgs_count)
        self.stdout.write(f'   ✅ Created {len(organisations)} organisations')
        
        # Create datasets
        self.stdout.write(f'📊 Creating {datasets_count} datasets...')
        datasets = create_datasets(organisations, licenses, all_users, topics, datasets_count)
        self.stdout.write(f'   ✅ Created {len(datasets)} datasets')
        
        # Create resources
        self.stdout.write(f'📁 Creating {resources_count} resources...')
        resources = create_resources(datasets, formats, resources_count)
        self.stdout.write(f'   ✅ Created {len(resources)} resources')

    def print_summary(self):
        """Print a summary of created data"""
        self.stdout.write('\n📈 Data Summary:')
        self.stdout.write('-' * 50)
        
        users_count = User.objects.count()
        staff_count = User.objects.filter(is_staff=True).count()
        
        self.stdout.write(f'👥 Users: {users_count} (Staff: {staff_count})')
        
        # Show stage-specific data
        formats_count = Format.objects.count()
        licenses_count = License.objects.count()
        topics_count = Topic.objects.count()
        orgs_count = Organisation.objects.count()
        datasets_count = Dataset.objects.count()
        resources_count = Resource.objects.count()
        
        # Stage 1: Basics
        if formats_count > 0 or licenses_count > 0:
            self.stdout.write(f'📄 Formats: {formats_count}')
            self.stdout.write(f'📝 Licenses: {licenses_count}')
        
        # Stage 2: Demo
        if topics_count > 0:
            self.stdout.write(f'🏷️  Topics: {topics_count}')
        
        # Stage 3: Full
        if orgs_count > 0:
            self.stdout.write(f'🏛️  Organisations: {orgs_count}')
        if datasets_count > 0:
            self.stdout.write(f'📊 Datasets: {datasets_count}')
            self.stdout.write(f'   └─ Published: {Dataset.objects.filter(is_published=True).count()}')
            self.stdout.write(f'   └─ Featured: {Dataset.objects.filter(is_featured=True).count()}')
        if resources_count > 0:
            self.stdout.write(f'📁 Resources: {resources_count}')
            file_resources = Resource.objects.exclude(file='').count()
            url_resources = Resource.objects.exclude(url='').count()
            self.stdout.write(f'   └─ Files: {file_resources}')
            self.stdout.write(f'   └─ URLs: {url_resources}')
        
        self.stdout.write('\n🚀 Ready to go!')
        self.stdout.write('Visit http://127.0.0.1:8000 to see your data')
        
        if User.objects.filter(is_superuser=True).exists():
            self.stdout.write('Admin panel: http://127.0.0.1:8000/admin')
            
        # Show login credentials
        self.stdout.write('\n🔑 Login Credentials:')
        if User.objects.filter(username='admin').exists():
            self.stdout.write('   Admin: admin / admin')
        if User.objects.filter(username='demo').exists():
            self.stdout.write('   Demo:  demo / demo')
        if User.objects.filter(is_superuser=False).exclude(username__in=['admin', 'demo']).exists():
            self.stdout.write('   Others: [username] / password')
        
        # Show next steps
        remaining_stages = []
        if formats_count == 0 or licenses_count == 0:
            remaining_stages.append('basics')
        if topics_count == 0:
            remaining_stages.append('demo')
        if orgs_count == 0:
            remaining_stages.append('full')
            
        if remaining_stages:
            self.stdout.write('\n📋 Next Steps:')
            for stage in remaining_stages:
                self.stdout.write(f'   python manage.py seed --stage {stage}')

    def setup_format_colors(self):
        """Ensure format colors are properly configured"""
        color_mapping = {
            # Green for data/spreadsheet formats
            'success': ['CSV', 'XLS', 'XLSX', 'ODS'],
            # Blue for document formats  
            'primary': ['DOC', 'DOCX'],
            # Red for PDF/presentation formats
            'danger': ['PDF', 'PPT'],
            # Orange for web/markup formats
            'warning': ['JSON', 'XML', 'HTML'],
        }
        
        for color, format_titles in color_mapping.items():
            for title in format_titles:
                Format.objects.filter(title=title).update(color=color)