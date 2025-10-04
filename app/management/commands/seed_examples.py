from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Show examples of how to use the seed command'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🌱 EKAN Seed Command Examples'))
        self.stdout.write('=' * 50)
        
        examples = [
            {
                'title': '🚀 Quick Start (Recommended for first time)',
                'command': 'python manage.py seed --quick',
                'description': 'Creates minimal test data: 5 users, 6 orgs, 20 datasets, 60 resources'
            },
            {
                'title': '📊 Full Development Dataset',
                'command': 'python manage.py seed',
                'description': 'Creates complete dataset: 15 users, 12 orgs, 50 datasets, 200 resources'
            },
            {
                'title': '🎯 Custom Amounts',
                'command': 'python manage.py seed --users 10 --datasets 30 --resources 100',
                'description': 'Create specific amounts of each data type'
            },
            {
                'title': '🗑️ Fresh Start (Destructive!)',
                'command': 'python manage.py seed --clear --quick',
                'description': 'Delete all existing data and create fresh test data'
            },
            {
                'title': '📈 Production-like Volume',
                'command': 'python manage.py seed --users 50 --organisations 20 --datasets 200 --resources 800',
                'description': 'Create large dataset for performance testing'
            }
        ]
        
        for example in examples:
            self.stdout.write(f'\n{example["title"]}')
            self.stdout.write(f'Command: {self.style.WARNING(example["command"])}')
            self.stdout.write(f'Purpose: {example["description"]}')
        
        self.stdout.write('\n' + '=' * 50)
        self.stdout.write('💡 Tips:')
        self.stdout.write('• Use --quick for initial testing')
        self.stdout.write('• Use --clear only when you want to start fresh')
        self.stdout.write('• The seed creates realistic government data with proper relationships')
        self.stdout.write('• All created datasets have topics, licenses, and resources assigned')
        self.stdout.write('• About 80% of datasets will be published (public)')
        self.stdout.write('• About 20% of datasets will be featured on homepage')
        
        self.stdout.write(f'\n🔗 After seeding, visit:')
        self.stdout.write('• Homepage: http://127.0.0.1:8000')
        self.stdout.write('• Admin: http://127.0.0.1:8000/admin')
        self.stdout.write('• API: http://127.0.0.1:8000/api/v1/')
        self.stdout.write('• Debug: http://127.0.0.1:8000/debug/')