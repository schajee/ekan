import random
from faker import Faker
from django.contrib.auth.models import User
from django.utils.text import slugify
from django.utils import timezone
from .models import Organisation, OrganisationMember, License, Topic, Dataset, Format, Resource

fake = Faker()

# Sample data for realistic content
GOVT_ORGANISATIONS = [
    "Ministry of Health", "Department of Education", "Ministry of Finance", 
    "Department of Transport", "Ministry of Environment", "Department of Justice",
    "Ministry of Agriculture", "Department of Energy", "Ministry of Tourism",
    "Department of Social Services", "Ministry of Labor", "Department of Defense"
]

TOPICS_DATA = [
    ("Education", "fa fa-graduation-cap", "#007bff"),
    ("Health", "fa fa-heartbeat", "#dc3545"),
    ("Environment", "fa fa-leaf", "#28a745"),
    ("Transport", "fa fa-car", "#6c757d"),
    ("Economy", "fa fa-chart-line", "#fd7e14"),
    ("Agriculture", "fa fa-seedling", "#20c997"),
    ("Energy", "fa fa-bolt", "#ffc107"),
    ("Tourism", "fa fa-map-marker-alt", "#e83e8c"),
    ("Social Services", "fa fa-users", "#6f42c1"),
    ("Justice", "fa fa-gavel", "#17a2b8"),
    ("Defense", "fa fa-shield-alt", "#343a40"),
    ("Technology", "fa fa-microchip", "#007bff"),
]

LICENSES_DATA = [
    ("Public Domain", "No copyright restrictions", True, "fab fa-creative-commons-pd"),
    ("Creative Commons Attribution", "Free to use with attribution", True, "fab fa-creative-commons"),
    ("Open Government License", "Open government data license", True, "fa fa-unlock"),
    ("Restricted Access", "Government use only", False, "fa fa-lock"),
]

FORMATS_DATA = [
    ("CSV", "Comma-separated values", "text/csv", True, "fa fa-file-csv"),
    ("JSON", "JavaScript Object Notation", "application/json", True, "fa fa-file-code"),
    ("XML", "Extensible Markup Language", "application/xml", True, "fa fa-file-code"),
    ("PDF", "Portable Document Format", "application/pdf", False, "fa fa-file-pdf"),
    ("XLSX", "Excel spreadsheet", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", True, "fa fa-file-excel"),
]


def create_users(count=10):
    """Create sample users"""
    users = []
    for i in range(count):
        username = fake.user_name()
        # Ensure unique usernames
        while User.objects.filter(username=username).exists():
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


def create_licenses():
    """Create predefined licenses"""
    licenses = []
    for title, description, is_open, icon in LICENSES_DATA:
        license_obj, created = License.objects.get_or_create(
            slug=slugify(title),
            defaults={
                'title': title,
                'description': description,
                'is_open': is_open,
                'icon': icon,
            }
        )
        licenses.append(license_obj)
    return licenses


def create_topics():
    """Create predefined topics"""
    topics = []
    for title, icon, color in TOPICS_DATA:
        topic, created = Topic.objects.get_or_create(
            slug=slugify(title),
            defaults={
                'title': title,
                'description': fake.paragraph(nb_sentences=3),
                'icon': icon,
                'color': color,
                'is_featured': fake.boolean(chance_of_getting_true=40),
            }
        )
        topics.append(topic)
    return topics


def create_formats():
    """Create predefined formats"""
    formats = []
    for title, description, mime_type, is_data_format, icon in FORMATS_DATA:
        format_obj, created = Format.objects.get_or_create(
            slug=slugify(title),
            defaults={
                'title': title,
                'description': description,
                'mime_type': mime_type,
                'is_data_format': is_data_format,
                'icon': icon,
            }
        )
        formats.append(format_obj)
    return formats


def create_organisations(users, count=12):
    """Create government organisations"""
    organisations = []
    available_orgs = GOVT_ORGANISATIONS.copy()
    
    for i in range(min(count, len(available_orgs))):
        title = available_orgs[i]
        org, created = Organisation.objects.get_or_create(
            slug=slugify(title),
            defaults={
                'title': title,
                'description': fake.paragraph(nb_sentences=4),
                'url': fake.url(),
                'manager': random.choice(users),
                'is_active': True,
                'created': fake.date_time_between(start_date='-1y', end_date='now', tzinfo=timezone.get_current_timezone()),
            }
        )
        organisations.append(org)
    return organisations


def create_organisation_members(organisations, users):
    """Create organisation members with various roles"""
    members = []
    roles = ['admin', 'manager', 'coordinator', 'editor', 'analyst', 'viewer']
    job_titles = [
        'Data Manager', 'Senior Analyst', 'Information Officer', 'Research Coordinator',
        'Database Administrator', 'Policy Analyst', 'Statistics Officer', 'Data Scientist',
        'Information Systems Manager', 'Research Assistant', 'Data Entry Specialist'
    ]
    
    for org in organisations:
        # Create 2-5 members per organization
        num_members = random.randint(2, 5)
        selected_users = random.sample(users, min(num_members, len(users)))
        
        for i, user in enumerate(selected_users):
            # First member is often an admin/manager, others have varied roles
            role = 'admin' if i == 0 else random.choice(roles)
            
            member, created = OrganisationMember.objects.get_or_create(
                organisation=org,
                user=user,
                defaults={
                    'role': role,
                    'title': random.choice(job_titles),
                    'phone': fake.phone_number() if random.choice([True, False]) else '',
                    'email': fake.email() if random.choice([True, False]) else '',
                    'is_public_contact': random.choice([True, False, False]),  # 1/3 chance
                    'is_active': True,
                }
            )
            members.append(member)
    
    return members


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
        
        dataset = Dataset.objects.create(
            title=title,
            slug=slug,
            description=fake.paragraph(nb_sentences=5),
            notes=fake.text(max_nb_chars=500) if fake.boolean(chance_of_getting_true=60) else "",
            organisation=random.choice(organisations),
            license=random.choice(licenses),
            author=random.choice(users),
            maintainer_name=fake.name() if fake.boolean(chance_of_getting_true=70) else "",
            maintainer_email=fake.email() if fake.boolean(chance_of_getting_true=70) else "",
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
    
    for i in range(count):
        dataset = random.choice(datasets)
        title = f"{fake.word().title()} {fake.word().title()} Data"
        
        # Create unique slug
        base_slug = slugify(title)
        slug = f"{base_slug}-{fake.uuid4()[:8]}"
        
        created_date = fake.date_time_between(
            start_date=dataset.created, 
            end_date='now', 
            tzinfo=timezone.get_current_timezone()
        )
        
        format_obj = random.choice(formats)
        
        resource = Resource.objects.create(
            title=title,
            slug=slug,
            description=fake.paragraph(nb_sentences=3),
            dataset=dataset,
            format=format_obj,
            url=fake.url() if fake.boolean(chance_of_getting_true=30) else "",
            size=fake.random_int(min=1024, max=10485760),  # 1KB to 10MB
            mimetype=format_obj.mime_type,
            is_preview_available=format_obj.is_data_format,
            download_count=fake.random_int(min=0, max=500),
            created=created_date,
        )
        resources.append(resource)
    
    return resources