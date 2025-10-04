from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from django.db import transaction
import os
import shutil
from app.models import Organisation, License, Dataset, Format, Resource


class Command(BaseCommand):
    help = 'Load real file samples into media directory and create corresponding resources'

    def handle(self, *args, **options):
        self.stdout.write('📁 Loading file samples...')
        
        try:
            with transaction.atomic():
                self.load_file_samples()
            
            self.stdout.write(
                self.style.SUCCESS('✅ File samples loaded successfully!')
            )
            self.print_summary()
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Error loading file samples: {str(e)}')
            )

    def load_file_samples(self):
        """Load real file samples and create resources"""
        
        # Check if we have the required base data
        if not Format.objects.exists():
            self.stdout.write(self.style.ERROR('No formats found. Run: python manage.py load_fixtures'))
            return
            
        if not License.objects.exists():
            self.stdout.write(self.style.ERROR('No licenses found. Run: python manage.py load_fixtures'))
            return
            
        if not Organisation.objects.exists():
            self.stdout.write(self.style.ERROR('No organisations found. Run: python manage.py seed'))
            return
            
        if not User.objects.exists():
            self.stdout.write(self.style.ERROR('No users found. Run: python manage.py seed'))
            return

        # Get required objects
        license_obj = License.objects.first()
        org = Organisation.objects.first()
        author = User.objects.first()
        
        # Define file samples
        file_samples = [
            {
                'source': 'app/fixtures/file_example_CSV_5000.csv',
                'title': 'Sample Dataset',
                'description': 'CSV dataset with 5000 rows of realistic data',
                'format_slug': 'csv',
                'dataset_title': 'Sample Data Collection',
            },
            {
                'source': 'app/fixtures/file_example_JSON_1kb.json',
                'title': 'Configuration Data',
                'description': 'JSON configuration file',
                'format_slug': 'json',
                'dataset_title': 'System Configuration',
            },
            {
                'source': 'app/fixtures/file_example_XML_24kb.xml',
                'title': 'Metadata Schema',
                'description': 'XML metadata schema',
                'format_slug': 'xml',
                'dataset_title': 'Data Standards',
            },
            {
                'source': 'app/fixtures/file-sample_150kB.pdf',
                'title': 'Annual Report',
                'description': 'PDF document sample',
                'format_slug': 'pdf',
                'dataset_title': 'Reports Archive',
            },
            {
                'source': 'app/fixtures/file_example_XLSX_50.xlsx',
                'title': 'Budget Analysis',
                'description': 'Excel spreadsheet',
                'format_slug': 'xlsx',
                'dataset_title': 'Financial Data',
            },
        ]
        
        # Create resources with real files
        for file_info in file_samples:
            if not os.path.exists(file_info['source']):
                self.stdout.write(f"   ⚠️  File not found: {file_info['source']}")
                continue
                
            try:
                format_obj = Format.objects.get(slug=file_info['format_slug'])
            except Format.DoesNotExist:
                self.stdout.write(f"   ⚠️  Format not found: {file_info['format_slug']}")
                continue
            
            # Get or create dataset
            dataset, created = Dataset.objects.get_or_create(
                title=file_info['dataset_title'],
                defaults={
                    'slug': file_info['dataset_title'].lower().replace(' ', '-'),
                    'description': f"Dataset containing {file_info['title'].lower()}",
                    'organisation': org,
                    'license': license_obj,
                    'author': author,
                    'is_published': True
                }
            )
            
            # Copy file to media directory
            filename = os.path.basename(file_info['source'])
            media_path = os.path.join('media', filename)
            os.makedirs('media', exist_ok=True)
            shutil.copy2(file_info['source'], media_path)
            
            # Create resource
            resource, created = Resource.objects.get_or_create(
                title=file_info['title'],
                dataset=dataset,
                defaults={
                    'slug': f"{file_info['title'].lower().replace(' ', '-')}-{format_obj.slug}",
                    'description': file_info['description'],
                    'format': format_obj,
                    'file': filename,
                    'size': os.path.getsize(file_info['source']),
                    'mimetype': format_obj.mime_type,
                    'is_preview_available': format_obj.is_data_format,
                    'download_count': 0
                }
            )
            
            if created:
                self.stdout.write(f'   ✅ Created: {resource.title} ({format_obj.title})')
            else:
                self.stdout.write(f'   ♻️  Exists: {resource.title} ({format_obj.title})')

    def print_summary(self):
        """Print summary"""
        real_files = Resource.objects.exclude(file='').count()
        
        self.stdout.write('\n📈 File Samples Summary:')
        self.stdout.write('-' * 50)
        self.stdout.write(f'📁 Resources with real files: {real_files}')
        self.stdout.write('\n🚀 File samples ready for preview testing!')