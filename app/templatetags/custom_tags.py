from django.conf import settings
from django import template
from django.urls import reverse
from django.shortcuts import get_object_or_404
from app.models import Dataset, Organisation, Topic, Format, License, Resource
from django.contrib.auth.models import User
import os

register = template.Library()


@register.filter
def basename(value):
    """Extract the filename from a file path"""
    if value:
        return os.path.basename(value)
    return value


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
                
        elif url_name == 'dataset_create':
            org_slug = kwargs.get('org_slug')
            if org_slug:
                org = get_object_or_404(Organisation, slug=org_slug, is_active=True)
                breadcrumbs.append({'title': 'Organisations', 'url': reverse('app:organisations')})
                breadcrumbs.append({'title': org.title, 'url': reverse('app:organisation', kwargs={'slug': org.slug})})
                breadcrumbs.append({'title': 'Create Dataset', 'url': None})
                
        elif url_name == 'dataset_edit':
            dataset_slug = kwargs.get('slug')
            if dataset_slug:
                dataset = get_object_or_404(Dataset, slug=dataset_slug)
                breadcrumbs.append({'title': 'Datasets', 'url': reverse('app:datasets')})
                breadcrumbs.append({'title': dataset.title, 'url': reverse('app:dataset', kwargs={'slug': dataset.slug})})
                breadcrumbs.append({'title': 'Edit', 'url': None})
                
        elif url_name == 'resource':
            resource_uuid = kwargs.get('uuid')
            dataset_slug = kwargs.get('dataset_slug')
            if resource_uuid and dataset_slug:
                resource = get_object_or_404(Resource, id=resource_uuid, dataset__slug=dataset_slug, dataset__is_published=True)
                dataset = resource.dataset
                breadcrumbs.append({'title': 'Datasets', 'url': reverse('app:datasets')})
                breadcrumbs.append({'title': dataset.title, 'url': reverse('app:dataset', kwargs={'slug': dataset.slug})})
                breadcrumbs.append({'title': resource.title, 'url': None})
                
        elif url_name == 'resource_create':
            dataset_slug = kwargs.get('dataset_slug')
            if dataset_slug:
                dataset = get_object_or_404(Dataset, slug=dataset_slug)
                breadcrumbs.append({'title': 'Datasets', 'url': reverse('app:datasets')})
                breadcrumbs.append({'title': dataset.title, 'url': reverse('app:dataset', kwargs={'slug': dataset.slug})})
                breadcrumbs.append({'title': 'Add Resource', 'url': None})
                
        elif url_name == 'resource_edit':
            resource_uuid = kwargs.get('uuid')
            dataset_slug = kwargs.get('dataset_slug')
            if resource_uuid and dataset_slug:
                resource = get_object_or_404(Resource, id=resource_uuid, dataset__slug=dataset_slug)
                dataset = resource.dataset
                breadcrumbs.append({'title': 'Datasets', 'url': reverse('app:datasets')})
                breadcrumbs.append({'title': dataset.title, 'url': reverse('app:dataset', kwargs={'slug': dataset.slug})})
                breadcrumbs.append({'title': resource.title, 'url': reverse('app:resource', kwargs={'dataset_slug': dataset.slug, 'uuid': resource.id})})
                breadcrumbs.append({'title': 'Edit', 'url': None})
                
        elif url_name == 'resource_preview':
            resource_uuid = kwargs.get('uuid')
            dataset_slug = kwargs.get('dataset_slug')
            if resource_uuid and dataset_slug:
                resource = get_object_or_404(Resource, id=resource_uuid, dataset__slug=dataset_slug, dataset__is_published=True)
                dataset = resource.dataset
                breadcrumbs.append({'title': 'Datasets', 'url': reverse('app:datasets')})
                breadcrumbs.append({'title': dataset.title, 'url': reverse('app:dataset', kwargs={'slug': dataset.slug})})
                breadcrumbs.append({'title': resource.title, 'url': reverse('app:resource', kwargs={'dataset_slug': dataset.slug, 'uuid': resource.id})})
                breadcrumbs.append({'title': 'Preview', 'url': None})
                
        elif url_name == 'organisations':
            breadcrumbs.append({'title': 'Organisations', 'url': None})
            
        elif url_name == 'organisation':
            org_slug = kwargs.get('slug')
            if org_slug:
                org = get_object_or_404(Organisation, slug=org_slug, is_active=True)
                breadcrumbs.append({'title': 'Organisations', 'url': reverse('app:organisations')})
                breadcrumbs.append({'title': org.title, 'url': None})
                
        elif url_name == 'organisation_datasets':
            org_slug = kwargs.get('slug')
            if org_slug:
                org = get_object_or_404(Organisation, slug=org_slug, is_active=True)
                breadcrumbs.append({'title': 'Organisations', 'url': reverse('app:organisations')})
                breadcrumbs.append({'title': org.title, 'url': reverse('app:organisation', kwargs={'slug': org.slug})})
                breadcrumbs.append({'title': 'Datasets', 'url': None})
                
        elif url_name == 'organisation_register':
            breadcrumbs.append({'title': 'Organisations', 'url': reverse('app:organisations')})
            breadcrumbs.append({'title': 'Register Organization', 'url': None})
                
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
        'datasets': Dataset.objects.filter(is_published=True).count(),
        'organisations': Organisation.objects.filter(is_active=True, status=Organisation.STATUS_APPROVED).count(),
        'topics': Topic.objects.count(),
        'users': User.objects.count()
    }
    return stats


@register.simple_tag(name="filters")
def get_filters():
    """ Returns sidebar filters """
    filters = {
        'organisations': Organisation.objects.filter(is_active=True, status=Organisation.STATUS_APPROVED),
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


@register.filter
def can_manage(organisation, user):
    """Check if user can manage the organisation"""
    if not user or not user.is_authenticated:
        return False
    return organisation.can_user_manage(user)


@register.filter
def highlight_search(text, query):
    """Highlight search terms in text"""
    if not query or not text:
        return text
    
    import re
    from django.utils.safestring import mark_safe
    from django.utils.html import escape
    
    # Escape the text and query for safety
    escaped_text = escape(str(text))
    escaped_query = escape(str(query))
    
    # Create a case-insensitive regex pattern
    pattern = re.compile(re.escape(escaped_query), re.IGNORECASE)
    
    # Replace matches with highlighted version
    highlighted = pattern.sub(
        f'<mark class="bg-warning bg-opacity-50">{escaped_query}</mark>',
        escaped_text
    )
    
    return mark_safe(highlighted)


@register.simple_tag(takes_context=True)
def search_results_summary(context):
    """Generate a search results summary message"""
    request = context.get('request')
    if not request:
        return ''
    
    query = request.GET.get('q', '')
    filters = []
    
    # Check for active filters
    if request.GET.get('organisation'):
        filters.append(f"organisation: {request.GET.get('organisation')}")
    if request.GET.get('topic'):
        filters.append(f"topic: {request.GET.get('topic')}")
    if request.GET.get('license'):
        filters.append(f"license: {request.GET.get('license')}")
    
    # Build summary message
    parts = []
    if query:
        parts.append(f'matching "{query}"')
    if filters:
        parts.append(f"filtered by {', '.join(filters)}")
    
    if parts:
        return f"Results {' and '.join(parts)}"
    return "All results"


@register.simple_tag
def distinct_formats(resources):
    """Get distinct formats from a list of resources"""
    seen_formats = set()
    distinct_resources = []
    
    for resource in resources:
        if resource.format and resource.format.title not in seen_formats:
            seen_formats.add(resource.format.title)
            distinct_resources.append(resource)
    
    return distinct_resources
