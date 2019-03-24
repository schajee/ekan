from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from web import views

app_name = 'web'

urlpatterns = [
    path('', views.Home.index, name='home'),

    path('signup', views.Auth.signup, name='signup'),
    path('verify/<int:uid>/<str:token>', views.Auth.verify, name='verify'),
    path('login', views.Auth.login, name='login'),
    path('recover', views.Auth.recover, name='recover'),
    path('logout', views.Auth.logout, name='logout'),

    path('account', views.Auth.account, name='account'),
    path('account/<str:page>', views.Auth.account, name='account_page'),

    path('datasets', views.DatasetView.index, name='datasets'),
    path('datasets/<str:slug>', views.DatasetView.show, name='dataset'),
    path('datasets/<slug:dataset>/resources/<uuid:resource>',
         views.ResourceView.show, name='resource'),
    path('datasets/<slug:dataset>/resources/<str:resource>',
         views.ResourceView.download, name='download'),

    path('organisations', views.OrganisationView.index, name='organisations'),
    path('organisations/<str:slug>',
         views.OrganisationView.show, name='organisation'),

    path('topics', views.TopicView.index, name='topics'),
    path('topics/<str:slug>', views.TopicView.show, name='topic'),

    path('<str:slug>', views.Static.pages, name='page'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
