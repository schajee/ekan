from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.db import transaction


class Command(BaseCommand):
    help = 'Load essential fixtures (formats and licenses) for EKAN'

    def add_arguments(self, parser):
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Verbose output'
        )

    def handle(self, *args, **options):
        verbose = options.get('verbose', False)
        
        if verbose:
            verbosity = 2
        else:
            verbosity = 1

        self.stdout.write('📦 Loading essential fixtures...')
        
        try:
            with transaction.atomic():
                # Load formats
                self.stdout.write('📄 Loading formats...')
                call_command('loaddata', 'formats', verbosity=verbosity)
                
                # Load licenses
                self.stdout.write('📝 Loading licenses...')
                call_command('loaddata', 'licenses', verbosity=verbosity)
            
            self.stdout.write(
                self.style.SUCCESS('✅ Fixtures loaded successfully!')
            )
            
            self.print_summary()
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Failed to load fixtures: {str(e)}')
            )

    def print_summary(self):
        """Print summary of loaded fixtures"""
        from app.models import Format, License
        
        self.stdout.write('\n📈 Loaded Fixtures Summary:')
        self.stdout.write('-' * 50)
        self.stdout.write(f'📄 Formats: {Format.objects.count()}')
        self.stdout.write(f'📝 Licenses: {License.objects.count()}')
        
        self.stdout.write('\n🚀 Ready for seeding!')
        self.stdout.write('Run: python manage.py seed --datasets 50')