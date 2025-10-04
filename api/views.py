from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from django_filters.rest_framework import DjangoFilterBackend
from .serializers import DatasetSerializer, OrganisationSerializer, TopicSerializer, ResourceSerializer
from app.models import Dataset, Organisation, Topic, Resource


class DatasetViewSet(viewsets.ModelViewSet):
    """
    API endpoint for datasets.
    Only published datasets are visible to anonymous users.
    Only staff can create/update datasets.
    """
    queryset = Dataset.objects.all()
    serializer_class = DatasetSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['organisation', 'topics', 'license', 'is_featured']
    search_fields = ['title', 'description', 'notes']
    ordering_fields = ['created', 'updated', 'title']
    ordering = ['-updated']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        if not self.request.user.is_staff:
            queryset = queryset.filter(is_published=True)
        return queryset


class OrganisationViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for organisations.
    Read-only for all users.
    """
    queryset = Organisation.objects.filter(is_active=True)
    serializer_class = OrganisationSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'description']
    ordering_fields = ['title', 'created']
    ordering = ['title']


class TopicViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for topics.
    Read-only for all users.
    """
    queryset = Topic.objects.all()
    serializer_class = TopicSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'description']
    ordering_fields = ['title']
    ordering = ['title']


class ResourceViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for resources.
    Read-only for all users.
    Only resources from published datasets are visible.
    """
    queryset = Resource.objects.filter(dataset__is_published=True)
    serializer_class = ResourceSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['dataset', 'format']
    search_fields = ['title', 'description']
    ordering_fields = ['created', 'updated', 'title']
    ordering = ['-updated']
