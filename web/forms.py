from django import forms
from django.contrib.auth.models import User
from django.contrib.auth import authenticate

from web import models

SUBJECTS = (
    ('I have a general question', 'I have a general question'),
    ('I would like to publish data', 'I would like to publish data'),
)


class ContactForm(forms.Form):
    name = forms.CharField(
        label='Full Name',
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        max_length=100,
        help_text='Provide your full name for reference'
    )
    organisation = forms.CharField(
        label='Organisation',
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        max_length=100,
        required=False,
        help_text='Provide the name of your organisation (if any)'
    )
    email = forms.EmailField(
        label='Email Address',
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        help_text='Provide a valid email address'
    )
    subject = forms.ChoiceField(
        label='Subject',
        widget=forms.Select(attrs={'class': 'form-control'}),
        choices=SUBJECTS,
        help_text='Select the nature of your query or comment'
    )
    message = forms.CharField(
        label='Message',
        widget=forms.Textarea(attrs={'class': 'form-control'}),
        help_text='Describe your query or comment'
    )


class LoginForm(forms.Form):
    """Defines the Login form"""
    username = forms.CharField(
        label='Username',
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        help_text='A valid email address; e.g. name@example.com'
    )
    password = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        # help_text='Provide a valid email address'
    )

    def clean(self):
        username = self.cleaned_data['username']
        password = self.cleaned_data['password']

        self.user = authenticate(username=username, password=password)
        if self.user is None or not self.user.is_active:
            raise forms.ValidationError('Invalid username and/or password')
        return self.cleaned_data


class SignupForm(forms.Form):
    email = forms.EmailField(
        label='Email Address',
        widget=forms.EmailInput(attrs={'class': 'form-control'}),
        help_text='A valid email address; e.g. name@example.com'
    )
    password = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        help_text='Use a strong password for this account.'
    )

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('Email address already exists')
        return email


class AccountForm(forms.ModelForm):
    password = forms.CharField(
        label='Password',
        help_text='Fill both Password and Confirm if you wish to update your password',
        max_length=100,
        widget=forms.PasswordInput(
            render_value=False,
            attrs={
                'class': 'form-control',
                'autocomplete': 'new-password',
                'placeholder': 'Password'
            }
        ),
        required=False
    )
    confirm = forms.CharField(
        label='Confirm',
        max_length=100,
        widget=forms.PasswordInput(
            attrs={
                'class': 'form-control',
                'autocomplete': 'new-password',
                'placeholder': 'Confirm Password'
            }
        ),
        required=False
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name',
                  'last_name', 'password', 'confirm']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.TextInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'}),
        }

    def clean(self):
        cleaned_data = super(AccountForm, self).clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm")

        if password != confirm_password:
            raise forms.ValidationError(
                "Password and Confirmation do not match"
            )


class ResetForm(forms.Form):
    email = forms.EmailField(
        label='Email Address',
        widget=forms.EmailInput(attrs={'class': 'form-control'}),
        # help_text='Provide a valid email address'
    )

    def clean_email(self):
        email = self.cleaned_data['email']
        if not User.objects.filter(email=email).exists():
            raise forms.ValidationError('Email address does not exist')
        return email


class ResourceForm(forms.ModelForm):
    class Meta:
        model = models.Resource
        fields = '__all__'

    def clean(self):
        cleaned_data = super(ResourceForm, self).clean()

        r_file = cleaned_data.get("file")
        r_url = cleaned_data.get('url')

        if r_url and r_file:
            raise forms.ValidationError(
                'Either FILE or URL can be specified. Please remove one of them.')

        if not r_url and not r_file:
            raise forms.ValidationError(
                'A File or URL must be specified as data source for this item.')

        return cleaned_data


class DatasetForm(forms.ModelForm):
    class Meta:
        model = models.Dataset
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(DatasetForm, self).__init__(*args, **kwargs)
        self.fields['organisation'].queryset = models.Organisation.objects.filter(
            manager=self.current_user)
