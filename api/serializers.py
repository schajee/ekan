from rest_framework import serializers
from app.models import Dataset, Organisation, Topic, Resource, License, Format


class LicenseSerializer(serializers.ModelSerializer):
    class Meta:
        model = License
        fields = ['id', 'title', 'slug', 'description', 'url', 'icon', 'is_open']


class FormatSerializer(serializers.ModelSerializer):
    class Meta:
        model = Format
        fields = ['id', 'title', 'slug', 'description', 'icon', 'mime_type', 'is_data_format']


class TopicSerializer(serializers.ModelSerializer):
    dataset_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Topic
        fields = ['id', 'title', 'slug', 'description', 'icon', 'color', 'is_featured', 'dataset_count']
    
    def get_dataset_count(self, obj):
        return obj.datasets.filter(is_published=True).count()


class OrganisationSerializer(serializers.ModelSerializer):
    dataset_count = serializers.SerializerMethodField()
    manager_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Organisation
        fields = ['id', 'title', 'slug', 'description', 'url', 'logo', 'manager_name', 
                 'is_active', 'created', 'updated', 'dataset_count']
    
    def get_dataset_count(self, obj):
        return obj.datasets.filter(is_published=True).count()
    
    def get_manager_name(self, obj):
        return obj.manager.get_full_name() if obj.manager else None


class ResourceSerializer(serializers.ModelSerializer):
    format_details = FormatSerializer(source='format', read_only=True)
    file_size_human = serializers.ReadOnlyField()
    is_file_upload = serializers.ReadOnlyField()
    is_external_url = serializers.ReadOnlyField()
    download_url = serializers.SerializerMethodField()
    
    class Meta:
        model = Resource
        fields = ['id', 'title', 'slug', 'description', 'file', 'url', 'size', 
                 'file_size_human', 'mimetype', 'encoding', 'format_details',
                 'is_preview_available', 'download_count', 'is_file_upload', 
                 'is_external_url', 'download_url', 'created', 'updated']
    
    def get_download_url(self, obj):
        request = self.context.get('request')
        if request:
            from django.urls import reverse
            return request.build_absolute_uri(
                reverse('app:resource_download', kwargs={'slug': obj.slug})
            )
        return None


class DatasetSerializer(serializers.ModelSerializer):
    organisation_details = OrganisationSerializer(source='organisation', read_only=True)
    topics_details = TopicSerializer(source='topics', many=True, read_only=True)
    license_details = LicenseSerializer(source='license', read_only=True)
    resources = ResourceSerializer(many=True, read_only=True)
    resource_count = serializers.ReadOnlyField()
    author_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Dataset
        fields = ['id', 'title', 'slug', 'description', 'notes', 'organisation', 
                 'organisation_details', 'topics', 'topics_details', 'license', 
                 'license_details', 'author_name', 'maintainer_name', 'maintainer_email',
                 'is_published', 'is_featured', 'resource_count', 'resources',
                 'created', 'updated', 'published_date']
    
    def get_author_name(self, obj):
        return obj.author.get_full_name() if obj.author else obj.author.username