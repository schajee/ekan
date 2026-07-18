from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from allauth.socialaccount.models import SocialAccount


class Command(BaseCommand):
    help = 'Fix missing email addresses for social login users'
    
    def handle(self, *args, **options):
        fixed_count = 0
        
        # Find users with empty emails who have social accounts
        users_without_email = User.objects.filter(email='')
        
        for user in users_without_email:
            social_accounts = SocialAccount.objects.filter(user=user)
            
            for social_account in social_accounts:
                # Try to extract email from social account extra_data
                email = social_account.extra_data.get('email')
                
                if email:
                    user.email = email
                    user.save()
                    fixed_count += 1
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'Fixed email for user {user.username}: {email}'
                        )
                    )
                    break
                
                # If direct email not found, try other common fields
                if not email and 'email_verified' in social_account.extra_data:
                    # Some providers might have email in a different structure
                    email = social_account.extra_data.get('email_verified')
                    if email and '@' in str(email):
                        user.email = email
                        user.save()
                        fixed_count += 1
                        self.stdout.write(
                            self.style.SUCCESS(
                                f'Fixed email for user {user.username}: {email}'
                            )
                        )
                        break
        
        if fixed_count == 0:
            self.stdout.write(
                self.style.WARNING('No users with missing emails found or no emails could be extracted')
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(f'Fixed emails for {fixed_count} users')
            )