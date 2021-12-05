from datetime import date
from os import name, removexattr
from django.shortcuts import render, get_object_or_404
from django.core.mail import EmailMultiAlternatives
from django.template.context import RequestContext
from django.urls.base import translate_url
from .models import UserProfile, Project, Domain, Picture, Region, Prefecture, Commune, Canton, Locality
from .serializers import UserProfileSerializer, UserProfileReadSerializer, ProjectSerializer, ProjectReadSerializer, DomainSerializer, DomainReadSerializer, ChangePasswordSerializer
from .serializers import PictureSerializer, PictureReadSerializer, RegionReadSerializer, RegionSerializer, PrefectureSerializer, PrefectureReadSerializer
from .serializers import CommuneSerializer, CommuneReadSerializer, CantonSerializer, CantonReadSerializer, LocalitySerializer, LocalityReadSerializer

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

class RegionViewSet(viewsets.ModelViewSet):
    permission_classes = (AllowAny,)
    
    queryset = Region.objects.all()
    def get_serializer_class(self):
        if self.request.method in ['GET']:
            return RegionReadSerializer
        return RegionSerializer

class PrefectureViewSet(viewsets.ModelViewSet):
    permission_classes = (AllowAny,)
    
    queryset = Prefecture.objects.all()
    def get_serializer_class(self):
        if self.request.method in ['GET']:
            return PrefectureReadSerializer

class CantonViewSet(viewsets.ModelViewSet):
    permission_classes = (AllowAny,)
    queryset = Canton.objects.all()
    def get_serializer_class(self):
        if self.request.method in ['GET']:
            return CantonReadSerializer
        return CantonSerializer

class CommuneViewSet(viewsets.ModelViewSet):
    permission_classes = (AllowAny,)
    queryset = Commune.objects.all()
    def get_serializer_class(self):
        if self.request.method in ['GET']:
            return CommuneReadSerializer
        return CommuneSerializer

class LocalityViewSet(viewsets.ModelViewSet):
    permission_classes = (AllowAny,)
    
    queryset = Locality.objects.all()

    def get_serializer_class(self):
        if self.request.method in ['GET']:
            return LocalityReadSerializer
        return LocalitySerializer

class DomainViewSet(viewsets.ModelViewSet):
    
    queryset = Domain.objects.all()

    def get_serializer_class(self):
        if self.request.method in ['GET']:
            return DomainReadSerializer
        return DomainSerializer

class ProjectViewSet(viewsets.ModelViewSet):
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
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

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

def modify_input_project_multiple_files(project_id, proofs):
    dict = {}
    dict['project'] = project_id
    dict['name'] = proofs
    return dict

class PictureViewSet(viewsets.ModelViewSet):
    

    queryset = Picture.objects.all()

    def get_serializer_class(self):

        if self.request.method in ['GET']:
            return PictureReadSerializer
        return PictureSerializer

#Filtrage paginé des projets
@api_view(['POST'])
def projects_filter(request):  
    data = {}
    if 'year' in request.data and request.data['year']:
        data['year'] = request.data['year']
    if 'updatedDomain' in request.data and request.data['updatedDomain']:
        data['updatedDomain'] = request.data['updatedDomain']      
    if 'q' in request.data and request.data['q']:
        data['code__icontains'] = str(request.data['q'])
    projects = Project.objects.filter(**data)  

    if len(projects)> 0:
        paginator = StandardResultsSetPagination()
        result_page = paginator.paginate_queryset(projects, request)
        serializer = ProjectReadSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)
    else:
        return Response([],status=status.HTTP_200_OK) 

#Filtrage paginé des localités
@api_view(['POST'])
def localities_filter(request):  
    data = {}
    if 'canton' in request.data and request.data['canton']:
        data['canton_id'] = request.data['canton']
    if 'commune' in request.data and request.data['commune']:
        data['canton__commune_id'] = request.data['commune']
    if 'prefecture' in request.data and request.data['prefecture']:
        data['canton__commune__prefecture_id'] = request.data['prefecture']  
    if 'region' in request.data and request.data['region']:
        data['canton__commune__prefecture__region_id'] = request.data['region']          
    if 'q' in request.data and request.data['q']:
        data['name__icontains'] = str(request.data['q'])
    localities = Locality.objects.filter(**data)  

    if len(localities)> 0:
        paginator = StandardResultsSetPagination()
        result_page = paginator.paginate_queryset(localities, request)
        serializer = LocalityReadSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)
    else:
        return Response([],status=status.HTTP_200_OK) 

#Filtrage paginé des localités
@api_view(['POST'])
def users_filter(request):  
    data = {}

    if 'role' in request.data and request.data['role']:
        data['role'] = request.data['role']          
    if 'q' in request.data and request.data['q']:
        data['first_name__icontains'] = str(request.data['q'])
    users = UserProfile.objects.filter(**data)  

    if len(users)> 0:
        paginator = StandardResultsSetPagination()
        result_page = paginator.paginate_queryset(users, request)
        serializer = UserProfileReadSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)
    else:
        return Response([],status=status.HTTP_200_OK) 

class StandardResultsSetPagination(pagination.PageNumberPagination):
    page_size = 50
    page_query_param = 'page'
    page_size_query_param = 'perPage'
    max_page_size = 20000  

import dateutil.parser
import os.path
import pandas as pd
import openpyxl
@api_view(['GET'])
def import_projects(request):        
    workbook = xlrd.open_workbook('/home/moozistudio/Bureau/Untitled spreadsheet.xlsx')
    SheetNameList = workbook.sheet_names()
    worksheet = workbook.sheet_by_name(SheetNameList[0])
    num_rows = worksheet.nrows 
    num_cells = worksheet.ncols 
    updatedDomain_R={}
    region_R={}
    prefecture_R={}
    commune_R={}
    canton_R={}
    locality_R={}
    curr_row = 1
    while curr_row < num_rows:
        cell_value_0 = worksheet.cell_value(curr_row, 0)
        cell_value_1 = worksheet.cell_value(curr_row, 1)
        cell_value_2 = worksheet.cell_value(curr_row, 2)
        cell_value_3 = worksheet.cell_value(curr_row, 3)
        cell_value_4 = worksheet.cell_value(curr_row, 4)
        cell_value_5 = worksheet.cell_value(curr_row, 5)
        cell_value_6 = worksheet.cell_value(curr_row, 6)
        cell_value_7 = worksheet.cell_value(curr_row, 7)
        cell_value_8 = worksheet.cell_value(curr_row, 8)
        cell_value_9 = worksheet.cell_value(curr_row, 9)
        cell_value_10 = worksheet.cell_value(curr_row, 10)
        cell_value_11 = worksheet.cell_value(curr_row, 11)
        cell_value_12 = worksheet.cell_value(curr_row, 12)
        # Région curr_cell == 3          
        project = Project()
        # Région curr_cell == 3
        if cell_value_1 not in region_R:
            region = Region()
            region.name = cell_value_1
            region.save()
            region_R[cell_value_1] = region
        # Préfecture curr_cell == 2
        if cell_value_2 not in prefecture_R:
            prefecture = Prefecture()
            prefecture.name = cell_value_2
            prefecture_R[cell_value_2] = prefecture
            prefecture_R[cell_value_2].region = region_R[cell_value_1]
            prefecture_R[cell_value_2].save()
        # Localité curr_cell == 0
        if cell_value_3 not in commune_R:
            commune = Commune()
            commune.name = cell_value_3
            commune_R[cell_value_3] = commune
            commune_R[cell_value_3].prefecture = prefecture_R[cell_value_2]
            commune_R[cell_value_3].save()
        # Canton curr_cell == 1
        if cell_value_4 not in canton_R:
            canton = Canton()
            canton.name = cell_value_4
            canton_R[cell_value_4] = canton
            canton_R[cell_value_4].commune = commune_R[cell_value_3]
            canton_R[cell_value_4].save()        
        # Localité curr_cell == 0
        if cell_value_6 not in locality_R:
            locality = Locality()
            locality.name = cell_value_6
            locality_R[cell_value_6] = locality
            locality_R[cell_value_6].canton = canton_R[cell_value_4]
            locality_R[cell_value_6].save()
            project.locality = locality
            project.save()
        if cell_value_6 in locality_R:
            project.locality = locality_R[cell_value_6]
            project.save()
        if cell_value_7 not in updatedDomain_R:
            domain = Domain()
            domain.name = cell_value_7
            domain.save()
            updatedDomain_R[cell_value_7] = domain 
            updatedDomain_R[cell_value_7].save()  
            project.updatedDomain = domain
            project.save()
        if cell_value_7 in updatedDomain_R:
            project.updatedDomain = updatedDomain_R[cell_value_7]
            project.save()
        project.code = cell_value_0
        project.name = cell_value_5  
        tt = str(cell_value_8)
        ss = tt[:4]
        project.year = ss
        project.par = cell_value_9
        if cell_value_11 == '':
            project.longitude = 0
        if cell_value_11 != '':
            project.longitude = cell_value_11
        if cell_value_12 == '':
            project.latitude = 0
        if cell_value_12 != '':
            project.latitude = cell_value_12
        project.save()
        curr_row = curr_row + 1 
    return Response({'ok': 'Fichier téléversé avec succès'}, status=status.HTTP_200_OK)
 
@api_view(['GET'])
@permission_classes([AllowAny])
def charts(request):
    tab1 = []
    tab2 = []
    dict = {}
    projects = Project.objects.all()
    for project in projects:
        pro = Project.objects.get(code=project)
        year = pro.year
        if year not in dict:
            c = Project.objects.filter(year=pro.year)
            g = (pro.year)
            tab1.append(g)
            tab2.append(c.count())
            dict[year] = year
    return Response( {
        'labels' : tab1,
        'data' : tab2                   
        })

from django.db.models import Sum
@api_view(['GET'])
@permission_classes([AllowAny])
def camembert(request):
    communes = Project.objects.all()
    communeProjects = {}
    #total des des frais d'achat par agent
    for commune in communes:
        communeProjects[commune.id] = {} 
        som = Project.objects.filter(locality__canton__commune__id=commune.id).count()
        communeProjects[commune.id] = som    
    communeProjects['projects'] = CommuneReadSerializer(communes, many=True).data            
    return Response( {
        'communeProjects' : communeProjects,
        })

#projets paginés
@api_view(['GET'])
def paginated_projects(request):    
    projects = Project.objects.all()
    if len(projects)> 0:
        paginator = StandardResultsSetPagination()
        result_page = paginator.paginate_queryset(projects, request)
        serializer = ProjectReadSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)
    else:
        return Response([],status=status.HTTP_200_OK) 

#projets paginés
@api_view(['GET'])
def paginated_localities(request):
    localities = Locality.objects.all()
    if len(localities)> 0:
        paginator = StandardResultsSetPagination()
        result_page = paginator.paginate_queryset(localities, request)
        serializer = LocalityReadSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)
    else:
        return Response([],status=status.HTTP_200_OK) 

class StandardResultsSetPagination(pagination.PageNumberPagination):
    page_size = 50
    page_query_param = 'page'
    page_size_query_param = 'perPage'
    max_page_size = 20000  

@api_view(['GET'])
def get_user(request):
    serializer = UserProfileSerializer(request.user)
    return Response(serializer.data)
 




