from django.contrib import admin
from django.utils.html import format_html
from .models import Organisation, OrganisationMember, License, Topic, Dataset, Format, Resource


class OrganisationMemberInline(admin.TabularInline):
    model = OrganisationMember
    extra = 0
    fields = ['user', 'role', 'title', 'email', 'phone', 'is_public_contact', 'is_active']


@admin.register(Organisation)
class OrganisationAdmin(admin.ModelAdmin):
    list_display = ['title', 'status_badge', 'requested_by', 'manager', 'is_active', 'dataset_count', 'member_count', 'created']
    list_filter = ['status', 'is_active', 'created']
    search_fields = ['title', 'description', 'requested_by__username', 'requested_by__email']
    readonly_fields = ['created', 'updated', 'slug']
    inlines = [OrganisationMemberInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'slug', 'description', 'url', 'logo')
        }),
        ('Management', {
            'fields': ('manager', 'is_active')
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
    
    def member_count(self, obj):
        return obj.members.count() if hasattr(obj, 'members') else 0
    member_count.short_description = 'Members'
    
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


@admin.register(OrganisationMember)
class OrganisationMemberAdmin(admin.ModelAdmin):
    list_display = ['display_name', 'organisation', 'role_badge', 'title', 'is_public_contact', 'is_active', 'joined_date']
    list_filter = ['role', 'is_public_contact', 'is_active', 'organisation']
    search_fields = ['user__username', 'user__first_name', 'user__last_name', 'user__email', 'organisation__title', 'title']
    readonly_fields = ['joined_date']
    
    fieldsets = (
        ('Member Information', {
            'fields': ('organisation', 'user', 'role', 'title')
        }),
        ('Contact Information', {
            'fields': ('email', 'phone', 'is_public_contact')
        }),
        ('Status', {
            'fields': ('is_active', 'joined_date')
        }),
    )
    
    def display_name(self, obj):
        return obj.display_name
    display_name.short_description = 'Name'
    
    def role_badge(self, obj):
        colors = {
            'admin': 'danger',
            'manager': 'primary',
            'coordinator': 'info',
            'editor': 'success',
            'analyst': 'warning',
            'viewer': 'secondary'
        }
        color = colors.get(obj.role, 'secondary')
        return format_html(
            '<span class="badge bg-{}">{}</span>',
            color,
            obj.get_role_display()
        )
    role_badge.short_description = 'Role'


@admin.register(License)
class LicenseAdmin(admin.ModelAdmin):
    list_display = ['title', 'is_open', 'icon']
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
    list_display = ['title', 'mime_type', 'is_data_format', 'icon']
    list_filter = ['is_data_format']
    search_fields = ['title', 'mime_type']


class ResourceInline(admin.TabularInline):
    model = Resource
    extra = 0
    fields = ['title', 'file', 'url', 'format']
    readonly_fields = ['slug']


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
    
    def resource_count(self, obj):
        return obj.resources.count() if hasattr(obj, 'resources') else 0
    resource_count.short_description = 'Resources'


@admin.register(Resource)
class ResourceAdmin(admin.ModelAdmin):
    list_display = ['title', 'dataset', 'format', 'created']
    list_filter = ['format', 'created']
    search_fields = ['title', 'description', 'dataset__title']
    readonly_fields = ['slug', 'created', 'updated']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'slug', 'description', 'dataset')
        }),
        ('File/URL', {
            'fields': ('file', 'url', 'format')
        }),
        ('Timestamps', {
            'fields': ('created', 'updated'),
            'classes': ['collapse']
        }),
    )
