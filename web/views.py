import os

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import BadHeaderError, EmailMessage, send_mail
from django.core.paginator import Paginator
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render, reverse
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode

from web.tokens import account_activation_token
from web import forms, models


class Home:
    """Home Page"""
    @classmethod
    def index(cls, request):
        return render(request, 'home.html', {
            'topics': models.Topic.objects.order_by('?').all()[:9],
        })


class DatasetView:
    """Datasets"""
    @classmethod
    def index(cls, request):
        # Load file objects
        datasets = models.Dataset.objects.order_by('-updated').all()
        # Filter datasets results 
        datasets = filter_results(request, datasets)
        # Paginate the list
        paginator = Paginator(datasets, settings.PAGE_SIZE)
        # Render view with file objects
        return render(request, 'datasets/index.html', {
            'datasets': paginator.get_page(request.GET.get('page')),
            'paginator': paginator
        })

    @classmethod
    def show(cls, request, slug):
        dataset = get_object_or_404(models.Dataset, slug=slug)
        return render(request, 'datasets/show.html', {
            'dataset': dataset
        })


class ResourceView:
    """Resources"""
    @classmethod
    def show(cls, request, dataset, resource):
        resource = get_object_or_404(models.Resource, slug=resource)
        return render(request, 'resources/show.html', {
            'resource': resource
        })

    @classmethod
    def download(cls, request, dataset, resource):
        return JsonResponse(str(resource), safe=False, status=200)


class OrganisationView:
    """Organisations"""
    @classmethod
    def index(cls, request):
        return render(request, 'organisations/index.html', {
            'organisations': models.Organisation.objects.all()
        })

    @classmethod
    def show(cls, request, slug):
        # Fetch object or die
        organisation = get_object_or_404(models.Organisation, slug=slug)
        # Fetch related datasets
        datasets = organisation.dataset_set.order_by('-updated').all()
        # Filter datasets results
        datasets = filter_results(request, datasets)
        # Paginate the list
        paginator = Paginator(datasets, 10)
        # Render view with objects
        return render(request, 'organisations/show.html', {
            'organisation': organisation,
            'datasets': paginator.get_page(request.GET.get('page')),
            'paginator': paginator
        })


class TopicView:
    """Topics"""
    @classmethod
    def index(cls, request):
        return render(request, 'topics/index.html', {
            'topics': models.Topic.objects.all()
        })

    @classmethod
    def show(cls, request, slug):
        # Fetch object or die
        topic = get_object_or_404(models.Topic, slug=slug)
        # Fetch related datasets
        datasets = topic.dataset_set.order_by('-updated').all()
        # Filter datasets results
        datasets = filter_results(request, datasets)
        # Paginate the list with related datasets
        paginator = Paginator(datasets, 10)
        # Render view with objects
        return render(request, 'topics/show.html', {
            'topic': topic,
            'datasets': paginator.get_page(request.GET.get('page')),
            'paginator': paginator
        })


class Auth:
    @classmethod
    def signup(cls, request):
        if request.method == 'GET':
            form = forms.SignupForm()
        elif request.method == 'POST':
            form = forms.SignupForm(request.POST)
            if form.is_valid():

                user = User.objects.create_user(
                    username=form.cleaned_data['email'],
                    email=form.cleaned_data['email'],
                    password=form.cleaned_data['password'],
                    is_active=False
                )
                user.save()

                site = get_current_site(request)

                subject, from_email, to = 'Welcome to ' + \
                    settings.APP_NAME, settings.EMAIL_FROM, user.email

                message = render_to_string('emails/verify.html', {
                    'user': user,
                    'domain': site.domain,
                    'uid': user.pk,
                    'token': account_activation_token.make_token(user),
                })

                email = EmailMessage(
                    subject, message, from_email, [to])
                email.send()

                return render(request, 'auth/verify.html')
        return render(request, 'auth/signup.html', {
            'form': form
        })

    @classmethod 
    def verify(cls, request, uid, token):
        try:
            user = User.objects.get(pk=uid)
        except(TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        if user is not None and account_activation_token.check_token(user, token):
            user.is_active = True
            user.save()
            login(request, user)
            return redirect(reverse('web:home'))
        else:
            return HttpResponse(status=500)

    @classmethod
    def login(cls, request):
        if request.method == 'GET':
            form = forms.LoginForm()
        elif request.method == 'POST':
            form = forms.LoginForm(request.POST)
            if form.is_valid():
                # Authenticate username and password
                username = form.cleaned_data['username']
                password = form.cleaned_data['password']
                user = authenticate(
                    request, username=username, password=password)
                # If authenticated
                if user is not None:
                    # Login user - return back
                    login(request, user)
                    return redirect(reverse('web:home'))
        return render(request, 'auth/login.html', {
            'form': form
        })

    @classmethod
    def recover(cls, request):
        if request.method == 'GET':
            form = forms.ResetForm()
        elif request.method == 'POST':
            form = forms.ResetForm(request.POST)
            if form.is_valid():
                return JsonResponse(request.POST, safe=False, status=200)
        return render(request, 'auth/recover.html', {
            'form': form
        })

    @classmethod
    def account(cls, request, page='account'):
        items = None
        form = None
        if request.method == 'GET':
            if page:
                if page == 'account':
                    form = forms.AccountForm(instance=request.user)
                elif page == 'organisations':
                    items = request.user.organisation_set.all()
                elif page == 'datasets':
                    orgs = request.user.organisation_set.all()
                    items = models.Dataset.objects.filter(organisation__in=orgs)
                elif page == 'resources':
                    orgs = request.user.organisation_set.all()
                    data = models.Dataset.objects.filter(organisation__in=orgs)
                    items = models.Resource.objects.filter(
                        dataset__in=data)
        elif request.method == 'POST':
            form = forms.AccountForm(request.POST, instance=request.user)
            if form.is_valid():
                user = form.save(commit=False)
                user.save(update_fields=['username', 'email', 'first_name', 'last_name'])
                if request.POST['password']:
                    user.set_password(form.cleaned_data['password'])
                    user.save()
                messages.success(request, 'Account has been updated!')
        return render(request, 'account/index.html', {
            'page': page,
            'items': items,
            'form': form
        })
    
    @classmethod
    def logout(cls, request):
        # Logout user
        logout(request)
        # Return to homepage
        return redirect(reverse('web:home'))


class Static:
    @classmethod
    def pages(cls, request, slug):
        if slug == 'contact':
            if request.method == 'GET':
                form = forms.ContactForm()
            elif request.method == 'POST':
                form = forms.ContactForm(request.POST)
                if form.is_valid():
                    try:
                        send_mail(
                            request.POST['subject'],
                            request.POST['message'],
                            request.POST['email'],
                            [settings.EMAIL_TARGET],
                            fail_silently=False,
                        )
                        messages.success(
                            request, 'Thank you for contacting us. Your query has been forwarded to the relevent department!')
                        return redirect(reverse('web:page', args=('contact',)))
                    except BadHeaderError as error:
                        messages.error(request, str(error))

            return render(request, 'pages/' + slug + '.html', {
                'form': form,
            })
        else:
            return render(request, 'pages/' + slug + '.html')


def filter_results(request, datasets):
    """Filters datasets based on query parameters"""

    # Filter for search criteria
    query = request.GET.get('search', None)
    if query is not None:
        datasets = datasets.filter(title__icontains=query)

    # Filter results on organisation
    query = request.GET.get('organisation', None)
    if query is not None:
        organisations = models.Organisation.objects.filter(slug__exact=query)
        datasets = datasets.filter(organisation__in=organisations)
    
    # Filter results on topics
    query = request.GET.get('topic', None)
    if query is not None:
        topics = models.Topic.objects.filter(slug__exact=query)
        datasets = datasets.filter(topic__in=topics)

    # Filter results on format
    query = request.GET.get('license', None)
    if query is not None:
        licenses = models.License.objects.filter(slug__exact=query)
        datasets = datasets.filter(license__in=licenses)

    return datasets
