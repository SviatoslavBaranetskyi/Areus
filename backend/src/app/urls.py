from django.urls import path

from . import views

urlpatterns = [
    path('', views.MainPageView.as_view(), name='main-page'),
    path('login', views.login, name='login-page'),
    path('logout', views.logout, name='logout-page'),
    path('api/get-databases', views.GetDatabasesView.as_view(), name='get-databases'),
    path('api/get-tables/', views.GetTablesView.as_view(), name='get-tables'),
    path('api/get-table-rows/', views.TableRowsView.as_view(), name='get-table-rows')
]
