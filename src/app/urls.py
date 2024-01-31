from django.urls import path

from . import views

urlpatterns = [
    path('', views.MainPageView.as_view(), name='main-page'),
    path('login', views.login, name='login-page'),
    path('get_databases', views.get_databases, name='get_databases')
]
