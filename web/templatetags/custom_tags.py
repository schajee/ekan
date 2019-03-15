from django import template
from web.models import Dataset, Organisation, Topic, Format, License
from django.contrib.auth.models import User

register = template.Library()


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
