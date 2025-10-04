from django.contrib import admin
from django.utils.html import format_html
from .models import Organisation, License, Topic, Dataset, Format, Resource


@admin.register(Organisation)
class OrganisationAdmin(admin.ModelAdmin):
    list_display = ['title', 'manager', 'is_active', 'dataset_count', 'created']
    list_filter = ['is_active', 'created']
    search_fields = ['title', 'description']
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ['created', 'updated']
    
    def dataset_count(self, obj):
        return obj.datasets.count()
    dataset_count.short_description = 'Datasets'


@admin.register(License)
class LicenseAdmin(admin.ModelAdmin):
    list_display = ['title', 'is_open', 'icon']
    list_filter = ['is_open']
    search_fields = ['title', 'description']
    prepopulated_fields = {'slug': ('title',)}


@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    list_display = ['title', 'color_display', 'is_featured', 'dataset_count']
    list_filter = ['is_featured']
    search_fields = ['title', 'description']
    prepopulated_fields = {'slug': ('title',)}
    
    def color_display(self, obj):
        return format_html(
            '<span style="background-color: {}; padding: 3px 8px; border-radius: 3px; color: white;">{}</span>',
            obj.color,
            obj.color
        )
    color_display.short_description = 'Color'
    
    def dataset_count(self, obj):
        return obj.datasets.count()
    dataset_count.short_description = 'Datasets'


@admin.register(Format)
class FormatAdmin(admin.ModelAdmin):
    list_display = ['title', 'mime_type', 'is_data_format', 'icon']
    list_filter = ['is_data_format']
    search_fields = ['title', 'mime_type']
    prepopulated_fields = {'slug': ('title',)}


class ResourceInline(admin.TabularInline):
    model = Resource
    extra = 0
    fields = ['title', 'file', 'url', 'format', 'size']
    readonly_fields = ['slug', 'size', 'mimetype']


@admin.register(Dataset)
class DatasetAdmin(admin.ModelAdmin):
    list_display = ['title', 'organisation', 'author', 'is_published', 'is_featured', 'resource_count', 'updated']
    list_filter = ['is_published', 'is_featured', 'organisation', 'topics', 'license']
    search_fields = ['title', 'description', 'notes']
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ['created', 'updated', 'resource_count']
    filter_horizontal = ['topics']
    inlines = [ResourceInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'slug', 'description', 'notes')
        }),
        ('Organisation & Classification', {
            'fields': ('organisation', 'topics', 'license')
        }),
        ('Metadata', {
            'fields': ('author', 'maintainer_name', 'maintainer_email')
        }),
        ('Publishing', {
            'fields': ('is_published', 'is_featured', 'published_date')
        }),
        ('Timestamps', {
            'fields': ('created', 'updated'),
            'classes': ['collapse']
        }),
    )
    
    def save_model(self, request, obj, form, change):
        if not change:  # Creating new object
            obj.author = request.user
        super().save_model(request, obj, form, change)


@admin.register(Resource)
class ResourceAdmin(admin.ModelAdmin):
    list_display = ['title', 'dataset', 'format', 'file_size_human', 'download_count', 'created']
    list_filter = ['format', 'is_preview_available', 'created']
    search_fields = ['title', 'description', 'dataset__title']
    readonly_fields = ['slug', 'size', 'mimetype', 'download_count', 'file_size_human', 
                      'is_file_upload', 'is_external_url', 'created', 'updated']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'slug', 'description', 'dataset')
        }),
        ('File/URL', {
            'fields': ('file', 'url', 'format')
        }),
        ('Metadata', {
            'fields': ('size', 'file_size_human', 'mimetype', 'encoding', 'is_preview_available')
        }),
        ('Statistics', {
            'fields': ('download_count', 'is_file_upload', 'is_external_url')
        }),
        ('Timestamps', {
            'fields': ('created', 'updated'),
            'classes': ['collapse']
        }),
    )


# Customize the admin site
admin.site.site_header = "EKAN Administration"
admin.site.site_title = "EKAN Admin"
admin.site.index_title = "Welcome to EKAN Administration"
