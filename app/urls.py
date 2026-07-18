from django.urls import path
from django.views.generic import RedirectView
from django.conf import settings
from django.conf.urls.static import static
from . import views

app_name = 'app'

urlpatterns = [
    # Home
    path('', views.HomeView.as_view(), name='home'),
    
    # Datasets
    path('datasets/', views.DatasetListView.as_view(), name='datasets'),
    path('datasets/<slug:slug>/', views.DatasetDetailView.as_view(), name='dataset'),
    path('datasets/<slug:slug>/edit/', views.DatasetUpdateView.as_view(), name='dataset_edit'),
    path('datasets/<slug:slug>/delete/', views.DatasetDeleteView.as_view(), name='dataset_delete'),
    path('datasets/<slug:slug>/publish/', views.DatasetPublishView.as_view(), name='dataset_publish'),
    
    # Dataset creation for organizations
    path('organisations/<slug:org_slug>/datasets/create/', views.DatasetCreateView.as_view(), name='dataset_create'),
    
    # Resources (nested under datasets)
    # Resource creation for datasets (must come before resource detail to avoid conflicts)
    path('datasets/<slug:dataset_slug>/resources/create/', views.ResourceCreateView.as_view(), name='resource_create'),
    
    path('datasets/<slug:dataset_slug>/resources/<uuid:uuid>/', views.ResourceDetailView.as_view(), name='resource'),
    path('datasets/<slug:dataset_slug>/resources/<uuid:uuid>/preview/', views.ResourcePreviewView.as_view(), name='resource_preview'),
    path('datasets/<slug:dataset_slug>/resources/<uuid:uuid>/download/', views.ResourceDownloadView.as_view(), name='resource_download'),
    path('datasets/<slug:dataset_slug>/resources/<uuid:uuid>/edit/', views.ResourceUpdateView.as_view(), name='resource_edit'),
    path('datasets/<slug:dataset_slug>/resources/<uuid:uuid>/delete/', views.ResourceDeleteView.as_view(), name='resource_delete'),
    
    # Organisations
    path('organisations/', views.OrganisationListView.as_view(), name='organisations'),
    path('organisations/register/', views.OrganisationRegistrationView.as_view(), name='organisation_register'),
    path('organisations/requests/success/', views.OrganisationRequestSuccessView.as_view(), name='organisation_request_success'),
    path('organisations/<slug:slug>/', views.OrganisationDetailView.as_view(), name='organisation'),
    path('organisations/<slug:slug>/edit/', views.OrganisationEditView.as_view(), name='organisation_edit'),
    path('organisations/<slug:slug>/datasets/', views.OrganisationDatasetListView.as_view(), name='organisation_datasets'),
    
    # Topics
    path('topics/', views.TopicListView.as_view(), name='topics'),
    path('topics/<slug:slug>/', views.TopicDetailView.as_view(), name='topic'),
    
    # Authentication redirects to allauth
    path('login/', RedirectView.as_view(pattern_name='account_login'), name='login'),
    path('signup/', RedirectView.as_view(pattern_name='account_signup'), name='signup'),
    path('logout/', RedirectView.as_view(pattern_name='account_logout'), name='logout'),
    
    # Account management (redirects to allauth for now)
    path('account/', RedirectView.as_view(pattern_name='account_profile'), name='account'),
    path('account/<str:page>/', views.AccountView.as_view(), name='account_page'),
    
    # Static pages (using slug parameter for compatibility)
    path('about/', views.AboutView.as_view(), name='about'),
    path('contact/', views.ContactView.as_view(), name='contact'),
    path('privacy/', views.PrivacyView.as_view(), name='privacy'),
    path('terms/', views.TermsView.as_view(), name='terms'),
    path('faqs/', views.FAQsView.as_view(), name='faqs'),
    
    # Debug endpoint (only in DEBUG mode)
    path('debug/', views.DebugView.as_view(), name='debug'),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) \
  + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)