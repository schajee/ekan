import os
from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.http import HttpResponse, JsonResponse
from web import models
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.db.models import Count
from django.core.paginator import Paginator
from web import forms
from django.core.mail import BadHeaderError, send_mail
from django.contrib import messages
from django.conf import settings


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
        query = request.GET.get('search', None)
        if query is not None:
            datasets = datasets.filter(title__contains=query)
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
        # Filter results on search criteria
        query = request.GET.get('search', None)
        if query is not None:
            datasets = datasets.filter(title__contains=query)
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
        # Filter results on search criteria
        query = request.GET.get('search', None)
        if query is not None:
            datasets = datasets.filter(title__contains=query)
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
            return render(request, 'auth/signup.html')
        elif request.method == 'POST':
            JsonResponse(request.POST, safe=False, status=200)

    @classmethod
    def login(cls, request):
        if request.method == 'GET':
            return render(request, 'auth/login.html')
        elif request.method == 'POST':
            return JsonResponse(request.POST, safe=False, status=200)

    @classmethod
    def account(cls, request):
        if request.method == 'GET':
            return render(request, 'auth/account.html')
        elif request.method == 'POST':
            return JsonResponse(request.POST, safe=False, status=200)

    @classmethod
    def logout(cls, request):
        # Logout user
        logout(request)
        # Return to homepage
        return redirect(reverse('home'))

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
                        messages.success(request, 'Thank you for contacting us. Your query has been forwarded to the relevent department!')
                        return redirect(reverse('web:page', args=('contact',)))
                    except BadHeaderError as error:
                        messages.error(request, str(error))
                    
            return render(request, 'pages/' + slug + '.html', {
                'form': form,
            })
        else:
            return render(request, 'pages/' + slug + '.html')
            
