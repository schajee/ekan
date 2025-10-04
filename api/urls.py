from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Create a router and register our viewsets with it.
router = DefaultRouter()
router.register(r'datasets', views.DatasetViewSet)
router.register(r'organisations', views.OrganisationViewSet)
router.register(r'topics', views.TopicViewSet)
router.register(r'resources', views.ResourceViewSet)

# The API URLs are now determined automatically by the router.
urlpatterns = [
    path('v1/', include(router.urls)),
]