from django import forms
from .models import Organisation


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