from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from app.models import Organisation, Dataset, Resource, Topic, License, Format


class Command(BaseCommand):
    help = 'Show current database status and data counts'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('📊 EKAN Database Status'))
        self.stdout.write('=' * 50)
        
        # Get counts
        users = User.objects.count()
        staff = User.objects.filter(is_staff=True).count()
        superusers = User.objects.filter(is_superuser=True).count()
        
        organisations = Organisation.objects.count()
        active_orgs = Organisation.objects.filter(is_active=True).count()
        
        datasets = Dataset.objects.count()
        published_datasets = Dataset.objects.filter(is_published=True).count()
        featured_datasets = Dataset.objects.filter(is_featured=True).count()
        
        resources = Resource.objects.count()
        topics = Topic.objects.count()
        licenses = License.objects.count()
        formats = Format.objects.count()
        
        # Display status
        self.stdout.write('👥 Users:')
        self.stdout.write(f'   Total: {users}')
        self.stdout.write(f'   Staff: {staff}')
        self.stdout.write(f'   Superusers: {superusers}')
        
        self.stdout.write('\n🏛️ Organisations:')
        self.stdout.write(f'   Total: {organisations}')
        self.stdout.write(f'   Active: {active_orgs}')
        
        self.stdout.write('\n📊 Datasets:')
        self.stdout.write(f'   Total: {datasets}')
        self.stdout.write(f'   Published: {published_datasets}')
        self.stdout.write(f'   Featured: {featured_datasets}')
        
        self.stdout.write(f'\n📁 Resources: {resources}')
        self.stdout.write(f'🏷️ Topics: {topics}')
        self.stdout.write(f'📝 Licenses: {licenses}')
        self.stdout.write(f'📄 Formats: {formats}')
        
        # Status indicators
        self.stdout.write('\n🚦 Status:')
        if datasets == 0:
            self.stdout.write(self.style.ERROR('   ❌ No data found - run "python manage.py seed --quick"'))
        elif datasets < 10:
            self.stdout.write(self.style.WARNING('   ⚠️ Minimal data - consider running "python manage.py seed"'))
        else:
            self.stdout.write(self.style.SUCCESS('   ✅ Good amount of test data available'))
        
        if published_datasets == 0:
            self.stdout.write(self.style.WARNING('   ⚠️ No published datasets - visitors will see empty site'))
        
        # Recent activity
        recent_datasets = Dataset.objects.order_by('-created')[:3]
        if recent_datasets:
            self.stdout.write('\n📋 Recent Datasets:')
            for ds in recent_datasets:
                status = '🟢' if ds.is_published else '🔴'
                self.stdout.write(f'   {status} {ds.title} ({ds.organisation.title})')
        
        self.stdout.write('\n💡 Quick Commands:')
        self.stdout.write('• Add test data: python manage.py seed --quick')
        self.stdout.write('• Clear all data: python manage.py seed --clear')
        self.stdout.write('• See examples: python manage.py seed_examples')