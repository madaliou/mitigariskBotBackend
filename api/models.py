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

ROLECHOICES = (
    ('admin', 'Administrateur'),

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

class UserProfile(AbstractUser):
    email = models.EmailField(max_length=70,blank=True, unique=True)
    phoneNumber = models.CharField(max_length=20, null=True, unique=True)
    role = models.CharField(_("Role"), max_length=255, choices=ROLECHOICES, blank=True) 
    first_name = models.CharField(max_length=255, blank=True)
    last_name = models.CharField(max_length=255, blank=True)
    username = models.CharField(max_length=255, unique=True, blank=True)
    birthDate = models.DateField(_("Date de naissance"), blank=True, null=True) 
    passwordChanged = models.BooleanField(default=False)   
    author = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='children', null=True, on_delete=models.CASCADE)
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

class Region(TimestampedModel):   
    name = models.CharField(max_length=255)  
   
    def __str__(self):
        return self.name  
    @property
    def value(self):
        return self.id    
    @property
    def label(self):
        return self.name       

class Prefecture(TimestampedModel):   
    name = models.CharField(max_length=255)     
    region = models.ForeignKey(Region, related_name='region', on_delete=models.CASCADE)

    def __str__(self):
        return self.name
    @property
    def value(self):
        return self.id    
    @property
    def label(self):
        return self.name 

class Commune(TimestampedModel):   
    name = models.CharField(max_length=1024)     
    prefecture = models.ForeignKey(Prefecture, related_name='prefecture', on_delete=models.CASCADE, null=True)
    def __str__(self):
        return self.name
    @property
    def value(self):
        return self.id    
    @property
    def label(self):
        return self.name 

class Canton(TimestampedModel):   
    name = models.CharField(max_length=255)     
    commune = models.ForeignKey(Commune, related_name='commune', on_delete=models.CASCADE)
  
    def __str__(self):
        return self.name
    @property
    def value(self):
        return self.id    
    @property
    def label(self):
        return self.name 

class Locality(TimestampedModel):   
    name = models.CharField(max_length=1024)     
    canton = models.ForeignKey(Canton, related_name='canton', on_delete=models.CASCADE)
  
    def __str__(self):
        return self.name
    @property
    def value(self):
        return self.id    
    @property
    def label(self):
        return self.name 

class Domain(TimestampedModel):   
    _safedelete_policy = HARD_DELETE_NOCASCADE 
    name = models.CharField(max_length=1024) 

    def __str__(self):
        return self.name
    @property
    def value(self):
        return self.id    
    @property
    def label(self):
        return self.name   

from rest_framework.response import Response

class Project(TimestampedModel):   
    _safedelete_policy = HARD_DELETE_NOCASCADE 
    name = models.CharField(max_length=1024)  
    code = models.CharField(max_length=255)  
    updatedDomain = models.ForeignKey(Domain, related_name='projectDomain', on_delete=models.CASCADE, null=True)
    locality = models.ForeignKey(Locality, related_name='projectLocality', on_delete=models.CASCADE, null=True)
    year = models.DateField(null=True)
    number = models.FloatField(default=0) 
    par = models.CharField(max_length=255)  
    longitude = models.CharField(max_length=255)
    latitude = models.CharField(max_length=255)

    def __str__(self):
        return self.code
    @property
    def value(self):
        return self.id    
    @property
    def label(self):
        tab = []   
        tab.append(self.latitude) 
        tab.append(self.longitude) 
        return tab

class Picture(TimestampedModel):
    name = models.ImageField(upload_to='uploads/images/', blank=True)  

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



