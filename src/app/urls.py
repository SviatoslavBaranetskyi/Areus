from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index-page"),
    path("login", views.login_page_view, name="login-page"),
]
