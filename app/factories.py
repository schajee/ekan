import random
from faker import Faker
from django.contrib.auth.models import User
from django.utils.text import slugify
from django.utils import timezone
from .models import Organisation, Topic, Dataset, Resource

fake = Faker()

# Sample data for realistic content
GOVT_ORGANISATIONS = [
    "Ministry of Health", "Department of Education", "Ministry of Finance", 
    "Department of Transport", "Ministry of Environment", "Department of Justice",
    "Ministry of Agriculture", "Department of Energy", "Ministry of Tourism",
    "Department of Social Services", "Ministry of Labor", "Department of Defense"
]

TOPICS_DATA = [
    ("Education", "#007bff"),
    ("Health", "#dc3545"),
    ("Environment", "#28a745"),
    ("Transport", "#6c757d"),
    ("Economy", "#fd7e14"),
    ("Agriculture", "#20c997"),
    ("Energy", "#ffc107"),
    ("Tourism", "#e83e8c"),
    ("Social Services", "#6f42c1"),
    ("Justice", "#17a2b8"),
    ("Defense", "#343a40"),
    ("Technology", "#007bff"),
]

LICENSES_DATA = [
    ("Public Domain", "No copyright restrictions", True, "bi bi-c-circle"),
    ("Creative Commons Attribution", "Free to use with attribution", True, "bi bi-cc-circle"),
    ("Open Government License", "Open government data license", True, "bi bi-unlock"),
    ("Restricted Access", "Government use only", False, "bi bi-lock"),
]

FORMATS_DATA = [
    ("CSV", "Comma-separated values", "text/csv", True, "bi bi-filetype-csv"),
    ("JSON", "JavaScript Object Notation", "application/json", True, "bi bi-filetype-json"),
    ("XML", "Extensible Markup Language", "application/xml", True, "bi bi-filetype-xml"),
    ("PDF", "Portable Document Format", "application/pdf", False, "bi bi-filetype-pdf"),
    ("XLSX", "Excel spreadsheet", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", True, "bi bi-filetype-xlsx"),
    ("XLS", "Excel 97-2003 spreadsheet", "application/vnd.ms-excel", True, "bi bi-filetype-xls"),
    ("ODS", "OpenDocument Spreadsheet", "application/vnd.oasis.opendocument.spreadsheet", True, "bi bi-file-earmark-spreadsheet"),
    ("DOC", "Microsoft Word document", "application/msword", False, "bi bi-filetype-doc"),
    ("DOCX", "Microsoft Word document", "application/vnd.openxmlformats-officedocument.wordprocessingml.document", False, "bi bi-filetype-docx"),
    ("RTF", "Rich Text Format", "application/rtf", False, "bi bi-file-earmark-text"),
    ("HTML", "HyperText Markup Language", "text/html", False, "bi bi-filetype-html"),
    ("ZIP", "Compressed archive", "application/zip", False, "bi bi-file-earmark-zip"),
]


def create_users(count=10):
    """Create sample users (excluding admin and demo users)"""
    users = []
    
    # Create regular users
    for i in range(count):
        username = fake.user_name()
        # Ensure unique usernames and avoid reserved names
        while User.objects.filter(username=username).exists() or username in ['admin', 'demo']:
            username = fake.user_name()
        
        user = User.objects.create_user(
            username=username,
            email=fake.email(),
            first_name=fake.first_name(),
            last_name=fake.last_name(),
            is_staff=fake.boolean(chance_of_getting_true=30),
            is_active=True
        )
        user.date_joined = fake.date_time_between(start_date='-2y', end_date='now', tzinfo=timezone.get_current_timezone())
        user.save()
        users.append(user)
    return users


# NOTE: Licenses and Formats are now loaded from fixtures
# No longer creating them in factories


def create_topics():
    """Create predefined topics"""
    topics = []
    for title, color in TOPICS_DATA:
        topic, created = Topic.objects.get_or_create(
            slug=slugify(title),
            defaults={
                'title': title,
                'description': fake.paragraph(nb_sentences=3),
                'color': color,
                'is_featured': fake.boolean(chance_of_getting_true=40),
            }
        )
        topics.append(topic)
    return topics


def create_organisations(users, count=12):
    """Create government organisations"""
    organisations = []
    available_orgs = GOVT_ORGANISATIONS.copy()
    
    for i in range(min(count, len(available_orgs))):
        title = available_orgs[i]
        requesting_user = random.choice(users)
        staff_users = [u for u in users if u.is_staff]
        approving_user = random.choice(staff_users) if staff_users else users[0]
        
        org, created = Organisation.objects.get_or_create(
            slug=slugify(title),
            defaults={
                'title': title,
                'description': fake.paragraph(nb_sentences=4),
                'url': fake.url(),
                'requested_by': requesting_user,
                'manager': random.choice(users),
                'status': 'approved',  # Make organisations approved
                'approved_by': approving_user,
                'approval_date': fake.date_time_between(start_date='-6m', end_date='-1m', tzinfo=timezone.get_current_timezone()),
                'is_active': True,
                'created': fake.date_time_between(start_date='-1y', end_date='now', tzinfo=timezone.get_current_timezone()),
            }
        )
        
        # Add 2-5 users to this organisation
        num_users = random.randint(2, 5)
        selected_users = random.sample(users, min(num_users, len(users)))
        for user in selected_users:
            org.users.add(user)
        
        organisations.append(org)
    return organisations


def create_datasets(organisations, licenses, users, topics, count=50):
    """Create sample datasets"""
    datasets = []
    
    for i in range(count):
        title = fake.catch_phrase().title()
        slug = slugify(title)
        
        # Ensure unique slug
        counter = 1
        original_slug = slug
        while Dataset.objects.filter(slug=slug).exists():
            slug = f"{original_slug}-{counter}"
            counter += 1
        
        created_date = fake.date_time_between(start_date='-8m', end_date='now', tzinfo=timezone.get_current_timezone())
        is_published = fake.boolean(chance_of_getting_true=80)
        
        organisation = random.choice(organisations)
        # Select maintainer from the organisation's users if available, otherwise any user
        maintainer = random.choice(list(organisation.users.all())) if organisation.users.exists() else random.choice(users)
        
        dataset = Dataset.objects.create(
            title=title,
            slug=slug,
            description=fake.paragraph(nb_sentences=5),
            notes=fake.text(max_nb_chars=500) if fake.boolean(chance_of_getting_true=60) else "",
            organisation=organisation,
            license=random.choice(licenses),
            author=random.choice(users),
            maintainer=maintainer,
            is_published=is_published,
            is_featured=fake.boolean(chance_of_getting_true=20),
            created=created_date,
            published_date=created_date if is_published else None,
        )
        
        # Add 1-3 random topics
        num_topics = fake.random_int(min=1, max=min(3, len(topics)))
        selected_topics = random.sample(topics, num_topics)
        for topic in selected_topics:
            dataset.topics.add(topic)
        
        datasets.append(dataset)
    
    return datasets


def create_resources(datasets, formats, count=200):
    """Create sample resources"""
    resources = []
    
    # Map fixture files to formats
    fixture_files = {
        'CSV': 'app/fixtures/file_example_CSV_5000.csv',
        'JSON': 'app/fixtures/file_example_JSON_1kb.json',
        'XML': 'app/fixtures/file_example_XML_24kb.xml',
        'PDF': 'app/fixtures/file-sample_150kB.pdf',
        'XLSX': 'app/fixtures/file_example_XLSX_50.xlsx',
        'XLS': 'app/fixtures/file_example_XLS_50.xls',
        'ODS': 'app/fixtures/file_example_ODS_100.ods',
        'DOC': 'app/fixtures/file-sample_100kB.doc',
        'DOCX': 'app/fixtures/file-sample_100kB.docx',
        'RTF': 'app/fixtures/file-sample_100kB.rtf',
        'HTML': 'app/fixtures/file-sample.htm',
        'ZIP': 'app/fixtures/file_sample_zip_2MB.zip',
    }
    
    for i in range(count):
        dataset = random.choice(datasets)
        
        created_date = fake.date_time_between(
            start_date=dataset.created, 
            end_date='now', 
            tzinfo=timezone.get_current_timezone()
        )
        
        format_obj = random.choice(formats)
        
        # Randomly decide between file upload or URL (50/50 chance)
        use_file = fake.boolean()
        file_path = None
        url = None
        
        if use_file and format_obj.title.upper() in fixture_files:
            # Use fixture file for this format
            file_path = fixture_files[format_obj.title.upper()]
            url = ""  # Clear URL when using file
        else:
            # Use URL instead
            url = fake.url()
        
        resource = Resource.objects.create(
            dataset=dataset,
            format=format_obj,
            url=url,
            size=fake.random_int(min=1024, max=10485760),  # 1KB to 10MB
            mimetype=format_obj.mime_type,
            is_preview_available=format_obj.is_data_format,
            download_count=fake.random_int(min=0, max=500),
            created=created_date,
        )
        
        # If we have a file path, copy the fixture file to the resource
        if file_path:
            import os
            from django.core.files import File
            from django.conf import settings
            
            fixture_file_path = os.path.join(settings.BASE_DIR, file_path)
            if os.path.exists(fixture_file_path):
                with open(fixture_file_path, 'rb') as f:
                    file_name = os.path.basename(fixture_file_path)
                    resource.file.save(file_name, File(f), save=True)
        
        resources.append(resource)
    
    return resources