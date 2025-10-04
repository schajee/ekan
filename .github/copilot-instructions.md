# EKAN (Easy Knowledge Archive Network) - AI Coding Assistant Instructions

## Project Architecture

**EKAN** is a Django-based open data portal inspired by CKAN, with a clean separation between web app and REST API.

### Core Entity Model
- **Resource**: Basic data unit (file/URL) with format classification and pandas preview capabilities
- **Dataset**: Collection of resources, categorized by topics, owned by organisations
- **Organisation**: Government entities with assigned staff managers
- **Topic**: Multi-select classification tags for datasets
- **Format**: Limited to 5 types (CSV, JSON, XML, PDF, XLSX) with color-coded badges

### Application Structure
```
app/          # Main Django application (web interface)
├── models.py          # Core data models with smart breadcrumbs
├── views.py           # Class-based views with filtering
├── templatetags/      # Custom tags: smart_breadcrumbs, query_replace
├── management/commands/ # Data seeding, social auth setup, preview updates
└── static/           # Bootstrap 5.3.8 + Public Sans font

api/          # REST API (DRF with filtering)
project/      # Django settings with environment variable support
templates/    # Bootstrap-based UI with partial system
├── layouts/  # base.html, auth.html with modern design
├── partials/ # Reusable components (cards, breadcrumbs, sidebar)
└── account/  # Custom allauth templates (no django-allauth-ui)
```

## Critical Developer Workflows

### Environment Setup
```bash
# Always use virtual environment Python
.\.venv\Scripts\python.exe manage.py [command]

# Environment configuration via .env file
# Required: SECRET_KEY, GOOGLE_OAUTH2_CLIENT_ID, EMAIL_BACKEND
uv sync  # Install dependencies from pyproject.toml

# Note: Development server typically runs via debugger, not manual runserver
```

### Key Management Commands
```bash
# Database seeding with synthetic data
.\.venv\Scripts\python.exe manage.py seed --datasets 50 --organisations 12

# Social authentication setup from .env
.\.venv\Scripts\python.exe manage.py setup_social_auth

# Email testing
.\.venv\Scripts\python.exe manage.py test_email --to user@example.com

# Preview data updates (pandas DataFrame.head())
.\.venv\Scripts\python.exe manage.py update_preview_availability
```

## Project-Specific Conventions

### Template System
- **Smart Breadcrumbs**: Automatically generated from URL patterns using `{% smart_breadcrumbs %}`
- **Partial Components**: Reusable cards for datasets, organisations, topics with footer-based counts
- **Color-Coded Formats**: CSV=success, JSON=info, XML=warning, PDF=danger, XLSX=primary
- **Authentication**: Custom Bootstrap templates, POST-only logout forms

### Model Patterns
```python
# Auto-slugification in save() methods
def save(self, *args, **kwargs):
    if not self.slug:
        self.slug = slugify(self.title)
    super().save(*args, **kwargs)

# Preview data with pandas (Resources only)
def get_preview_data(self, max_rows=10):
    df = pd.read_csv(self.url)
    return df.head(max_rows).to_html(classes='table table-hover')
```

### URL Structure
- Nested resource URLs: `/datasets/<slug>/resources/<slug>/`
- RESTful API at `/api/v1/` with DRF ViewSets
- Authentication redirects to django-allauth URLs
- Static pages use generic `<str:slug>/` pattern

### Frontend Architecture
- **No JavaScript Framework**: Pure Bootstrap 5.3.8 with Public Sans font
- **django-browser-reload**: Auto-refresh during development
- **Template Partials**: `{% include 'partials/resource_tag.html' %}` for reusability
- **Filtering**: Mutual exclusivity between topics/organisations in sidebar

## Integration Points

### Authentication Flow
- **django-allauth** with mandatory email verification
- **Google OAuth2** configured via environment variables
- **Social apps** auto-created by management command
- **Custom templates** in `templates/account/` (no django-allauth-ui)

### Data Processing
- **pandas** for CSV/Excel preview with `.head()` method
- **factory-boy + Faker** for synthetic data generation
- **Limited formats** enforced in factories and database seeding
- **Preview availability** tracking for dashboard optimization

### API Design
- **DRF ViewSets** with django-filter integration
- **Pagination**: 20 items per page
- **Permissions**: IsAuthenticatedOrReadOnly
- **Filtering**: SearchFilter + OrderingFilter enabled

## Environment Variables (.env)
```env
DEBUG=True
SECRET_KEY=<generated-key>
DATABASE_URL=sqlite:///db.sqlite3
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
GOOGLE_OAUTH2_CLIENT_ID=<google-client-id>
GOOGLE_OAUTH2_CLIENT_SECRET=<google-secret>
SENDGRID_API_KEY=<optional-for-production>
```

## Testing and Debugging
- **Django Check**: Validates allauth configuration and static files
- **Template Loading**: Test with `get_template()` for syntax validation  
- **Preview Testing**: Use pandas to verify CSV/Excel processing
- **Social Auth**: Verify provider configuration in admin or shell
- **Development Server**: Typically runs via VS Code debugger, not manual runserver

Always use the virtual environment Python executable (`.\.venv\Scripts\python.exe`) for consistency across development environments.