import uuid
from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils.text import slugify


class Organisation(models.Model):
    """Government entities that publish datasets"""
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, max_length=200)
    description = models.TextField(blank=True)
    url = models.URLField(blank=True, help_text="Official website URL")
    logo = models.ImageField(upload_to='organisations/', blank=True, null=True)
    manager = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, 
                               help_text="Staff member responsible for this organisation")
    is_active = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['title']

    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse('organisations:detail', kwargs={'slug': self.slug})
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)


class License(models.Model):
    """Data licensing options (e.g., Public Domain, Creative Commons, etc.)"""
    title = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    url = models.URLField(blank=True, help_text="URL to license details")
    icon = models.CharField(max_length=100, default="fa fa-certificate")
    is_open = models.BooleanField(default=True, help_text="Is this an open license?")

    class Meta:
        ordering = ['title']

    def __str__(self):
        return self.title


class Topic(models.Model):
    """Thematic classification for datasets (e.g., education, transport, health)"""
    title = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=100, default="fa fa-tag")
    color = models.CharField(max_length=7, default="#007bff", 
                           help_text="Hex color code for display")
    is_featured = models.BooleanField(default=False)

    class Meta:
        ordering = ['title']

    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse('topics:detail', kwargs={'slug': self.slug})


class Dataset(models.Model):
    """Collection of related resources from an organisation"""
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, max_length=200)
    description = models.TextField(help_text="Detailed description of the dataset")
    notes = models.TextField(blank=True, help_text="Additional notes or methodology")
    
    organisation = models.ForeignKey(Organisation, on_delete=models.CASCADE, 
                                   related_name='datasets')
    topics = models.ManyToManyField(Topic, blank=True, related_name='datasets')
    license = models.ForeignKey(License, null=True, blank=True, 
                               on_delete=models.SET_NULL, related_name='datasets')
    
    # Metadata
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='authored_datasets')
    maintainer_name = models.CharField(max_length=100, blank=True)
    maintainer_email = models.EmailField(blank=True)
    
    # Status
    is_published = models.BooleanField(default=False)
    is_featured = models.BooleanField(default=False)
    
    # Timestamps
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    published_date = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-updated']

    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse('datasets:detail', kwargs={'slug': self.slug})
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)
    
    @property
    def resource_count(self):
        return self.resources.count()


class Format(models.Model):
    """File format types (e.g., CSV, JSON, PDF, XLSX)"""
    title = models.CharField(max_length=50)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=100, default="fa fa-file")
    mime_type = models.CharField(max_length=100, blank=True)
    is_data_format = models.BooleanField(default=True, 
                                       help_text="Can this format be previewed/analyzed?")

    class Meta:
        ordering = ['title']

    def __str__(self):
        return self.title.upper()


class Resource(models.Model):
    """Individual files or URLs within a dataset"""
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True, editable=False)
    description = models.TextField(blank=True)
    
    dataset = models.ForeignKey(Dataset, on_delete=models.CASCADE, related_name='resources')
    format = models.ForeignKey(Format, null=True, blank=True, 
                              on_delete=models.SET_NULL, related_name='resources')
    
    # File or URL
    file = models.FileField(upload_to='resources/%Y/%m/', blank=True, null=True)
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
        ordering = ['created']

    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse('resources:detail', kwargs={'slug': self.slug})
    
    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            self.slug = f"{base_slug}-{uuid.uuid4().hex[:8]}"
        
        # Auto-detect file size and mimetype
        if self.file and hasattr(self.file, 'size'):
            self.size = self.file.size
        
        # Set preview availability based on format
        self.is_preview_available = self.can_preview()
        
        super().save(*args, **kwargs)
    
    def can_preview(self):
        """Check if this resource can be previewed"""
        if not self.format:
            return False
        
        previewable_formats = ['CSV', 'XLSX', 'XLS', 'JSON', 'XML', 'TSV']
        return self.format.title.upper() in previewable_formats
    
    def get_preview_data(self, max_rows=100):
        """Get preview data for supported file types"""
        import pandas as pd
        import json
        
        if not self.file or not self.can_preview():
            return None
        
        try:
            file_path = self.file.path if hasattr(self.file, 'path') else self.file.url
            format_upper = self.format.title.upper() if self.format else ''
            
            if format_upper == 'CSV':
                # Read CSV and use head() to limit rows
                df = pd.read_csv(file_path)
                df_preview = df.head(max_rows)
                return {
                    'type': 'dataframe',
                    'data': df_preview.to_html(
                        classes='table table-striped table-hover', 
                        table_id='preview-table',
                        escape=False, 
                        border=0,
                        index=False
                    ),
                    'shape': df.shape,
                    'preview_shape': df_preview.shape,
                    'columns': list(df.columns)
                }
            
            elif format_upper in ['XLSX', 'XLS']:
                # Read Excel and use head() to limit rows
                df = pd.read_excel(file_path)
                df_preview = df.head(max_rows)
                return {
                    'type': 'dataframe',
                    'data': df_preview.to_html(
                        classes='table table-striped table-hover', 
                        table_id='preview-table',
                        escape=False, 
                        border=0,
                        index=False
                    ),
                    'shape': df.shape,
                    'preview_shape': df_preview.shape,
                    'columns': list(df.columns)
                }
            
            elif format_upper == 'JSON':
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # If it's a list of records, try to convert to DataFrame
                if isinstance(data, list) and data and isinstance(data[0], dict):
                    df = pd.DataFrame(data)
                    df_preview = df.head(max_rows)
                    return {
                        'type': 'dataframe',
                        'data': df_preview.to_html(
                            classes='table table-striped table-hover', 
                            table_id='preview-table',
                            escape=False, 
                            border=0,
                            index=False
                        ),
                        'shape': df.shape,
                        'preview_shape': df_preview.shape,
                        'columns': list(df.columns)
                    }
                else:
                    # Just show formatted JSON
                    preview_data = data if len(str(data)) < 5000 else str(data)[:5000] + '...'
                    return {
                        'type': 'json',
                        'data': json.dumps(preview_data, indent=2, ensure_ascii=False)
                    }
            
            elif format_upper == 'TSV':
                # Read TSV and use head() to limit rows
                df = pd.read_csv(file_path, sep='\t')
                df_preview = df.head(max_rows)
                return {
                    'type': 'dataframe',
                    'data': df_preview.to_html(
                        classes='table table-striped table-hover', 
                        table_id='preview-table',
                        escape=False, 
                        border=0,
                        index=False
                    ),
                    'shape': df.shape,
                    'preview_shape': df_preview.shape,
                    'columns': list(df.columns)
                }
            
            elif format_upper == 'XML':
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Show first 3000 chars of formatted XML
                preview_content = content[:3000] + '...' if len(content) > 3000 else content
                return {
                    'type': 'xml',
                    'data': preview_content
                }
        
        except Exception as e:
            return {
                'type': 'error',
                'data': f'Preview unavailable: {str(e)}'
            }
        
        return None
    
    @property
    def file_size_human(self):
        """Return human-readable file size"""
        if not self.size:
            return "Unknown"
        
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
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
