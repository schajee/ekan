import uuid
from django.db import models
from django.contrib.auth.models import User

class Organisation(models.Model):
    """Organises datasets into units; used primarily for Govt Departments"""
    title = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    url = models.URLField(blank=True)
    manager = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
    
    def type(self):
        return 'organisation'
    

class License(models.Model):
    """Defines licensing of a dataset; e.g. Public, ODC, etc."""
    title = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    icon = models.CharField(max_length=100)

    def __str__(self):
        return self.title


class Topic(models.Model):
    """Thematic classification of datasets; e.g. education, transport"""
    title = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    icon = models.CharField(max_length=100)
    datasets = models.ManyToManyField('Dataset', through='Dataset_Topic')

    def __str__(self):
        return self.title


class Dataset(models.Model):
    title = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    organisation = models.ForeignKey(Organisation, null=True, on_delete=models.SET_NULL)
    topics = models.ManyToManyField(Topic, through='Dataset_Topic')
    license = models.ForeignKey(License, null=True, on_delete=models.SET_NULL)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
    
    def type(self):
        return 'dataset'


class Dataset_Topic(models.Model):
    """Defines the Many-to-Many relationship between Dataset and Topic"""
    topic = models.ForeignKey(Topic, null=True, on_delete=models.CASCADE)
    dataset = models.ForeignKey(Dataset, null=True, on_delete=models.CASCADE)


class Format(models.Model):
    """Defines resource format; e.g. CSV, JSON, XLSX"""
    title = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    icon = models.CharField(max_length=100)

    def __str__(self):
        return self.title


class Resource(models.Model):
    """Fundamental data unit of Type; Belongs to a Dataset"""
    title = models.CharField(max_length=100)
    slug = models.CharField(max_length=36, default=uuid.uuid4, unique=True)
    description = models.TextField(blank=True)
    dataset = models.ForeignKey(Dataset, null=True, on_delete=models.SET_NULL)
    file = models.FileField(blank=True)
    url = models.URLField(blank=True)
    format = models.ForeignKey(Format, null=True, on_delete=models.SET_NULL)
    size = models.IntegerField(blank=True, default=0)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
