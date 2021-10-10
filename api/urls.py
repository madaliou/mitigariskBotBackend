# basic_api/urls.py
from django.conf.urls import url, include
from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns
from api import views
from rest_framework_jwt.views import obtain_jwt_token, refresh_jwt_token, verify_jwt_token
from rest_framework.routers import DefaultRouter
from . import views as acc_views

router = DefaultRouter()
router.register('users', views.UserProfileViewSet, basename='users')
router.register('domains', views.DomainViewSet, basename='domains')
router.register('projects', views.ProjectViewSet, basename='projects')
router.register('localities', views.LocalityViewSet, basename='localities')

urlpatterns = [    
    path('', include(router.urls)),
    path('login/', obtain_jwt_token),
    path('projects-filter/', views.projects_filter), 
    path('import-projects/', views.import_projects), 

 
    
]









