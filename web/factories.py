import factory, uuid
import factory.fuzzy
from . import models
from django.contrib.auth.models import User
from django.utils.text import slugify


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    username = factory.Faker('user_name')
    email = factory.Faker('email')
    password = 'password'
    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')
    is_active = True
    is_staff = True


class TopicFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Topic

    title = factory.Faker('job')
    slug = factory.LazyAttribute(lambda a: slugify(a.title))
    icon = 'fa fa-cube'


class FormatFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Format
    
    title = factory.Faker('file_extension')
    slug = factory.LazyAttribute(lambda a: slugify(a.title))
    icon = 'fa fa-file'


class LicenseFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.License
    
    title = factory.Faker('sentence', nb_words=4)
    slug = factory.LazyAttribute(lambda a: slugify(a.title))
    icon = 'fab fa-creative-commons'


class TypeFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Type

    title = factory.Faker('color_name')
    slug = factory.LazyAttribute(lambda a: slugify(a.title))
    icon = 'fa fa-link'


class OrganisationFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Organisation

    title = factory.Faker('company')
    slug = factory.LazyAttribute(lambda a: slugify(a.title))
    description = factory.Faker('text')
    url = factory.Faker('url')
    manager = factory.fuzzy.FuzzyChoice(User.objects.all())


class DatasetFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Dataset
    
    title = factory.Faker('name')
    slug = factory.LazyAttribute(lambda a: slugify(a.title))
    description = factory.Faker('text')
    organisation = factory.fuzzy.FuzzyChoice(models.Organisation.objects.all())
    license = factory.fuzzy.FuzzyChoice(models.License.objects.all())


class DatasetTopicFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Dataset_Topic

    topic = factory.fuzzy.FuzzyChoice(models.Topic.objects.all())
    dataset = factory.fuzzy.FuzzyChoice(models.Dataset.objects.all())


class ResourceFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Resource

    title = factory.Faker('sentence', nb_words=4)
    description = factory.Faker('text')
    dataset = factory.fuzzy.FuzzyChoice(models.Dataset.objects.all())
    type = factory.fuzzy.FuzzyChoice(models.Type.objects.all())
    format = factory.fuzzy.FuzzyChoice(models.Format.objects.all())
    identifier = factory.Faker('url')
    size = factory.Faker('pyint')
