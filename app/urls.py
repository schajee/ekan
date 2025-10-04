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
    
    # Resources  
    path('datasets/<slug:dataset_slug>/resources/<slug:slug>/', 
         views.ResourceDetailView.as_view(), name='resource'),
    path('datasets/<slug:dataset_slug>/resources/<slug:slug>/preview/', 
         views.ResourcePreviewView.as_view(), name='resource_preview'),
    path('resources/<slug:slug>/download/', 
         views.ResourceDownloadView.as_view(), name='resource_download'),
    
    # Organisations
    path('organisations/', views.OrganisationListView.as_view(), name='organisations'),
    path('organisations/<slug:slug>/', views.OrganisationDetailView.as_view(), name='organisation'),
    
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
    
    # Email verification (for old templates)
    path('verify/<int:uid>/<str:token>/', views.VerifyView.as_view(), name='verify'),
    
    # Static pages (using slug parameter for compatibility)
    path('about/', views.AboutView.as_view(), name='about'),
    path('contact/', views.ContactView.as_view(), name='contact'),
    path('privacy/', views.PrivacyView.as_view(), name='privacy'),
    path('terms/', views.TermsView.as_view(), name='terms'),
    path('faqs/', views.FAQsView.as_view(), name='faqs'),
    
    # Debug endpoint (only in DEBUG mode)
    path('debug/', views.DebugView.as_view(), name='debug'),
    
    # Generic page handler for template compatibility (keep last)
    path('<str:slug>/', views.PageView.as_view(), name='page'),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) \
  + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)