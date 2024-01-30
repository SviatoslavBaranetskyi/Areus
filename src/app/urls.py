from django.urls import path

from . import views

urlpatterns = [
    path('', views.login, name='index-page'),
    path('main', views.MainPageView.as_view(), name='main-page'),
]
