from django.contrib import admin
from django.utils.html import format_html
from .models import Organisation, License, Topic, Dataset, Format, Resource


@admin.register(Organisation)
class OrganisationAdmin(admin.ModelAdmin):
    list_display = ['title', 'status_badge', 'requested_by', 'manager', 'is_active', 'dataset_count', 'user_count', 'created']
    list_filter = ['status', 'is_active', 'created']
    search_fields = ['title', 'description', 'requested_by__username', 'requested_by__email']
    readonly_fields = ['created', 'updated', 'slug']
    filter_horizontal = ['users']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'slug', 'description', 'url', 'logo')
        }),
        ('Management', {
            'fields': ('manager', 'users', 'is_active')
        }),
        ('Request Information', {
            'fields': ('status', 'requested_by', 'approved_by', 'approval_date', 'rejection_reason'),
            'classes': ['collapse']
        }),
        ('Timestamps', {
            'fields': ('created', 'updated'),
            'classes': ['collapse']
        }),
    )
    
    def status_badge(self, obj):
        colors = {
            'pending': 'warning',
            'approved': 'success', 
            'rejected': 'danger'
        }
        color = colors.get(obj.status, 'secondary')
        return format_html(
            '<span class="badge bg-{}">{}</span>',
            color,
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'
    
    def dataset_count(self, obj):
        return obj.datasets.count() if hasattr(obj, 'datasets') else 0
    dataset_count.short_description = 'Datasets'
    
    def user_count(self, obj):
        return obj.users.count()
    user_count.short_description = 'Users'
    
    actions = ['approve_organizations', 'reject_organizations']
    
    def approve_organizations(self, request, queryset):
        for org in queryset.filter(status=Organisation.STATUS_PENDING):
            org.approve(request.user)
        self.message_user(request, f"Approved {queryset.count()} organizations.")
    approve_organizations.short_description = "Approve selected organizations"
    
    def reject_organizations(self, request, queryset):
        for org in queryset.filter(status=Organisation.STATUS_PENDING):
            org.reject(request.user, "Rejected via admin action")
        self.message_user(request, f"Rejected {queryset.count()} organizations.")
    reject_organizations.short_description = "Reject selected organizations"


@admin.register(License)
class LicenseAdmin(admin.ModelAdmin):
    list_display = ['title', 'is_open']
    list_filter = ['is_open']
    search_fields = ['title', 'description']


@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    list_display = ['title', 'color_display', 'is_featured', 'dataset_count']
    list_filter = ['is_featured']
    search_fields = ['title', 'description']
    
    def color_display(self, obj):
        return format_html(
            '<span style="background-color: {}; padding: 3px 8px; border-radius: 3px; color: white;">{}</span>',
            obj.color,
            obj.color
        )
    color_display.short_description = 'Color'
    
    def dataset_count(self, obj):
        return obj.datasets.count() if hasattr(obj, 'datasets') else 0
    dataset_count.short_description = 'Datasets'


@admin.register(Format)
class FormatAdmin(admin.ModelAdmin):
    list_display = ['title', 'color', 'mime_type', 'is_data_format']
    list_filter = ['color', 'is_data_format']
    search_fields = ['title', 'mime_type']


class ResourceInline(admin.TabularInline):
    model = Resource
    extra = 0
    fields = ['file', 'url', 'format']
    readonly_fields = []


@admin.register(Dataset)
class DatasetAdmin(admin.ModelAdmin):
    list_display = ['title', 'organisation', 'author', 'is_published', 'is_featured', 'resource_count', 'updated']
    list_filter = ['is_published', 'is_featured', 'organisation', 'topics', 'license']
    search_fields = ['title', 'description', 'notes']
    readonly_fields = ['created', 'updated', 'slug', 'resource_count']
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
            'fields': ('author', 'maintainer')
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
    
    def resource_count(self, obj):
        return obj.resources.count() if hasattr(obj, 'resources') else 0
    resource_count.short_description = 'Resources'


@admin.register(Resource)
class ResourceAdmin(admin.ModelAdmin):
    list_display = ['resource_name', 'dataset', 'format', 'created']
    list_filter = ['format', 'created']
    search_fields = ['dataset__title']
    readonly_fields = ['id', 'created', 'updated']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('id', 'dataset')
        }),
        ('File/URL', {
            'fields': ('file', 'url', 'format')
        }),
        ('Timestamps', {
            'fields': ('created', 'updated'),
            'classes': ['collapse']
        }),
    )
    
    def resource_name(self, obj):
        return obj.title
    resource_name.short_description = 'Name'
