from django import forms

FAVORITE_COLORS_CHOICES = (
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
        choices=FAVORITE_COLORS_CHOICES,
        help_text='Select the nature of your query or comment'
    )
    message = forms.CharField(
        label='Message',
        widget=forms.Textarea(attrs={'class':'form-control'}),
        help_text='Describe your query or comment'
    )
