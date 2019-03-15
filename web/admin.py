from django.contrib import admin

# Register your models here.
from .models import Topic, Dataset, Resource, Organisation, License, Type, Format, Dataset_Topic


@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("title",)}


@admin.register(Type)
class TypeAdmin(admin.ModelAdmin):
    pass


@admin.register(Format)
class FormatAdmin(admin.ModelAdmin):
    pass


@admin.register(License)
class LicenseAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("title",)}


@admin.register(Resource)
class ResourceAdmin(admin.ModelAdmin):
    pass


@admin.register(Organisation)
class OrganisationAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("title",)}


class DatasetTopicInline(admin.TabularInline):
    model = Dataset_Topic
    extra = 1


@admin.register(Dataset)
class DatasetAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("title",)}
    inlines = (DatasetTopicInline,)