from django.contrib import admin

# Register your models here.
from .models import UserProfile

class UserProfileA(admin.ModelAdmin):
    list_display = ('role','first_name', 'last_name', 'username', 'email', 'birthDate', 'password')
    list_filter = ('first_name',)

admin.site.register(UserProfile, UserProfileA)

