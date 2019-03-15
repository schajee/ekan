from django.urls import path

from web import views

app_name = 'web'

urlpatterns = [
    path('', views.Home.index, name='home'),

    path('signup', views.Auth.signup, name='signup'),
    path('login', views.Auth.login, name='login'),
    path('account', views.Auth.account, name='account'),
    path('logout', views.Auth.logout, name='logout'),

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
