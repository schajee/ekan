from django.core.management.base import BaseCommand
from app.models import Topic, Format


class Command(BaseCommand):
    help = 'Convert FontAwesome icons to Bootstrap Icons'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🔄 Converting FontAwesome to Bootstrap Icons'))
        
        # Topic icon mapping
        topic_icon_map = {
            'fa fa-seedling': 'bi bi-tree',
            'fa fa-shield-alt': 'bi bi-shield-check',
            'fa fa-chart-line': 'bi bi-graph-up',
            'fa fa-graduation-cap': 'bi bi-mortarboard',
            'fa fa-bolt': 'bi bi-lightning',
            'fa fa-leaf': 'bi bi-tree-fill',
            'fa fa-heartbeat': 'bi bi-heart-pulse',
            'fa fa-gavel': 'bi bi-hammer',
            'fa fa-users': 'bi bi-people',
            'fa fa-microchip': 'bi bi-cpu',
            'fa fa-home': 'bi bi-house',
            'fa fa-car': 'bi bi-car-front',
            'fa fa-plane': 'bi bi-airplane',
            'fa fa-building': 'bi bi-building',
            'fa fa-globe': 'bi bi-globe',
            'fa fa-book': 'bi bi-book',
            'fa fa-briefcase': 'bi bi-briefcase',
            'fa fa-cog': 'bi bi-gear',
            'fa fa-wrench': 'bi bi-wrench',
            'fa fa-tools': 'bi bi-tools',
        }
        
        # Format icon mapping
        format_icon_map = {
            'fa fa-file-csv': 'bi bi-filetype-csv',
            'fa fa-file-pdf': 'bi bi-filetype-pdf',
            'fa fa-file-excel': 'bi bi-filetype-xlsx',
            'fa fa-file-word': 'bi bi-filetype-docx',
            'fa fa-file-powerpoint': 'bi bi-filetype-pptx',
            'fa fa-file-code': 'bi bi-filetype-json',
            'fa fa-file-archive': 'bi bi-file-zip',
            'fa fa-file-image': 'bi bi-filetype-png',
            'fa fa-file-alt': 'bi bi-file-text',
            'fa fa-file': 'bi bi-file-earmark',
            'fa fa-database': 'bi bi-database',
            'fa fa-link': 'bi bi-link',
        }
        
        # Update topics
        updated_topics = 0
        for topic in Topic.objects.all():
            old_icon = topic.icon
            if old_icon in topic_icon_map:
                topic.icon = topic_icon_map[old_icon]
                topic.save()
                updated_topics += 1
                self.stdout.write(f'   📝 {topic.title}: {old_icon} → {topic.icon}')
            elif old_icon.startswith('fa '):
                # Fallback for unmapped icons
                fallback_icon = 'bi bi-tag'
                topic.icon = fallback_icon
                topic.save()
                updated_topics += 1
                self.stdout.write(f'   🔄 {topic.title}: {old_icon} → {fallback_icon} (fallback)')
        
        # Update formats
        updated_formats = 0
        for fmt in Format.objects.all():
            old_icon = fmt.icon
            if old_icon in format_icon_map:
                fmt.icon = format_icon_map[old_icon]
                fmt.save()
                updated_formats += 1
                self.stdout.write(f'   📄 {fmt.title}: {old_icon} → {fmt.icon}')
            elif old_icon.startswith('fa '):
                # Fallback for unmapped format icons
                fallback_icon = 'bi bi-file-earmark'
                fmt.icon = fallback_icon
                fmt.save()
                updated_formats += 1
                self.stdout.write(f'   🔄 {fmt.title}: {old_icon} → {fallback_icon} (fallback)')
        
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS(f'✅ Updated {updated_topics} topic icons'))
        self.stdout.write(self.style.SUCCESS(f'✅ Updated {updated_formats} format icons'))
        self.stdout.write('')
        self.stdout.write('Next steps:')
        self.stdout.write('1. Update templates to remove fa-3x classes (use style="font-size: 3rem;" instead)')
        self.stdout.write('2. Test the updated icons in your browser')
        self.stdout.write('3. Remove FontAwesome CSS if no longer needed')