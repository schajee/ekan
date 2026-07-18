import uuid
from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils.text import slugify
from django.utils import timezone


class Organisation(models.Model):
    """Government entities that publish datasets"""

    # Status choices for approval workflow
    STATUS_PENDING = "pending"
    STATUS_APPROVED = "approved"
    STATUS_REJECTED = "rejected"

    STATUS_CHOICES = [
        (STATUS_PENDING, "Pending Review"),
        (STATUS_APPROVED, "Approved"),
        (STATUS_REJECTED, "Rejected"),
    ]

    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, max_length=200)
    description = models.TextField(blank=True)
    url = models.URLField(blank=True, help_text="Official website URL")
    logo = models.ImageField(upload_to="organisations/", blank=True, null=True)
    manager = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        help_text="Staff member responsible for this organisation",
    )
    users = models.ManyToManyField(
        User,
        blank=True,
        related_name="organisations",
        help_text="Users who can create/edit datasets for this organisation",
    )

    # Registration workflow fields
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING
    )
    requested_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="organisation_requests",
        help_text="User who requested this organisation",
    )
    approved_by = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="approved_organisations",
        help_text="Admin who approved/rejected this request",
    )
    approval_date = models.DateTimeField(null=True, blank=True)
    rejection_reason = models.TextField(blank=True, help_text="Reason for rejection")

    is_active = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["title"]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("app:organisation", kwargs={"slug": self.slug})

    @property
    def is_approved(self):
        return self.status == self.STATUS_APPROVED

    @property
    def is_pending(self):
        return self.status == self.STATUS_PENDING

    @property
    def is_rejected(self):
        return self.status == self.STATUS_REJECTED

    def approve(self, approved_by_user):
        """Approve the organisation request"""
        self.status = self.STATUS_APPROVED
        self.approved_by = approved_by_user
        self.approval_date = timezone.now()
        self.save()

    def reject(self, rejected_by_user, reason=""):
        """Reject the organisation request"""
        self.status = self.STATUS_REJECTED
        self.approved_by = rejected_by_user
        self.approval_date = timezone.now()
        self.rejection_reason = reason
        self.save()

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    @property
    def dataset_count(self):
        """Get total number of published datasets"""
        return self.datasets.filter(is_published=True).count()

    @property
    def resource_count(self):
        """Get total number of resources across all datasets"""
        return sum(
            dataset.resource_count
            for dataset in self.datasets.filter(is_published=True)
        )

    @property
    def active_members(self):
        """Get active organization users (simplified)"""
        return self.users.all()

    @property
    def public_contacts(self):
        """Get manager as the primary contact"""
        from django.contrib.auth.models import User
        if self.manager:
            return User.objects.filter(id=self.manager.id)
        return User.objects.none()

    def can_user_manage(self, user):
        """Check if user can manage this organisation"""
        if not user.is_authenticated:
            return False
        if user.is_superuser:
            return True
        if self.manager == user:
            return True
        return self.users.filter(id=user.id).exists()


class License(models.Model):
    """Data licensing options (e.g., Public Domain, Creative Commons, etc.)"""

    title = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    url = models.URLField(blank=True, help_text="URL to license details")
    is_open = models.BooleanField(default=True, help_text="Is this an open license?")

    class Meta:
        ordering = ["title"]

    def __str__(self):
        return self.title


class Topic(models.Model):
    """Thematic classification for datasets (e.g., education, transport, health)"""

    title = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    color = models.CharField(
        max_length=7, default="#007bff", help_text="Hex color code for display"
    )
    is_featured = models.BooleanField(default=False)

    class Meta:
        ordering = ["title"]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("app:topic", kwargs={"slug": self.slug})

    @property
    def published_dataset_count(self):
        """Count of published datasets for this topic"""
        return self.datasets.filter(is_published=True).count()


class Dataset(models.Model):
    """Collection of related resources from an organisation"""

    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, max_length=200)
    description = models.TextField(help_text="Detailed description of the dataset")
    notes = models.TextField(blank=True, help_text="Additional notes or methodology")

    organisation = models.ForeignKey(
        Organisation, on_delete=models.CASCADE, related_name="datasets"
    )
    topics = models.ManyToManyField(Topic, blank=True, related_name="datasets")
    license = models.ForeignKey(
        License,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="datasets",
    )

    # Metadata
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="authored_datasets"
    )
    maintainer = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="maintained_datasets",
        help_text="User responsible for maintaining this dataset",
    )

    # Status
    is_published = models.BooleanField(default=False)
    is_featured = models.BooleanField(default=False)

    # Timestamps
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    published_date = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-updated"]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("app:dataset", kwargs={"slug": self.slug})

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    @property
    def resource_count(self):
        return self.resources.count()

    @property
    def last_resource_update(self):
        """Get the date of the most recently updated resource"""
        latest_resource = self.resources.order_by('-updated').first()
        if latest_resource:
            return max(self.updated, latest_resource.updated)
        return self.updated


class Format(models.Model):
    """File format types (e.g., CSV, JSON, PDF, XLSX)"""

    # Bootstrap badge color choices
    COLOR_CHOICES = [
        ('success', 'Green (Data/Spreadsheet)'),
        ('primary', 'Blue (Documents)'),
        ('danger', 'Red (PDF/Presentations)'),
        ('warning', 'Orange (Web/Markup)'),
        ('secondary', 'Gray (Other)'),
    ]

    title = models.CharField(max_length=50)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    mime_type = models.CharField(max_length=100, blank=True)
    color = models.CharField(
        max_length=20, 
        choices=COLOR_CHOICES, 
        default='secondary',
        help_text="Bootstrap badge color for this format"
    )
    is_data_format = models.BooleanField(
        default=True, help_text="Can this format be previewed/analyzed?"
    )

    class Meta:
        ordering = ["title"]

    def __str__(self):
        return self.title.upper()


class Resource(models.Model):
    """Individual files or URLs within a dataset"""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    dataset = models.ForeignKey(
        Dataset, on_delete=models.CASCADE, related_name="resources"
    )
    format = models.ForeignKey(
        Format,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="resources",
    )

    # File or URL
    file = models.FileField(upload_to="resources/%Y/%m/", blank=True, null=True)
    url = models.URLField(blank=True, help_text="External URL if not uploading a file")

    # Metadata
    size = models.BigIntegerField(null=True, blank=True, help_text="File size in bytes")
    mimetype = models.CharField(max_length=100, blank=True)
    encoding = models.CharField(max_length=50, blank=True)

    # Status
    is_preview_available = models.BooleanField(default=False)
    download_count = models.PositiveIntegerField(default=0)

    # Timestamps
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["created"]

    def __str__(self):
        return f"Resource {str(self.id)[:8]} - {self.dataset.title}"

    def get_absolute_url(self):
        return reverse("app:resource", kwargs={"dataset_slug": self.dataset.slug, "uuid": self.id})

    @property
    def title(self):
        """Return a meaningful title for the resource"""
        import os
        if self.file:
            return os.path.basename(self.file.name)
        elif self.url:
            return self.url
        else:
            return f"Resource {str(self.id)[:8]}"

    def clean(self):
        """Validate that either file or URL is provided"""
        from django.core.exceptions import ValidationError

        if not self.file and not self.url:
            raise ValidationError("Either a file upload or URL must be provided.")

        if self.file and self.url:
            raise ValidationError("Provide either a file upload OR a URL, not both.")

    def save(self, *args, **kwargs):
        # Auto-detect file size and mimetype
        if self.file and hasattr(self.file, "size"):
            self.size = self.file.size

        # Set preview availability based on format
        self.is_preview_available = self.can_preview()

        super().save(*args, **kwargs)

    def can_preview(self):
        """Check if this resource can be previewed"""
        if not self.format:
            return False

        previewable_formats = ["CSV", "XLSX", "XLS", "JSON", "XML", "TSV"]
        return self.format.title.upper() in previewable_formats

    def get_preview_data(self, max_rows=100):
        """Get preview data for supported file types"""
        import pandas as pd
        import json

        if not self.can_preview():
            return None

        # Only preview uploaded files, not URLs
        if not self.file:
            if self.url:
                return {
                    "type": "url_only",
                    "data": "This resource is available via URL. Visit the link to view the content.",
                    "url": self.url,
                }
            else:
                return {
                    "type": "error",
                    "data": "No file or URL available for this resource.",
                }

        # Handle file-based previews only
        try:
            file_path = self.file.path
            format_upper = self.format.title.upper() if self.format else ""

            if format_upper == "CSV":
                # Read CSV and use head() to limit rows
                df = pd.read_csv(file_path)
                df_preview = df.head(max_rows)
                return {
                    "type": "dataframe",
                    "data": df_preview.to_html(
                        classes="table table-striped table-hover",
                        table_id="preview-table",
                        escape=False,
                        border=0,
                        index=False,
                    ),
                    "shape": df.shape,
                    "preview_shape": df_preview.shape,
                    "columns": list(df.columns),
                }

            elif format_upper in ["XLSX", "XLS"]:
                # Read Excel and use head() to limit rows
                df = pd.read_excel(file_path)
                df_preview = df.head(max_rows)
                return {
                    "type": "dataframe",
                    "data": df_preview.to_html(
                        classes="table table-striped table-hover",
                        table_id="preview-table",
                        escape=False,
                        border=0,
                        index=False,
                    ),
                    "shape": df.shape,
                    "preview_shape": df_preview.shape,
                    "columns": list(df.columns),
                }

            elif format_upper == "JSON":
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)

                # If it's a list of records, try to convert to DataFrame
                if isinstance(data, list) and data and isinstance(data[0], dict):
                    df = pd.DataFrame(data)
                    df_preview = df.head(max_rows)
                    return {
                        "type": "dataframe",
                        "data": df_preview.to_html(
                            classes="table table-striped table-hover",
                            table_id="preview-table",
                            escape=False,
                            border=0,
                            index=False,
                        ),
                        "shape": df.shape,
                        "preview_shape": df_preview.shape,
                        "columns": list(df.columns),
                    }
                else:
                    # Just show formatted JSON
                    preview_data = (
                        data if len(str(data)) < 5000 else str(data)[:5000] + "..."
                    )
                    return {
                        "type": "json",
                        "data": json.dumps(preview_data, indent=2, ensure_ascii=False),
                    }

            elif format_upper == "TSV":
                # Read TSV and use head() to limit rows
                df = pd.read_csv(file_path, sep="\t")
                df_preview = df.head(max_rows)
                return {
                    "type": "dataframe",
                    "data": df_preview.to_html(
                        classes="table table-striped table-hover",
                        table_id="preview-table",
                        escape=False,
                        border=0,
                        index=False,
                    ),
                    "shape": df.shape,
                    "preview_shape": df_preview.shape,
                    "columns": list(df.columns),
                }

            elif format_upper == "XML":
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()

                # Show first 3000 chars of formatted XML
                preview_content = (
                    content[:3000] + "..." if len(content) > 3000 else content
                )
                return {"type": "xml", "data": preview_content}

        except Exception as e:
            return {"type": "error", "data": f"Preview unavailable: {str(e)}"}

        return None

    @property
    def file_size_human(self):
        """Return human-readable file size"""
        if not self.size:
            return "Unknown"

        for unit in ["B", "KB", "MB", "GB", "TB"]:
            if self.size < 1024.0:
                return f"{self.size:.1f} {unit}"
            self.size /= 1024.0
        return f"{self.size:.1f} PB"

    @property
    def is_file_upload(self):
        return bool(self.file)

    @property
    def is_external_url(self):
        return bool(self.url and not self.file)
