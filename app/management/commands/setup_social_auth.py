from django.core.management.base import BaseCommand
from django.contrib.sites.models import Site
from allauth.socialaccount.models import SocialApp
from decouple import config


class Command(BaseCommand):
    help = 'Setup social authentication providers from environment variables'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--clean',
            action='store_true',
            help='Remove all existing social apps before creating new ones',
        )

    def handle(self, *args, **options):
        # Get the current site
        site = Site.objects.get(pk=config('SITE_ID', default=1, cast=int))
        
        # Clean up existing social apps if requested
        if options['clean']:
            deleted_count = SocialApp.objects.all().count()
            SocialApp.objects.all().delete()
            self.stdout.write(
                self.style.WARNING(f'Deleted {deleted_count} existing social applications')
            )
        
        # Setup Google OAuth2
        google_client_id = config('GOOGLE_OAUTH2_CLIENT_ID', default='')
        google_client_secret = config('GOOGLE_OAUTH2_CLIENT_SECRET', default='')
        
        if google_client_id and google_client_secret:
            # Remove any existing Google apps to avoid duplicates
            existing_google_apps = SocialApp.objects.filter(provider='google')
            if existing_google_apps.exists():
                existing_google_apps.delete()
                self.stdout.write(
                    self.style.WARNING('Removed existing Google OAuth2 applications')
                )
            
            # Create new Google app
            google_app = SocialApp.objects.create(
                provider='google',
                name='Google OAuth2',
                client_id=google_client_id,
                secret=google_client_secret,
            )
            google_app.sites.add(site)
            
            self.stdout.write(
                self.style.SUCCESS('Created Google OAuth2 social application')
            )
        else:
            self.stdout.write(
                self.style.WARNING('Google OAuth2 credentials not found in environment variables')
            )
        
        # Setup GitHub OAuth (if credentials are provided)
        github_client_id = config('GITHUB_CLIENT_ID', default='')
        github_client_secret = config('GITHUB_CLIENT_SECRET', default='')
        
        if github_client_id and github_client_secret:
            # Remove any existing GitHub apps to avoid duplicates
            existing_github_apps = SocialApp.objects.filter(provider='github')
            if existing_github_apps.exists():
                existing_github_apps.delete()
                self.stdout.write(
                    self.style.WARNING('Removed existing GitHub OAuth2 applications')
                )
            
            # Create new GitHub app
            github_app = SocialApp.objects.create(
                provider='github',
                name='GitHub OAuth2',
                client_id=github_client_id,
                secret=github_client_secret,
            )
            github_app.sites.add(site)
            
            self.stdout.write(
                self.style.SUCCESS('Created GitHub OAuth2 social application')
            )
        
        # Setup Facebook OAuth (if credentials are provided)
        facebook_app_id = config('FACEBOOK_APP_ID', default='')
        facebook_app_secret = config('FACEBOOK_APP_SECRET', default='')
        
        if facebook_app_id and facebook_app_secret:
            # Remove any existing Facebook apps to avoid duplicates
            existing_facebook_apps = SocialApp.objects.filter(provider='facebook')
            if existing_facebook_apps.exists():
                existing_facebook_apps.delete()
                self.stdout.write(
                    self.style.WARNING('Removed existing Facebook OAuth2 applications')
                )
            
            # Create new Facebook app
            facebook_app = SocialApp.objects.create(
                provider='facebook',
                name='Facebook OAuth2',
                client_id=facebook_app_id,
                secret=facebook_app_secret,
            )
            facebook_app.sites.add(site)
            
            self.stdout.write(
                self.style.SUCCESS('Created Facebook OAuth2 social application')
            )
        
        # Show final summary
        total_apps = SocialApp.objects.count()
        self.stdout.write(
            self.style.SUCCESS(f'Social authentication setup completed! Total apps: {total_apps}')
        )