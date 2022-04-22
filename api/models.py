from django.db import models
#from django.contrib.auth.models import settings.AUTH_USER_MODEL
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import AbstractUser
from .managers import CustomUserManager
from django.utils.translation import ugettext_lazy as _
from safedelete.models import SafeDeleteModel
from safedelete.models import HARD_DELETE_NOCASCADE
from datetime import datetime, date
from django.utils import timezone
from rest_framework.response import Response


ROLECHOICES = (
    ('admin', 'Administrateur'),
    ('user', 'Utilisateur'),

)

GENDERCHOICES = (
    ('male', 'Masculin'),
    ('female', 'Feminin'),
)

# Create your models here.
class TimestampedModel(SafeDeleteModel):
    _safedelete_policy = HARD_DELETE_NOCASCADE
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
        ordering = ['-id']


class Company(TimestampedModel):   
    _safedelete_policy = HARD_DELETE_NOCASCADE 
    name = models.CharField(max_length=255) 
    description = models.CharField(max_length=1024)  



class UserProfile(AbstractUser):
    email = models.EmailField(max_length=70,blank=True, unique=True)
    role = models.CharField(_("Role"), max_length=255, choices=ROLECHOICES, blank=True) 
    first_name = models.CharField(max_length=255, blank=True)
    last_name = models.CharField(max_length=255, blank=True)
    passwordChanged = models.BooleanField(default=False)   
    author = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='children', null=True, on_delete=models.CASCADE)
    company = models.ForeignKey(Company, related_name='users', on_delete=models.CASCADE, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)   
   
    class Meta:
        ordering = ['-id']      

    @property
    def fullName(self):
        return '%s %s' % (self.last_name, self.first_name)
    @property
    def value(self):
        return self.id    
    @property
    def label(self):
        return self.name 
 

class Category(TimestampedModel):   
    _safedelete_policy = HARD_DELETE_NOCASCADE 
    name = models.CharField(max_length=255)
    description = models.CharField(max_length=1024, null=True)  


class Ticket(TimestampedModel):   
    _safedelete_policy = HARD_DELETE_NOCASCADE 
    description = models.CharField(max_length=1024)  
    category = models.ForeignKey(Category, related_name='tickets', on_delete=models.CASCADE, null=True)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='tickets', null=True, on_delete=models.CASCADE)

   

class Picture(TimestampedModel):
    name = models.ImageField(upload_to='uploads/images/', blank=True)  
    #project = models.ForeignKey(Project, related_name='projectPictures', null = True, on_delete=models.CASCADE)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name
    
    @property
    def value(self):
        return self.id
    
    @property
    def label(self):
        return self.name



