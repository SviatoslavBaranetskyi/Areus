from django.urls import path
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi


schema_view = get_schema_view(
    openapi.Info(
        title="Areus",
        default_version="v1",
        description='''
        The objective of this project is to develop a simplified web application for managing databases, 
        inspired by phpMyAdmin. This project, built using the Django framework, emphasizes a clean design, modern 
        aesthetics, and enhanced performance. The development process will be divided into several steps, gradually 
        building functionality and refining the user interface.
        ''',
        license=openapi.License(name="BSD License")
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('swagger<format>/', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]

