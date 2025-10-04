from django.core.management.base import BaseCommand
from django.test import RequestFactory
from django.urls import reverse
from django.contrib.auth.models import AnonymousUser
from app.templatetags.custom_tags import smart_breadcrumbs
from app.models import Dataset, Organisation, Topic, Resource


class Command(BaseCommand):
    help = 'Test the smart breadcrumb system'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🧪 Testing Smart Breadcrumb System'))
        self.stdout.write('=' * 50)
        
        # Create a request factory
        factory = RequestFactory()
        
        # Test different URL patterns
        test_urls = [
            ('app:datasets', {}, 'Datasets listing'),
            ('app:organisations', {}, 'Organisations listing'),
            ('app:topics', {}, 'Topics listing'),
            ('app:about', {}, 'About page'),
            ('app:contact', {}, 'Contact page'),
        ]
        
        # Test with actual objects if they exist
        try:
            dataset = Dataset.objects.filter(is_published=True).first()
            if dataset:
                test_urls.append(('app:dataset', {'slug': dataset.slug}, f'Dataset: {dataset.title}'))
                
                resource = dataset.resources.first()
                if resource:
                    test_urls.append(('app:resource', {'dataset_slug': dataset.slug, 'slug': resource.slug}, f'Resource: {resource.title}'))
                    test_urls.append(('app:resource_preview', {'dataset_slug': dataset.slug, 'slug': resource.slug}, f'Preview: {resource.title}'))
            
            org = Organisation.objects.filter(is_active=True).first()
            if org:
                test_urls.append(('app:organisation', {'slug': org.slug}, f'Organisation: {org.title}'))
                
            topic = Topic.objects.first()
            if topic:
                test_urls.append(('app:topic', {'slug': topic.slug}, f'Topic: {topic.title}'))
                
        except Exception as e:
            self.stdout.write(f'Note: Could not load test objects - {e}')
        
        # Test each URL
        for url_name, kwargs, description in test_urls:
            try:
                url = reverse(url_name, kwargs=kwargs)
                request = factory.get(url)
                request.user = AnonymousUser()
                request.resolver_match = type('MockResolverMatch', (), {
                    'url_name': url_name,
                    'kwargs': kwargs
                })()
                
                # Create mock context
                context = {'request': request}
                
                # Call the breadcrumb function
                result = smart_breadcrumbs(context)
                breadcrumbs = result.get('breadcrumbs', [])
                
                self.stdout.write(f'\n🔗 {description}')
                self.stdout.write(f'   URL: {url}')
                self.stdout.write(f'   Pattern: {url_name}')
                
                if breadcrumbs:
                    breadcrumb_text = ' > '.join([
                        f"[{b['title']}]" if not b['url'] else b['title']
                        for b in breadcrumbs
                    ])
                    self.stdout.write(f'   Breadcrumbs: {breadcrumb_text}')
                else:
                    self.stdout.write('   ❌ No breadcrumbs generated')
                    
            except Exception as e:
                self.stdout.write(f'\n❌ Error testing {url_name}: {e}')
        
        self.stdout.write('\n' + '=' * 50)
        self.stdout.write(self.style.SUCCESS('✅ Smart Breadcrumb Test Complete'))
        self.stdout.write('')
        self.stdout.write('Legend:')
        self.stdout.write('• Regular text = clickable breadcrumb link')
        self.stdout.write('• [Bracketed] = current page (no link)')
        self.stdout.write('')
        self.stdout.write('💡 Benefits of Smart Breadcrumbs:')
        self.stdout.write('• ✅ Automatic generation based on URL patterns')
        self.stdout.write('• ✅ No manual breadcrumb blocks needed in templates')
        self.stdout.write('• ✅ Consistent navigation across all pages')
        self.stdout.write('• ✅ Proper hierarchical structure')
        self.stdout.write('• ✅ Database-driven titles for dynamic content')