from django.shortcuts import get_object_or_404
from django.views.generic import ListView, DetailView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse, Http404
from django.db.models import Q
from django.conf import settings
from .models import Dataset, Organisation, Topic, Resource


class HomeView(TemplateView):
    """Homepage displaying featured datasets and topics"""
    template_name = 'home.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'featured_datasets': Dataset.objects.filter(is_published=True, is_featured=True)[:6],
            'topics': Topic.objects.filter(is_featured=True)[:9],
            'recent_datasets': Dataset.objects.filter(is_published=True).order_by('-created')[:8],
        })
        return context


class DatasetListView(ListView):
    """List all published datasets with search and filtering"""
    model = Dataset
    template_name = 'datasets/index.html'
    context_object_name = 'datasets'
    paginate_by = getattr(settings, 'EKAN_ITEMS_PER_PAGE', 20)
    
    def get_queryset(self):
        queryset = Dataset.objects.filter(is_published=True).order_by('-updated')
        
        # Search functionality
        query = self.request.GET.get('q')
        if query:
            queryset = queryset.filter(
                Q(title__icontains=query) | 
                Q(description__icontains=query) |
                Q(notes__icontains=query)
            )
        
        # Filter by organisation
        org_slug = self.request.GET.get('organisation')
        if org_slug:
            queryset = queryset.filter(organisation__slug=org_slug)
        
        # Filter by topic
        topic_slug = self.request.GET.get('topic')
        if topic_slug:
            queryset = queryset.filter(topics__slug=topic_slug)
        
        # Filter by license
        license_slug = self.request.GET.get('license')
        if license_slug:
            queryset = queryset.filter(license__slug=license_slug)
        
        return queryset.distinct()


class DatasetDetailView(DetailView):
    """Display a single dataset with its resources"""
    model = Dataset
    template_name = 'datasets/show.html'
    context_object_name = 'dataset'
    
    def get_queryset(self):
        return Dataset.objects.filter(is_published=True)


class ResourceDetailView(DetailView):
    """Display a single resource"""
    model = Resource
    template_name = 'resources/show.html'
    context_object_name = 'resource'
    
    def get_object(self):
        dataset_slug = self.kwargs.get('dataset_slug')
        resource_slug = self.kwargs.get('slug')
        return get_object_or_404(
            Resource,
            slug=resource_slug,
            dataset__slug=dataset_slug,
            dataset__is_published=True
        )
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add preview data if available
        if self.object.can_preview():
            try:
                context['preview_data'] = self.object.get_preview_data()
            except Exception:
                context['preview_data'] = None
        return context


class ResourcePreviewView(DetailView):
    """Display resource preview in a modal or separate view"""
    model = Resource
    template_name = 'resources/preview.html'
    context_object_name = 'resource'
    
    def get_object(self):
        dataset_slug = self.kwargs.get('dataset_slug')
        resource_slug = self.kwargs.get('slug')
        return get_object_or_404(
            Resource,
            slug=resource_slug,
            dataset__slug=dataset_slug,
            dataset__is_published=True
        )
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        max_rows = int(self.request.GET.get('rows', 100))
        context['preview_data'] = self.object.get_preview_data(max_rows=max_rows)
        context['max_rows'] = max_rows
        return context


class ResourceDownloadView(DetailView):
    """Handle resource downloads"""
    model = Resource
    
    def get(self, request, *args, **kwargs):
        resource = self.get_object()
        
        # Increment download count
        resource.download_count += 1
        resource.save(update_fields=['download_count'])
        
        if resource.file:
            # Serve uploaded file
            response = HttpResponse(resource.file.read(), content_type=resource.mimetype or 'application/octet-stream')
            response['Content-Disposition'] = f'attachment; filename="{resource.file.name}"'
            return response
        elif resource.url:
            # Redirect to external URL
            from django.shortcuts import redirect
            return redirect(resource.url)
        else:
            raise Http404("Resource file not found")


class OrganisationListView(ListView):
    """List all active organisations"""
    model = Organisation
    template_name = 'organisations/index.html'
    context_object_name = 'organisations'
    paginate_by = getattr(settings, 'EKAN_ITEMS_PER_PAGE', 20)
    
    def get_queryset(self):
        return Organisation.objects.filter(is_active=True).order_by('title')


class OrganisationDetailView(DetailView):
    """Display an organisation with its datasets"""
    model = Organisation
    template_name = 'organisations/show.html'
    context_object_name = 'organisation'
    
    def get_queryset(self):
        return Organisation.objects.filter(is_active=True)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['datasets'] = self.object.datasets.filter(is_published=True).order_by('-updated')
        return context


class TopicListView(ListView):
    """List all topics"""
    model = Topic
    template_name = 'topics/index.html'
    context_object_name = 'topics'
    
    def get_queryset(self):
        return Topic.objects.all().order_by('title')


class TopicDetailView(DetailView):
    """Display a topic with its datasets"""
    model = Topic
    template_name = 'topics/show.html'
    context_object_name = 'topic'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['datasets'] = self.object.datasets.filter(is_published=True).order_by('-updated')
        return context


# Static page views
class AboutView(TemplateView):
    template_name = 'pages/about.html'


class ContactView(TemplateView):
    template_name = 'pages/contact.html'


class PrivacyView(TemplateView):
    template_name = 'pages/privacy.html'


class TermsView(TemplateView):
    template_name = 'pages/terms.html'


class FAQsView(TemplateView):
    template_name = 'pages/faqs.html'


class PageView(TemplateView):
    """Generic page view for handling page slugs"""
    
    def get_template_names(self):
        slug = self.kwargs.get('slug')
        return [f'pages/{slug}.html']


class AccountView(LoginRequiredMixin, TemplateView):
    """Account management view"""
    template_name = 'account/index.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page'] = self.kwargs.get('page', 'account')
        return context


class DebugView(TemplateView):
    """Debug view to test static file serving"""
    template_name = 'debug.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'static_url': settings.STATIC_URL,
            'media_url': settings.MEDIA_URL,
            'debug': settings.DEBUG,
            'request_path': self.request.path,
        })
        return context
