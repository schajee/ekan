from django.shortcuts import get_object_or_404, render
from django.views.generic import ListView, DetailView, TemplateView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.admin.views.decorators import staff_member_required
from django.utils.decorators import method_decorator
from django.contrib import messages
from django.urls import reverse
from django.http import HttpResponse, Http404
from django.db.models import Q
from django.conf import settings
from .models import Dataset, Organisation, Topic, Resource
from .forms import OrganisationRegistrationForm
from .mixins import (
    EKANMetaMixin, DatasetMetaMixin, OrganisationMetaMixin, 
    ResourceMetaMixin, TopicMetaMixin
)


class HomeView(EKANMetaMixin, TemplateView):
    """Homepage displaying featured datasets and topics"""
    template_name = 'home.html'
    
    meta_title = 'EKAN - Open Data Portal'
    meta_description = 'Open government data portal providing access to datasets, resources, and information that drive transparency, innovation, and informed decision-making.'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'featured_datasets': Dataset.objects.filter(is_published=True, is_featured=True)[:6],
            'topics': Topic.objects.filter(is_featured=True)[:9],
            'recent_datasets': Dataset.objects.filter(is_published=True).order_by('-created')[:8],
        })
        return context


class DatasetListView(DatasetMetaMixin, ListView):
    """List all published datasets with search and filtering"""
    model = Dataset
    template_name = 'datasets/index.html'
    context_object_name = 'datasets'
    paginate_by = getattr(settings, 'EKAN_ITEMS_PER_PAGE', 20)
    
    meta_title = 'Datasets | EKAN'
    meta_description = 'Browse and download open government datasets across various categories and organizations.'
    
    def get_queryset(self):
        queryset = Dataset.objects.filter(is_published=True).order_by('-updated')
        
        # Search functionality - search across multiple fields
        query = self.request.GET.get('q')
        if query:
            queryset = queryset.filter(
                Q(title__icontains=query) | 
                Q(description__icontains=query) |
                Q(notes__icontains=query) |
                Q(organisation__title__icontains=query) |
                Q(topics__title__icontains=query) |
                Q(resources__title__icontains=query) |
                Q(resources__description__icontains=query)
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


class DatasetDetailView(DatasetMetaMixin, DetailView):
    """Display a single dataset with its resources"""
    model = Dataset
    template_name = 'datasets/show.html'
    context_object_name = 'dataset'
    
    def get_queryset(self):
        return Dataset.objects.filter(is_published=True)


class ResourceDetailView(ResourceMetaMixin, DetailView):
    """Display a single resource"""
    model = Resource
    template_name = 'resources/show.html'
    context_object_name = 'resource'
    
    def get_object(self):
        resource_slug = self.kwargs.get('slug')
        return get_object_or_404(
            Resource,
            slug=resource_slug,
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
        
        # Add related resources (other resources from the same dataset)
        context['related_resources'] = self.object.dataset.resources.exclude(
            id=self.object.id
        ).order_by('-updated')[:5]
        
        return context


class ResourcePreviewView(DetailView):
    """Display resource preview in a modal or separate view"""
    model = Resource
    template_name = 'resources/preview.html'
    context_object_name = 'resource'
    
    def get_object(self):
        resource_slug = self.kwargs.get('slug')
        return get_object_or_404(
            Resource,
            slug=resource_slug,
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


class OrganisationListView(OrganisationMetaMixin, ListView):
    """List all active organisations with search"""
    model = Organisation
    template_name = 'organisations/index.html'
    context_object_name = 'organisations'
    paginate_by = getattr(settings, 'EKAN_ITEMS_PER_PAGE', 20)
    
    meta_title = 'Organizations | EKAN'
    meta_description = 'Browse government organizations and their published datasets on the EKAN open data portal.'
    
    def get_queryset(self):
        queryset = Organisation.objects.filter(
            is_active=True, 
            status=Organisation.STATUS_APPROVED
        ).order_by('title')
        
        # Search functionality
        query = self.request.GET.get('q')
        if query:
            queryset = queryset.filter(
                Q(title__icontains=query) | 
                Q(description__icontains=query)
            )
        
        return queryset.distinct()


class OrganisationDetailView(OrganisationMetaMixin, DetailView):
    """Display an organisation with its datasets"""
    model = Organisation
    template_name = 'organisations/show.html'
    context_object_name = 'organisation'
    
    def get_queryset(self):
        return Organisation.objects.filter(
            is_active=True, 
            status=Organisation.STATUS_APPROVED
        )
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        organisation = self.object
        
        # Get published datasets
        datasets = organisation.datasets.filter(is_published=True).order_by('-updated')
        
        # Statistics
        context.update({
            'datasets': datasets,
            'dataset_count': organisation.dataset_count,
            'resource_count': organisation.resource_count,
            'active_members': organisation.active_members,
            'public_contacts': organisation.public_contacts,
            'recent_datasets': datasets[:5],  # For statistics tab
        })
        return context


class TopicListView(TopicMetaMixin, ListView):
    """List all topics with search"""
    model = Topic
    template_name = 'topics/index.html'
    context_object_name = 'topics'
    paginate_by = getattr(settings, 'EKAN_ITEMS_PER_PAGE', 20)
    
    meta_title = 'Topics | EKAN'
    meta_description = 'Browse datasets by topic category to find data related to specific themes and subjects.'
    
    def get_queryset(self):
        queryset = Topic.objects.all().order_by('title')
        
        # Search functionality
        query = self.request.GET.get('q')
        if query:
            queryset = queryset.filter(
                Q(title__icontains=query) | 
                Q(description__icontains=query)
            )
        
        return queryset.distinct()


class TopicDetailView(TopicMetaMixin, DetailView):
    """Display a topic with its datasets"""
    model = Topic
    template_name = 'topics/show.html'
    context_object_name = 'topic'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['datasets'] = self.object.datasets.filter(is_published=True).order_by('-updated')
        return context


# Static page views
class AboutView(EKANMetaMixin, TemplateView):
    template_name = 'pages/about.html'
    
    meta_title = 'About | EKAN'
    meta_description = 'Learn about EKAN (Easy Knowledge Archive Network), a comprehensive open data portal designed to make government and public data accessible, discoverable, and usable for everyone.'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_datasets'] = Dataset.objects.filter(is_published=True).count()
        context['total_organisations'] = Organisation.objects.filter(status='approved').count()
        context['total_resources'] = Resource.objects.filter(dataset__is_published=True).count()
        context['total_topics'] = Topic.objects.count()
        return context


class ContactView(EKANMetaMixin, TemplateView):
    template_name = 'pages/contact.html'
    
    meta_title = 'Contact | EKAN'
    meta_description = 'Get in touch with the EKAN team for support, questions, or feedback about our open data portal.'


class PrivacyView(EKANMetaMixin, TemplateView):
    template_name = 'pages/privacy.html'
    
    meta_title = 'Privacy Policy | EKAN'
    meta_description = 'Learn about EKAN\'s privacy policy and how we protect your personal information while using our open data portal.'


class TermsView(EKANMetaMixin, TemplateView):
    template_name = 'pages/terms.html'
    
    meta_title = 'Terms of Use | EKAN'
    meta_description = 'Read the terms of use for the EKAN open data portal, including usage rights and responsibilities.'


class FAQsView(EKANMetaMixin, TemplateView):
    template_name = 'pages/faqs.html'
    
    meta_title = 'Frequently Asked Questions | EKAN'
    meta_description = 'Find answers to commonly asked questions about the EKAN open data portal, datasets, and how to use our platform.'


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


class OrganisationRegistrationView(LoginRequiredMixin, CreateView):
    """View for users to register new organisations"""
    model = Organisation
    form_class = OrganisationRegistrationForm
    template_name = 'organisations/register.html'
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs
    
    def form_valid(self, form):
        messages.success(
            self.request, 
            'Your organization request has been submitted successfully! '
            'An administrator will review it shortly.'
        )
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse('app:organisation_request_success')


class OrganisationRequestSuccessView(LoginRequiredMixin, TemplateView):
    """Success page after submitting organization request"""
    template_name = 'organisations/request_success.html'
