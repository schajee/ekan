from django.core.management.base import BaseCommand
from app.models import Dataset, Resource


class Command(BaseCommand):
    help = 'Debug resources for datasets'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🔍 Resources Debug Report'))
        self.stdout.write('=' * 50)
        
        datasets = Dataset.objects.filter(is_published=True)[:5]
        
        for dataset in datasets:
            self.stdout.write(f'\n📊 Dataset: {dataset.title}')
            self.stdout.write(f'   Slug: {dataset.slug}')
            self.stdout.write(f'   Published: {dataset.is_published}')
            
            resources = dataset.resources.all()
            self.stdout.write(f'   Resources count: {resources.count()}')
            
            if resources:
                for resource in resources:
                    self.stdout.write(f'      📁 {resource.title}')
                    self.stdout.write(f'         Format: {resource.format.title if resource.format else "No format"}')
                    self.stdout.write(f'         File: {resource.file.name if resource.file else "No file"}')
                    self.stdout.write(f'         URL: {resource.url or "No URL"}')
            else:
                self.stdout.write('      ❌ No resources found')
        
        self.stdout.write('\n📈 Total Stats:')
        total_datasets = Dataset.objects.filter(is_published=True).count()
        total_resources = Resource.objects.count()
        datasets_with_resources = Dataset.objects.filter(is_published=True, resources__isnull=False).distinct().count()
        
        self.stdout.write(f'   Published datasets: {total_datasets}')
        self.stdout.write(f'   Total resources: {total_resources}')
        self.stdout.write(f'   Datasets with resources: {datasets_with_resources}')
        
        if total_resources == 0:
            self.stdout.write(self.style.ERROR('\n❌ No resources found! Run: python manage.py seed --quick'))
        elif datasets_with_resources == 0:
            self.stdout.write(self.style.ERROR('\n❌ Resources exist but not linked to published datasets!'))
        else:
            self.stdout.write(self.style.SUCCESS('\n✅ Resources are properly linked to datasets'))