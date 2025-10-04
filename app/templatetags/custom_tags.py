from django.conf import settings
from django import template
from django.urls import reverse
from django.shortcuts import get_object_or_404
from app.models import Dataset, Organisation, Topic, Format, License, Resource
from django.contrib.auth.models import User

register = template.Library()


@register.inclusion_tag('partials/breadcrumbs.html', takes_context=True)
def smart_breadcrumbs(context):
    """Generate breadcrumbs automatically based on URL pattern and context"""
    request = context['request']
    
    # Get URL name and parameters
    url_name = request.resolver_match.url_name if request.resolver_match else None
    kwargs = request.resolver_match.kwargs if request.resolver_match else {}
    
    # Hide breadcrumbs on home page
    if url_name == 'home':
        return {'breadcrumbs': []}
    
    breadcrumbs = [{'title': 'Home', 'url': reverse('app:home')}]
    
    try:
        # Handle different URL patterns
        if url_name == 'datasets':
            breadcrumbs.append({'title': 'Datasets', 'url': None})
            
        elif url_name == 'dataset':
            dataset_slug = kwargs.get('slug')
            if dataset_slug:
                dataset = get_object_or_404(Dataset, slug=dataset_slug, is_published=True)
                breadcrumbs.append({'title': 'Datasets', 'url': reverse('app:datasets')})
                breadcrumbs.append({'title': dataset.title, 'url': None})
                
        elif url_name == 'resource':
            dataset_slug = kwargs.get('dataset_slug')
            resource_slug = kwargs.get('slug')
            if dataset_slug and resource_slug:
                dataset = get_object_or_404(Dataset, slug=dataset_slug, is_published=True)
                resource = get_object_or_404(Resource, slug=resource_slug, dataset=dataset)
                breadcrumbs.append({'title': 'Datasets', 'url': reverse('app:datasets')})
                breadcrumbs.append({'title': dataset.title, 'url': reverse('app:dataset', kwargs={'slug': dataset.slug})})
                breadcrumbs.append({'title': resource.title, 'url': None})
                
        elif url_name == 'resource_preview':
            dataset_slug = kwargs.get('dataset_slug')
            resource_slug = kwargs.get('slug')
            if dataset_slug and resource_slug:
                dataset = get_object_or_404(Dataset, slug=dataset_slug, is_published=True)
                resource = get_object_or_404(Resource, slug=resource_slug, dataset=dataset)
                breadcrumbs.append({'title': 'Datasets', 'url': reverse('app:datasets')})
                breadcrumbs.append({'title': dataset.title, 'url': reverse('app:dataset', kwargs={'slug': dataset.slug})})
                breadcrumbs.append({'title': resource.title, 'url': reverse('app:resource', kwargs={'dataset_slug': dataset.slug, 'slug': resource.slug})})
                breadcrumbs.append({'title': 'Preview', 'url': None})
                
        elif url_name == 'organisations':
            breadcrumbs.append({'title': 'Organisations', 'url': None})
            
        elif url_name == 'organisation':
            org_slug = kwargs.get('slug')
            if org_slug:
                org = get_object_or_404(Organisation, slug=org_slug, is_active=True)
                breadcrumbs.append({'title': 'Organisations', 'url': reverse('app:organisations')})
                breadcrumbs.append({'title': org.title, 'url': None})
                
        elif url_name == 'topics':
            breadcrumbs.append({'title': 'Topics', 'url': None})
            
        elif url_name == 'topic':
            topic_slug = kwargs.get('slug')
            if topic_slug:
                topic = get_object_or_404(Topic, slug=topic_slug)
                breadcrumbs.append({'title': 'Topics', 'url': reverse('app:topics')})
                breadcrumbs.append({'title': topic.title, 'url': None})
                
        elif url_name in ['about', 'contact', 'privacy', 'terms', 'faqs']:
            # Static pages
            page_titles = {
                'about': 'About',
                'contact': 'Contact',
                'privacy': 'Privacy Policy',
                'terms': 'Terms of Use',
                'faqs': 'Frequently Asked Questions'
            }
            breadcrumbs.append({'title': page_titles.get(url_name, url_name.title()), 'url': None})
            
        elif url_name == 'page':
            # Generic page handler
            page_slug = kwargs.get('slug', '')
            page_titles = {
                'about': 'About',
                'contact': 'Contact',
                'privacy': 'Privacy Policy',
                'terms': 'Terms of Use',
                'faqs': 'Frequently Asked Questions'
            }
            breadcrumbs.append({'title': page_titles.get(page_slug, page_slug.replace('-', ' ').title()), 'url': None})
            
        elif url_name in ['account', 'account_page']:
            breadcrumbs.append({'title': 'My Account', 'url': None})
            
    except Exception:
        # Fallback for any errors - just show current page title
        if url_name:
            breadcrumbs.append({'title': url_name.replace('_', ' ').title(), 'url': None})
    
    return {'breadcrumbs': breadcrumbs}


@register.simple_tag(name="stats")
def get_stats():
    """ Returns top-level stats """
    stats = {
        'datasets': Dataset.objects.count(),
        'organisations': Organisation.objects.count(),
        'topics': Topic.objects.count(),
        'users': User.objects.count()
    }
    return stats


@register.simple_tag(name="filters")
def get_filters():
    """ Returns sidebar filters """
    filters = {
        'organisations': Organisation.objects.all(),
        'topics': Topic.objects.all(),
        'licenses': License.objects.all(),
        'formats': Format.objects.all()
    }
    return filters

@register.simple_tag(name='query_add')
def query_add(request, **kwargs):
    updated = request.GET.copy()
    for k, v in kwargs.items():
        updated[k] = v
    return updated.urlencode()

@register.simple_tag(name='query_del')
def query_del(request, key):
    updated = request.GET.copy()
    updated.pop(key, None)
    return updated.urlencode()

@register.simple_tag(name='query_replace')
def query_replace(request, **kwargs):
    """Replace specific query parameters and ensure mutual exclusivity between topics and organizations"""
    updated = request.GET.copy()
    
    for k, v in kwargs.items():
        if k == 'topic':
            # When setting a topic, remove any organization filter and set the topic
            updated.pop('organisation', None)
            updated[k] = v
        elif k == 'organisation':
            # When setting an organization, remove any topic filter and set the organization
            updated.pop('topic', None)
            updated[k] = v
        else:
            # For other parameters, use normal add behavior
            updated[k] = v
    return updated.urlencode()

@register.simple_tag(name='app_title')
def app_title():
    return getattr(settings, 'EKAN_SITE_TITLE', 'EKAN')


@register.simple_tag(name='app_name')
def app_name():
    return getattr(settings, 'EKAN_SITE_TITLE', 'EKAN')
