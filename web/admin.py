from django.contrib import admin

# Register your models here.
from . import models, forms

@admin.register(models.Topic)
class TopicAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("title",)}


@admin.register(models.Format)
class FormatAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("title",)}


@admin.register(models.License)
class LicenseAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("title",)}


@admin.register(models.Resource)
class ResourceAdmin(admin.ModelAdmin):
    pass


@admin.register(models.Organisation)
class OrganisationAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("title",)}


class DatasetTopicInline(admin.TabularInline):
    model = models.Dataset_Topic
    extra = 1


@admin.register(models.Dataset)
class DatasetAdmin(admin.ModelAdmin):
    form = forms.DatasetForm
    prepopulated_fields = {"slug": ("title",)}
    inlines = (DatasetTopicInline,)

    def get_form(self, request, *args, **kwargs):
        form = super(DatasetAdmin, self).get_form(request, *args, **kwargs)
        form.current_user = request.user
        return form
