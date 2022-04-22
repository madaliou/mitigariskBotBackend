# basic_api/urls.py
from django.conf.urls import url, include
from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns
from api import views
from rest_framework_jwt.views import obtain_jwt_token, refresh_jwt_token, verify_jwt_token
from rest_framework.routers import DefaultRouter
from . import views as acc_views
from .views import ChangePasswordView
from api.views import RegisterView



router = DefaultRouter()
router.register('users', views.UserProfileViewSet, basename='users')
router.register('categories', views.CategoryViewSet, basename='categories')
router.register('companies', views.CompanyViewSet, basename='companies')
router.register('tickets', views.TicketViewSet, basename='tickets')
path('register/', RegisterView.as_view(), name='auth_register'),   


#router.register('domains', views.DomainViewSet, basename='domains')




urlpatterns = [    
    path('', include(router.urls)),
    path('login/', obtain_jwt_token),
    path('change-password/', ChangePasswordView.as_view(), name='change-password'),
    path('fix_ticket/', views.fix_ticket),
    path('fixed_tickets/', views.fixed_tickets),
    path('unfixed_tickets/', views.unfixed_tickets),



 
    
]









