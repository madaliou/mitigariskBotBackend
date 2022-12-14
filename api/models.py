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

PLATFORMCHOICES = (
    ('whatsapp', 'Whatsapp'),
    ('facebook', 'Facebook'),
    ('telegram', 'Telegram'),

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
    phoneNumber = models.CharField(max_length=20, unique=True)
    role = models.CharField(_("Role"), max_length=255, choices=ROLECHOICES, blank=True) 
    last_name = models.CharField(max_length=255, blank=True)
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

class Type(TimestampedModel):   
    _safedelete_policy = HARD_DELETE_NOCASCADE 
    name = models.CharField(max_length=255) 
    description = models.CharField(max_length=1024) 
 
class Category(TimestampedModel):   
    _safedelete_policy = HARD_DELETE_NOCASCADE 
    name = models.CharField(max_length=255)
    description = models.CharField(max_length=1024, null=True)  

class Gravity(TimestampedModel):   
    _safedelete_policy = HARD_DELETE_NOCASCADE 
    name = models.CharField(max_length=255)
    description = models.CharField(max_length=1024, null=True) 
 
class Ticket(TimestampedModel):   
    _safedelete_policy = HARD_DELETE_NOCASCADE 
    reference = models.CharField(max_length=255,null=True)
    description = models.TextField(max_length=1024)  
    fixed = models.PositiveSmallIntegerField(default=0)
    urgency = models.BooleanField(default=0)
    lostOfHumanlifes = models.BooleanField(default=0, null=True)
    injuries = models.BooleanField(default=0)
    proceedings = models.TextField(max_length=1024, null=True) 
    correction = models.TextField(max_length=1024, null=True) 
    platform = models.CharField(_("PLATFORM"), max_length=255, choices=PLATFORMCHOICES, blank=True, null=True) 
    category = models.ForeignKey(Category, related_name='tickets', on_delete=models.CASCADE, null=True)
    gravity = models.ForeignKey(Gravity, related_name='tickets', on_delete=models.CASCADE, null=True)
    type = models.ForeignKey(Type, related_name='types', on_delete=models.CASCADE, null=True)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='tickets', null=True, on_delete=models.CASCADE)
    
class Reply(TimestampedModel):   
    _safedelete_policy = HARD_DELETE_NOCASCADE 
    message = models.TextField(max_length=1024)  
    read = models.BooleanField(default=False)
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, blank=True, null=True)
    

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

