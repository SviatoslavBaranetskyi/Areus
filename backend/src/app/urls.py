from django.urls import path
from .yasg import urlpatterns as doc_urls

from . import views

urlpatterns = [
    path('', views.MainPageView.as_view(), name='main-page'),
    path('login/', views.login, name='login-page'),
    path('logout/', views.logout, name='logout-page'),
    path('api/databases/', views.DatabasesView.as_view(), name='databases'),
    path('api/tables/', views.TablesView.as_view(), name='tables'),
    path('api/table-rows/', views.TableRowsView.as_view(), name='table-rows'),
    path('api/users/', views.UserView.as_view(), name='users')
]

urlpatterns += doc_urls
