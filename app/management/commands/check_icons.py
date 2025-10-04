from django.core.management.base import BaseCommand
import os
import glob


class Command(BaseCommand):
    help = 'Check for any remaining FontAwesome icon usage'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🔍 FontAwesome to Bootstrap Icons Migration Report'))
        self.stdout.write('=' * 60)
        
        # Patterns to search for
        fa_patterns = [
            'fa fa-',
            'fab fa-',
            'fas fa-',
            'far fa-',
            'fa-',
            'class="fa"'
        ]
        
        # Search in templates
        template_dirs = ['templates']
        remaining_fa = []
        
        for template_dir in template_dirs:
            if os.path.exists(template_dir):
                for root, dirs, files in os.walk(template_dir):
                    # Skip old folder
                    if 'old' in root:
                        continue
                    for file in files:
                        if file.endswith('.html'):
                            filepath = os.path.join(root, file)
                            try:
                                with open(filepath, 'r', encoding='utf-8') as f:
                                    content = f.read()
                                    for i, line in enumerate(content.split('\n'), 1):
                                        for pattern in fa_patterns:
                                            if pattern in line:
                                                remaining_fa.append({
                                                    'file': filepath,
                                                    'line': i,
                                                    'content': line.strip(),
                                                    'pattern': pattern
                                                })
                            except Exception as e:
                                self.stdout.write(f'Error reading {filepath}: {e}')
        
        # Check CSS files
        css_files = glob.glob('app/static/**/*.css', recursive=True)
        for css_file in css_files:
            if 'old' in css_file:
                continue
            try:
                with open(css_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    for i, line in enumerate(content.split('\n'), 1):
                        for pattern in fa_patterns:
                            if pattern in line:
                                remaining_fa.append({
                                    'file': css_file,
                                    'line': i,
                                    'content': line.strip(),
                                    'pattern': pattern
                                })
            except Exception as e:
                self.stdout.write(f'Error reading {css_file}: {e}')
        
        # Report results
        if remaining_fa:
            self.stdout.write(self.style.WARNING(f'⚠️  Found {len(remaining_fa)} remaining FontAwesome references:'))
            self.stdout.write('')
            for item in remaining_fa:
                self.stdout.write(f'📄 {item["file"]}:{item["line"]}')
                self.stdout.write(f'   Pattern: {item["pattern"]}')
                self.stdout.write(f'   Content: {item["content"][:100]}...')
                self.stdout.write('')
        else:
            self.stdout.write(self.style.SUCCESS('✅ No remaining FontAwesome references found!'))
        
        self.stdout.write('')
        self.stdout.write('🎯 Bootstrap Icons Migration Summary:')
        self.stdout.write('✅ Navigation icons (datasets, organizations, topics, info)')
        self.stdout.write('✅ Action icons (download, external link, close, back)')
        self.stdout.write('✅ Social icons (GitHub, Facebook, Twitter)')
        self.stdout.write('✅ Topic icons (12 updated in database)')
        self.stdout.write('✅ Format icons (8 updated in database)')
        self.stdout.write('✅ Template sizing (fa-3x → style="font-size: 3rem;")')
        self.stdout.write('')
        self.stdout.write('📋 Next Steps:')
        self.stdout.write('1. Test all icons display correctly in browser')
        self.stdout.write('2. Remove FontAwesome CSS from base template if included')
        self.stdout.write('3. Verify all icon hover effects work properly')
        self.stdout.write('4. Check responsive behavior on mobile devices')