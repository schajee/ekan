from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.db import transaction


class Command(BaseCommand):
    help = 'Complete setup: load fixtures then seed data with file samples'

    def add_arguments(self, parser):
        parser.add_argument(
            '--datasets',
            type=int,
            default=50,
            help='Number of datasets to create (default: 50)'
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing data before loading (DESTRUCTIVE!)'
        )

    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write(
                self.style.WARNING('⚠️  This will DELETE all existing data!')
            )
            confirm = input('Are you sure you want to continue? (yes/no): ')
            if confirm.lower() != 'yes':
                self.stdout.write(self.style.ERROR('Operation cancelled.'))
                return

        try:
            with transaction.atomic():
                # Step 1: Load essential fixtures (formats and licenses)
                self.stdout.write('📦 Step 1: Loading essential fixtures...')
                call_command('load_fixtures')
                
                # Step 2: Seed synthetic data
                self.stdout.write(f'🌱 Step 2: Seeding {options["datasets"]} datasets...')
                call_command('seed', 
                           datasets=options['datasets'],
                           clear=options['clear'])
                
                # Step 3: Load real file samples
                self.stdout.write('📁 Step 3: Loading file samples...')
                call_command('load_files')
            
            self.stdout.write(
                self.style.SUCCESS('✅ Complete setup finished successfully!')
            )
            
            self.print_summary()
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Setup failed: {str(e)}')
            )

    def print_summary(self):
        """Print comprehensive summary"""
        from app.models import Format, License, Dataset, Resource, Organisation
        from django.contrib.auth.models import User
        
        self.stdout.write('\n📈 Complete Setup Summary:')
        self.stdout.write('-' * 50)
        self.stdout.write(f'👥 Users: {User.objects.count()}')
        self.stdout.write(f'🏛️  Organisations: {Organisation.objects.count()}')
        self.stdout.write(f'📄 Formats: {Format.objects.count()} (from fixtures)')
        self.stdout.write(f'📝 Licenses: {License.objects.count()} (from fixtures)')
        self.stdout.write(f'📊 Datasets: {Dataset.objects.count()}')
        self.stdout.write(f'📁 Resources: {Resource.objects.count()}')
        
        # Show breakdown of synthetic vs real files
        real_files = Resource.objects.exclude(file='').count()
        synthetic = Resource.objects.filter(file='').count()
        
        self.stdout.write(f'   └─ Real files: {real_files}')
        self.stdout.write(f'   └─ Synthetic: {synthetic}')
        
        self.stdout.write('\n🚀 Ready to go!')
        self.stdout.write('Visit http://127.0.0.1:8000 to explore your data')