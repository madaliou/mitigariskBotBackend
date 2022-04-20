from datetime import date
from os import name, removexattr
from django.shortcuts import render, get_object_or_404
from django.core.mail import EmailMultiAlternatives
from django.template.context import RequestContext
from django.urls.base import translate_url
from .models import UserProfile, Company, Category, Ticket
from .serializers import UserProfileSerializer, UserProfileReadSerializer, ChangePasswordSerializer
from .serializers import CompanyReadSerializer, CategoryReadSerializer, TicketReadSerializer
from .serializers import CompanySerializer, CategorySerializer, TicketSerializer, RegisterSerializer




from django.core.mail import send_mail
import json
from django.contrib.auth.models import User
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser
from rest_framework.response import Response
from django.http import JsonResponse, HttpResponse
from rest_framework.views import APIView
from rest_framework.decorators import api_view, authentication_classes
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from django.contrib.auth import get_user_model
from rest_framework import generics, mixins, viewsets, serializers
from django.forms.models import model_to_dict
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import AND, AllowAny
from datetime import datetime, timedelta
from django.dispatch import receiver
from django.template.loader import render_to_string
from rest_framework.views import APIView
from rest_framework import parsers, renderers
from .serializers import CustomTokenSerializer
from django_rest_passwordreset.models import ResetPasswordToken
from django_rest_passwordreset.views import get_password_reset_token_expiry_time
from django.utils import timezone
from datetime import timedelta
from django.core.mail import EmailMessage
from rest_framework.permissions import AllowAny
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import SessionAuthentication, BasicAuthentication 
import uuid
import xlrd
from rest_framework import pagination
from django.template import Context
from django.template.loader import render_to_string, get_template
from django.core.mail import EmailMultiAlternatives
from django.urls import reverse
from django_rest_passwordreset.signals import reset_password_token_created
from django.db.models import Q

from rest_framework_jwt.settings import api_settings
import random
import string

jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER

User = get_user_model()

def jwt_response_payload_handler(token, user=None, request=None):
    return {
        'accessToken': token,
        'userData': UserProfileReadSerializer(user, context={'request': request}).data
    }

  
class UserProfileViewSet(viewsets.ModelViewSet):
    queryset = UserProfile.objects.all()
    def get_serializer_class(self):
        if self.request.method in ['GET']:
            return UserProfileReadSerializer
        return UserProfileSerializer


class CompanyViewSet(viewsets.ModelViewSet):

    queryset = Company.objects.all().order_by('-id') 

    def get_serializer_class(self):
        
        if self.request.method in ['GET']:
            
            return CompanyReadSerializer
        return CompanySerializer


class CategoryViewSet(viewsets.ModelViewSet):

    queryset = Category.objects.all().order_by('-id') 

    def get_serializer_class(self):
        
        if self.request.method in ['GET']:
            
            return CategoryReadSerializer
        return CategorySerializer

class TicketViewSet(viewsets.ModelViewSet):

    queryset = Ticket.objects.all().order_by('-id') 

    def get_serializer_class(self):
        
        if self.request.method in ['GET']:
            
            return TicketReadSerializer
        return TicketSerializer


""" class ProjectViewSet(viewsets.ModelViewSet):
    permission_classes = (AllowAny,)
    
    queryset = Project.objects.all()

    def get_serializer_class(self):
        if self.request.method in ['GET']:
            return ProjectReadSerializer
        return ProjectSerializer
    
    def create(self, request, *args, **kwargs):        
        data = { 
                'code': request.data['code'],
                'name': request.data['name'],
                'updatedDomain': request.data['updatedDomain'],
                'par': request.data['par'],
                'locality': request.data['locality'],
                'year': str(request.data['year']),
                'longitude': request.data['longitude'],
                'latitude': request.data['latitude']

            }   
        if 'number' in request.data and request.data['number']:
            data['number'] = request.data['number']         
        serializer = ProjectSerializer(data=data)          
        if serializer.is_valid():
            instance = serializer.save() 
            instance_id = instance.id 
            if 'proofs' in request.data and request.data['proofs']:

                images = dict((request.data).lists())['proofs']
                flag = 1
                arr = []
                for img_name in images:
                    modified_data = modify_input_project_multiple_files(
                        instance_id, img_name)
                    print(modified_data)
                    file_serializer = PictureSerializer(data=modified_data)
                    if file_serializer.is_valid():
                        file_serializer.saclasseur_revu_corrigealizer(instance)  
            show = ProjectReadSerializer(instance)
            return Response(show.data, status=status.HTTP_201_CREATED)              
            show = ProjectReadSerializer(instance)
            return Response(show.data, status=status.HTTP_201_CREATED)             
        else:            
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)    
            
    def update(self, request, *args, **kwargs):     
        instance = self.get_object()  
        data = {
                'code': request.data['code'],
                'name': request.data['name'],
                'updatedDomain': request.data['updatedDomain'],
                'par': request.data['par'],
                'locality': request.data['locality'],
                'year': str(request.data['year']),
                'longitude': request.data['longitude'],
                'latitude': request.data['latitude']                  
            }
        if 'number' in request.data and request.data['number']:
            data['number'] = request.data['number'] 
        serializer = ProjectSerializer(instance,data=data)        
        if serializer.is_valid():
            instance = serializer.save()               
            instance_id = instance.id
            picture_delete = request.POST.getlist('pictures_remove', [])
            for pic in picture_delete:
                if pic is not None and pic != '':
                    p = Picture.objects.get(pk=pic)
                    if p is not None:
                        p.delete()
            if 'pictures_add' in request.data and request.data['pictures_add']:
                images = dict((request.data))['pictures_add']
                flag = 1
                arr = []
                for img_name in images:
                    # for inst in instance.picture
                    if img_name:
                        modified_data = modify_input_project_multiple_files(
                            instance_id, img_name)
                        file_serializer = PictureSerializer(data=modified_data)

                    if file_serializer.is_valid():
                        file_serializer.save()
                        arr.append(file_serializer.data)

                    else:
                        flag = 0

                if flag == 1:
                    show = ProjectReadSerializer(instance)                                 
            show = ProjectReadSerializer(instance)
            return Response(show.data, status=status.HTTP_201_CREATED)        
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST) """

# Changement de mot de passe
class ChangePasswordView(generics.UpdateAPIView):
    serializer_class = ChangePasswordSerializer
    model = User
    permission_classes = (IsAuthenticated,)

    def get_object(self, queryset=None):
        obj = self.request.user
        return obj

    def update(self, request, *args, **kwargs):
        self.object = self.get_object()
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            # Verifier le nombre de caractère du mot de passe
            if len(request.data['password']) < 8:
                return Response({"message": ["Ce mot de passe est trop court. Il doit contenir au minimum 8 caractères!"]}, status=status.HTTP_400_BAD_REQUEST)

            # Verifier l'ancien mot de passe
            if self.object.check_password(serializer.data.get("password")):
                return Response({"message": ["Veuillez choisir un mot de passe autre que l'ancien !"]}, status=status.HTTP_400_BAD_REQUEST)

            self.object.set_password(serializer.data.get("password"))
            self.object.passwordChanged = 1
            self.object.save()
            response = {
                'status': 'success',
                'code': status.HTTP_200_OK,
                'message': 'Mot de passe changé avec succès',
            }

            return Response(response)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = RegisterSerializer

@api_view(['GET'])
def get_user(request):
    serializer = UserProfileSerializer(request.user)
    return Response(serializer.data)
 




