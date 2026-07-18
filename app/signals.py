from django.dispatch import receiver
from allauth.socialaccount.signals import social_account_added, social_account_updated
from allauth.account.signals import user_signed_up


@receiver(social_account_added)
def populate_user_email_from_social(sender, request, sociallogin, **kwargs):
    """
    Automatically populate user email from social account data when a social account is added
    """
    user = sociallogin.user
    
    # If user doesn't have an email, try to get it from social account
    if not user.email:
        # Try to get email from social account extra_data
        email = sociallogin.account.extra_data.get('email')
        
        if email:
            user.email = email
            user.save()


@receiver(social_account_updated)
def update_user_email_from_social(sender, request, sociallogin, **kwargs):
    """
    Update user email from social account data when a social account is updated
    """
    user = sociallogin.user
    email = sociallogin.account.extra_data.get('email')
    
    if email and email != user.email:
        user.email = email
        user.save()


@receiver(user_signed_up)
def populate_user_info_on_signup(sender, request, user, sociallogin=None, **kwargs):
    """
    Populate user info when they sign up via social login
    """
    if sociallogin:
        # Get email from social account if not already set
        if not user.email:
            email = sociallogin.account.extra_data.get('email')
            if email:
                user.email = email
                user.save()