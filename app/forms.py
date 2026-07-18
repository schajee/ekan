from django import forms
from django.contrib.auth.models import User
from .models import Organisation, Dataset, Resource, Format, License, Topic


class OrganisationRegistrationForm(forms.ModelForm):
    """Form for users to request new organisations"""
    
    class Meta:
        model = Organisation
        fields = ['title', 'description', 'url', 'logo']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Organization name',
                'required': True
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Describe the organization and its mission...',
                'required': True
            }),
            'url': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://example.gov'
            }),
            'logo': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            })
        }
        help_texts = {
            'title': 'The official name of your organization',
            'description': 'Provide a detailed description of your organization and its role',
            'url': 'Official website URL (optional)',
            'logo': 'Upload your organization logo (optional)'
        }
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Make description required
        self.fields['description'].required = True
        
    def save(self, commit=True):
        organisation = super().save(commit=False)
        
        # Set the requesting user
        if self.user:
            organisation.requested_by = self.user
        
        # Set status to pending
        organisation.status = Organisation.STATUS_PENDING
        
        if commit:
            organisation.save()
        return organisation


class OrganisationEditForm(forms.ModelForm):
    """Form for editing existing organisations"""
    
    class Meta:
        model = Organisation
        fields = ['title', 'description', 'url', 'logo']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Organization name',
                'required': True
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Describe the organization and its mission...',
                'required': True
            }),
            'url': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://example.gov'
            }),
            'logo': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            })
        }
        help_texts = {
            'title': 'The official name of your organization',
            'description': 'Provide a detailed description of your organization and its role',
            'url': 'Official website URL (optional)',
            'logo': 'Upload your organization logo (optional)'
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make description required
        self.fields['description'].required = True


class DatasetForm(forms.ModelForm):
    """Form for organization members to create datasets"""
    
    class Meta:
        model = Dataset
        fields = ['title', 'description', 'notes', 'topics', 'license', 'maintainer']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Dataset title',
                'required': True
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Describe what this dataset contains...',
                'required': True
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Additional notes, methodology, or context (optional)...'
            }),
            'topics': forms.CheckboxSelectMultiple(attrs={
                'class': 'form-check-input'
            }),
            'license': forms.Select(attrs={
                'class': 'form-select'
            }),
            'maintainer': forms.Select(attrs={
                'class': 'form-select'
            })
        }
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        self.organisation = kwargs.pop('organisation', None)
        super().__init__(*args, **kwargs)
        
        # Filter topics and licenses
        self.fields['topics'].queryset = Topic.objects.all()
        self.fields['license'].queryset = License.objects.all()
        self.fields['license'].empty_label = "Select a license"
        
        # Filter maintainer to organization users
        if self.organisation:
            # Get users who are associated with this organization
            org_users = self.organisation.users.all()
            
            self.fields['maintainer'].queryset = org_users.order_by('first_name', 'last_name', 'username')
            
            # Set current user as default maintainer if they're in the organization
            if self.user and self.user in org_users and not self.instance.pk:
                self.fields['maintainer'].initial = self.user
        else:
            # Fallback to all users if no organization context
            self.fields['maintainer'].queryset = User.objects.all().order_by('first_name', 'last_name', 'username')
            if self.user and not self.instance.pk:
                self.fields['maintainer'].initial = self.user
        
        self.fields['maintainer'].empty_label = "Select a maintainer"
    
    def save(self, commit=True):
        dataset = super().save(commit=False)
        
        # Set the author and organisation
        if self.user:
            dataset.author = self.user
        if self.organisation:
            dataset.organisation = self.organisation
        
        if commit:
            dataset.save()
            # Save many-to-many relationships
            self.save_m2m()
        return dataset


class ResourceForm(forms.ModelForm):
    """Form for adding resources to datasets"""
    
    class Meta:
        model = Resource
        fields = ['format', 'file', 'url']
        widgets = {
            'format': forms.Select(attrs={
                'class': 'form-select'
            }),
            'file': forms.FileInput(attrs={
                'class': 'form-control'
            }),
            'url': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://example.com/data.csv'
            })
        }
    
    def __init__(self, *args, **kwargs):
        self.dataset = kwargs.pop('dataset', None)
        super().__init__(*args, **kwargs)
        
        # Filter formats
        self.fields['format'].queryset = Format.objects.all()
        self.fields['format'].empty_label = "Select a format"
    
    def clean(self):
        cleaned_data = super().clean()
        file = cleaned_data.get('file')
        url = cleaned_data.get('url')
        
        # Must have either file or URL, but not both
        if not file and not url:
            raise forms.ValidationError("You must provide either a file upload or a URL.")
        
        if file and url:
            raise forms.ValidationError("Please provide either a file upload OR a URL, not both.")
        
        return cleaned_data
    
    def save(self, commit=True):
        resource = super().save(commit=False)
        
        # Set the dataset
        if self.dataset:
            resource.dataset = self.dataset
        
        if commit:
            resource.save()
        return resource