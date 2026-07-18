from django.shortcuts import get_object_or_404, render, redirect
from django.views.generic import ListView, DetailView, TemplateView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.admin.views.decorators import staff_member_required
from django.utils.decorators import method_decorator
from django.contrib import messages
from django.urls import reverse
from django.http import HttpResponse, Http404
from django.db.models import Q
from django.conf import settings
from django.core.exceptions import PermissionDenied
from .models import Dataset, Organisation, Topic, Resource
from .forms import OrganisationRegistrationForm, OrganisationEditForm, DatasetForm, ResourceForm
from .mixins import (
    EKANMetaMixin, DatasetMetaMixin, OrganisationMetaMixin, 
    ResourceMetaMixin, TopicMetaMixin
)


class ResourcePermissionMixin:
    """Mixin to handle resource permissions for published/unpublished datasets"""
    
    def get_resource_with_permissions(self, dataset_slug, resource_uuid):
        """Get resource and check permissions for unpublished datasets"""
        resource = get_object_or_404(
            Resource,
            id=resource_uuid,
            dataset__slug=dataset_slug
        )
        
        # Check if user can access this resource
        if not resource.dataset.is_published:
            if self.request.user.is_authenticated:
                # Allow access if user is author, organization member, or superuser
                if (resource.dataset.author == self.request.user or 
                    resource.dataset.organisation.can_user_manage(self.request.user) or
                    self.request.user.is_superuser):
                    return resource
            # If not authorized, return 404
            raise Http404("Resource not found")
        
        return resource


class HomeView(EKANMetaMixin, TemplateView):
    """Homepage displaying featured datasets and topics"""
    template_name = 'home.html'
    
    meta_title = 'EKAN - Open Data Portal'
    meta_description = 'Open government data portal providing access to datasets, resources, and information that drive transparency, innovation, and informed decision-making.'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'featured_datasets': Dataset.objects.filter(is_published=True, is_featured=True)[:12],
            'topics': Topic.objects.filter(is_featured=True)[:12],
            'recent_datasets': Dataset.objects.filter(is_published=True).order_by('-created')[:12],
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
        # Show all published datasets, plus unpublished ones for authorized users
        if self.request.user.is_authenticated:
            return Dataset.objects.all()
        else:
            return Dataset.objects.filter(is_published=True)
    
    def get_object(self):
        """Get dataset and check permissions for unpublished datasets"""
        obj = super().get_object()
        
        # If dataset is not published, check if user has permission to view it
        if not obj.is_published and self.request.user.is_authenticated:
            # Allow access if user is author, organization member, or superuser
            if (obj.author == self.request.user or 
                obj.organisation.can_user_manage(self.request.user) or
                self.request.user.is_superuser):
                return obj
            else:
                from django.http import Http404
                raise Http404("Dataset not found")
        elif not obj.is_published:
            # Anonymous users cannot see unpublished datasets
            from django.http import Http404
            raise Http404("Dataset not found")
        
        return obj
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        dataset = self.object
        
        # Add user permission context
        context['user_can_manage'] = dataset.organisation.can_user_manage(self.request.user)
        
        return context


class ResourceDetailView(ResourcePermissionMixin, ResourceMetaMixin, DetailView):
    """Display a single resource"""
    model = Resource
    template_name = 'resources/show.html'
    context_object_name = 'resource'
    
    def get_object(self):
        dataset_slug = self.kwargs.get('dataset_slug')
        resource_uuid = self.kwargs.get('uuid')
        return self.get_resource_with_permissions(dataset_slug, resource_uuid)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        resource = self.object
        
        # Add user permission context
        context['user_can_manage'] = resource.dataset.organisation.can_user_manage(self.request.user)
        
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
        dataset_slug = self.kwargs.get('dataset_slug')
        resource_uuid = self.kwargs.get('uuid')
        return get_object_or_404(
            Resource,
            id=resource_uuid,
            dataset__slug=dataset_slug,
            dataset__is_published=True
        )
    
    def dispatch(self, request, *args, **kwargs):
        """Redirect URL-based resources to detail page since they can't be previewed"""
        resource = self.get_object()
        if not resource.file and resource.url:
            from django.shortcuts import redirect
            return redirect('app:resource', dataset_slug=resource.dataset.slug, uuid=resource.id)
        return super().dispatch(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        max_rows = int(self.request.GET.get('rows', 100))
        context['preview_data'] = self.object.get_preview_data(max_rows=max_rows)
        context['max_rows'] = max_rows
        return context


class ResourceDownloadView(DetailView):
    """Handle resource downloads"""
    model = Resource
    
    def get_object(self):
        dataset_slug = self.kwargs.get('dataset_slug')
        resource_uuid = self.kwargs.get('uuid')
        return get_object_or_404(
            Resource,
            id=resource_uuid,
            dataset__slug=dataset_slug,
            dataset__is_published=True
        )
    
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
    paginate_by = 12
    
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
        
        # Get recent resources from published datasets
        from app.models import Resource
        recent_resources = Resource.objects.filter(
            dataset__organisation=organisation,
            dataset__is_published=True
        ).order_by('-updated')[:6]
        
        # Statistics
        context.update({
            'datasets': datasets,
            'dataset_count': organisation.dataset_count,
            'resource_count': organisation.resource_count,
            'recent_datasets': datasets[:4],  # For statistics tab
            'recent_resources': recent_resources,
            'user_can_manage': organisation.can_user_manage(self.request.user),
        })
        return context


class OrganisationDatasetListView(ListView):
    """List all datasets for a specific organisation"""
    model = Dataset
    template_name = 'organisations/datasets.html'
    context_object_name = 'datasets'
    paginate_by = 20
    
    def get_organisation(self):
        return get_object_or_404(
            Organisation,
            slug=self.kwargs['slug'],
            is_active=True,
            status=Organisation.STATUS_APPROVED
        )
    
    def get_queryset(self):
        self.organisation = self.get_organisation()
        queryset = self.organisation.datasets.all()
        
        # If user is not authorized, only show published datasets
        if not (self.request.user.is_authenticated and 
                (self.organisation.can_user_manage(self.request.user) or 
                 self.request.user.is_superuser)):
            queryset = queryset.filter(is_published=True)
        
        return queryset.order_by('-updated')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['organisation'] = self.organisation
        context['user_can_manage'] = self.organisation.can_user_manage(self.request.user)
        
        # Count published vs unpublished for authorized users
        if self.request.user.is_authenticated:
            context['published_count'] = self.organisation.datasets.filter(is_published=True).count()
            context['unpublished_count'] = self.organisation.datasets.filter(is_published=False).count()
        
        return context


class TopicListView(TopicMetaMixin, ListView):
    """List all topics with search"""
    model = Topic
    template_name = 'topics/index.html'
    context_object_name = 'topics'
    paginate_by = 12
    
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


class OrganisationEditView(LoginRequiredMixin, UpdateView):
    """Edit existing organisation"""
    model = Organisation
    form_class = OrganisationEditForm
    template_name = 'organisations/edit.html'
    
    def dispatch(self, request, *args, **kwargs):
        # Check if user can edit this organization
        self.object = self.get_object()
        
        if not self.object.can_user_manage(request.user):
            messages.error(request, 'You do not have permission to edit this organization.')
            return redirect('app:organisation', slug=self.object.slug)
            
        return super().dispatch(request, *args, **kwargs)
    
    def get_success_url(self):
        messages.success(self.request, 'Organisation updated successfully!')
        return reverse('app:organisation', kwargs={'slug': self.object.slug})


# Dataset Management Views

class DatasetCreateView(LoginRequiredMixin, CreateView):
    """Create a new dataset for an organization"""
    model = Dataset
    form_class = DatasetForm
    template_name = 'datasets/create.html'
    
    def dispatch(self, request, *args, **kwargs):
        # Check if user is member of the organization
        self.organisation = get_object_or_404(Organisation, slug=kwargs['org_slug'])
        
        # Check if user can create datasets for this organization
        if not self.can_manage_organisation(request.user, self.organisation):
            messages.error(request, 'You do not have permission to create datasets for this organization.')
            return redirect('app:organisation', slug=self.organisation.slug)
        
        return super().dispatch(request, *args, **kwargs)
    
    def can_manage_organisation(self, user, organisation):
        """Check if user can manage this organisation"""
        return organisation.can_user_manage(user)
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        kwargs['organisation'] = self.organisation
        return kwargs
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['organisation'] = self.organisation
        return context
    
    def get_success_url(self):
        return reverse('app:dataset', kwargs={'slug': self.object.slug})


class DatasetUpdateView(LoginRequiredMixin, UpdateView):
    """Update an existing dataset"""
    model = Dataset
    form_class = DatasetForm
    template_name = 'datasets/edit.html'
    
    def dispatch(self, request, *args, **kwargs):
        # Check if user can edit this dataset
        dataset = self.get_object()
        
        if not self.can_edit_dataset(request.user, dataset):
            messages.error(request, 'You do not have permission to edit this dataset.')
            return redirect('app:dataset', slug=dataset.slug)
        
        return super().dispatch(request, *args, **kwargs)
    
    def can_edit_dataset(self, user, dataset):
        """Check if user can edit this dataset"""
        if user.is_superuser:
            return True
        
        # Dataset author can edit
        if dataset.author == user:
            return True
        
        # Organization manager or members can edit
        if dataset.organisation.can_user_manage(user):
            return True
        
        return False
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        kwargs['organisation'] = self.object.organisation
        return kwargs
    
    def get_success_url(self):
        return reverse('app:dataset', kwargs={'slug': self.object.slug})


class DatasetPublishView(LoginRequiredMixin, DetailView):
    """Publish an unpublished dataset"""
    model = Dataset
    
    def post(self, request, *args, **kwargs):
        dataset = self.get_object()
        
        # Check if user can publish this dataset
        if not self.can_publish_dataset(request.user, dataset):
            messages.error(request, 'You do not have permission to publish this dataset.')
            return redirect('app:dataset', slug=dataset.slug)
        
        # Check if dataset is already published
        if dataset.is_published:
            messages.info(request, 'This dataset is already published.')
            return redirect('app:dataset', slug=dataset.slug)
        
        # Publish the dataset
        dataset.is_published = True
        dataset.save()
        
        messages.success(request, f'Dataset "{dataset.title}" has been published successfully!')
        return redirect('app:dataset', slug=dataset.slug)
    
    def can_publish_dataset(self, user, dataset):
        """Check if user can publish this dataset"""
        if user.is_superuser:
            return True
        
        # Dataset author can publish
        if dataset.author == user:
            return True
        
        # Organization members who can manage can publish
        if dataset.organisation.can_user_manage(user):
            return True
        
        return False


class ResourceCreateView(LoginRequiredMixin, CreateView):
    """Add a new resource to a dataset"""
    model = Resource
    form_class = ResourceForm
    template_name = 'resources/create.html'
    
    def dispatch(self, request, *args, **kwargs):
        # Get the dataset
        self.dataset = get_object_or_404(Dataset, slug=kwargs['dataset_slug'])
        
        # Check if user can add resources to this dataset
        if not self.can_edit_dataset(request.user, self.dataset):
            messages.error(request, 'You do not have permission to add resources to this dataset.')
            return redirect('app:dataset', slug=self.dataset.slug)
        
        return super().dispatch(request, *args, **kwargs)
    
    def can_edit_dataset(self, user, dataset):
        """Check if user can edit this dataset"""
        if user.is_superuser:
            return True
        
        # Dataset author can edit
        if dataset.author == user:
            return True
        
        # Organization manager or members can edit
        if dataset.organisation.can_user_manage(user):
            return True
        
        return False
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['dataset'] = self.dataset
        return kwargs
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['dataset'] = self.dataset
        return context
    
    def get_success_url(self):
        return reverse('app:dataset', kwargs={'slug': self.dataset.slug})


class ResourceUpdateView(LoginRequiredMixin, UpdateView):
    """Update an existing resource"""
    model = Resource
    form_class = ResourceForm
    template_name = 'resources/edit.html'
    
    def get_object(self):
        dataset_slug = self.kwargs.get('dataset_slug')
        resource_uuid = self.kwargs.get('uuid')
        return get_object_or_404(
            Resource,
            id=resource_uuid,
            dataset__slug=dataset_slug
        )
    
    def dispatch(self, request, *args, **kwargs):
        # Check if user can edit this resource
        resource = self.get_object()
        
        if not self.can_edit_dataset(request.user, resource.dataset):
            messages.error(request, 'You do not have permission to edit this resource.')
            return redirect('app:resource', dataset_slug=resource.dataset.slug, uuid=resource.id)
        
        return super().dispatch(request, *args, **kwargs)
    
    def can_edit_dataset(self, user, dataset):
        """Check if user can edit this dataset"""
        if user.is_superuser:
            return True
        
        # Dataset author can edit
        if dataset.author == user:
            return True
        
        # Organization manager or members can edit
        if dataset.organisation.can_user_manage(user):
            return True
        
        return False
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['dataset'] = self.object.dataset
        return kwargs
    
    def get_success_url(self):
        return reverse('app:resource', kwargs={'dataset_slug': self.object.dataset.slug, 'uuid': self.object.id})


class DatasetDeleteView(LoginRequiredMixin, DeleteView):
    """Delete a dataset"""
    model = Dataset
    template_name = 'datasets/delete.html'
    context_object_name = 'dataset'
    
    def test_func(self):
        dataset = self.get_object()
        return (dataset.author == self.request.user or 
                dataset.organisation.can_user_manage(self.request.user) or
                self.request.user.is_superuser)
    
    def get_success_url(self):
        return reverse('app:organisation', kwargs={'slug': self.object.organisation.slug})


class ResourceDeleteView(LoginRequiredMixin, DeleteView):
    """Delete a resource"""
    model = Resource
    template_name = 'resources/delete.html'
    context_object_name = 'resource'
    
    def get_object(self):
        dataset_slug = self.kwargs.get('dataset_slug')
        resource_uuid = self.kwargs.get('uuid')
        return get_object_or_404(
            Resource,
            id=resource_uuid,
            dataset__slug=dataset_slug
        )
    
    def test_func(self):
        resource = self.get_object()
        return (resource.dataset.author == self.request.user or 
                resource.dataset.organisation.can_user_manage(self.request.user) or
                self.request.user.is_superuser)
    
    def get_success_url(self):
        return reverse('app:dataset', kwargs={'slug': self.object.dataset.slug})
