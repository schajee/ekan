from django.core.management.base import BaseCommand
from app.models import Resource


class Command(BaseCommand):
    help = 'Update resource preview availability based on file formats'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🔄 Updating resource preview availability...'))
        
        resources = Resource.objects.all()
        updated_count = 0
        
        for resource in resources:
            old_preview = resource.is_preview_available
            resource.is_preview_available = resource.can_preview()
            
            if old_preview != resource.is_preview_available:
                resource.save(update_fields=['is_preview_available'])
                updated_count += 1
                
                status = '✅ Preview available' if resource.is_preview_available else '❌ No preview'
                self.stdout.write(f'   📄 {resource.title} ({resource.format}): {status}')
        
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS(f'✅ Updated {updated_count} resources'))
        
        # Show summary
        previewable = Resource.objects.filter(is_preview_available=True).count()
        total = Resource.objects.count()
        
        self.stdout.write('')
        self.stdout.write('📊 Preview Summary:')
        self.stdout.write(f'   Previewable: {previewable}')
        self.stdout.write(f'   Not previewable: {total - previewable}')
        self.stdout.write(f'   Total resources: {total}')
        
        if previewable > 0:
            self.stdout.write('')
            self.stdout.write('🎯 Previewable formats found:')
            formats = Resource.objects.filter(is_preview_available=True).values_list('format__title', flat=True).distinct()
            for fmt in formats:
                count = Resource.objects.filter(is_preview_available=True, format__title=fmt).count()
                self.stdout.write(f'   📊 {fmt}: {count} resources')
        
        self.stdout.write('')
        self.stdout.write('💡 Test preview functionality:')
        if previewable > 0:
            sample_resource = Resource.objects.filter(is_preview_available=True).first()
            if sample_resource:
                self.stdout.write(f'   Visit: /datasets/{sample_resource.dataset.slug}/resources/{sample_resource.slug}/preview/')
        else:
            self.stdout.write('   No previewable resources found. Upload CSV, XLSX, or JSON files to test.')