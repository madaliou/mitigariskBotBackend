from datetime import date
from os import name, removexattr
from django.shortcuts import render, get_object_or_404
from django.core.mail import EmailMultiAlternatives
from django.template.context import RequestContext
from django.urls.base import translate_url
from .models import UserProfile, Project, Domain, Picture, Region, Prefecture, Commune, Canton, Locality
from .serializers import UserProfileSerializer, UserProfileReadSerializer, ProjectSerializer, ProjectReadSerializer, DomainSerializer, DomainReadSerializer
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

class LocalityViewSet(viewsets.ModelViewSet):
    queryset = Locality.objects.all()

    def get_serializer_class(self):
        if self.request.method in ['GET']:
            return LocalityReadSerializer
        return LocalitySerializer

class DomainViewSet(viewsets.ModelViewSet):
    permission_classes = (AllowAny,)
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
                'number': request.data['number'],
                'par': request.data['par'],
                'locality': request.data['locality'],
                'foundPoints': request.data['foundPoints'],
                'year': str(request.data['year']) + '-01-01',
                'longitude': request.data['longitude'],
                'latitude': request.data['latitude']

            }            
        serializer = ProjectSerializer(data=data)          
        if serializer.is_valid():
            instance = serializer.save()              
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
                'number': request.data['number'],
                'par': request.data['par'],
                'locality': request.data['locality'],
                'foundPoints': request.data['foundPoints'],
                'year': str(request.data['year']) + '-01-01',
                'longitude': request.data['longitude'],
                'latitude': request.data['latitude']                  
            }
         
        serializer = ProjectSerializer(instance,data=data)        
        if serializer.is_valid():
            instance = serializer.save()                                                  
            show = ProjectReadSerializer(instance)
            return Response(show.data, status=status.HTTP_201_CREATED)        
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class PictureViewSet(viewsets.ModelViewSet):

    queryset = Picture.objects.all()

    def get_serializer_class(self):

        if self.request.method in ['GET']:

            return PictureReadSerializer
        return PictureSerializer

def modify_input_operation_multiple_files(operation_id, proofs):
    dict = {}
    dict['operation'] = operation_id
    dict['name'] = proofs
    return dict

#Filtrage paginé des projets
@api_view(['POST'])
def projects_filter(request):  
    data = {}
    if 'year' in request.data and request.data['year']:
        data['year__year'] = request.data['year']
    if 'updatedDomain' in request.data and request.data['updatedDomain']:
        data['updatedDomain'] = request.data['updatedDomain']      
    """ if 'q' in request.data and request.data['q']:
        data['wording__icontains'] = str(request.data['q']) """
    projects = Project.objects.filter(**data)  
    if len(projects)> 0:
        paginator = StandardResultsSetPagination()
        result_page = paginator.paginate_queryset(projects, request)
        serializer = ProjectReadSerializer(result_page, many=True)
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
    workbook = xlrd.open_workbook('/home/moozistudio/Bureau/Plateau_Base2.xlsx')
    SheetNameList = workbook.sheet_names()
    worksheet = workbook.sheet_by_name(SheetNameList[0])
    print('SheetNameListSheetNameListSheetNameListSheetNameListSheetNameList', SheetNameList)
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
        cell_value_13 = worksheet.cell_value(curr_row, 13)
        # Région curr_cell == 3          
        project = Project()
        # Région curr_cell == 3
        if cell_value_2 not in region_R:
            region = Region()
            region.name = cell_value_2
            region.save()
            region_R[cell_value_2] = region
        # Préfecture curr_cell == 2
        if cell_value_3 not in prefecture_R:
            prefecture = Prefecture()
            prefecture.name = cell_value_3
            prefecture_R[cell_value_3] = prefecture
            prefecture_R[cell_value_3].region = region_R[cell_value_2]
            prefecture_R[cell_value_3].save()
        # Localité curr_cell == 0
        if cell_value_4 not in commune_R:
            commune = Commune()
            commune.name = cell_value_4
            commune_R[cell_value_4] = commune
            commune_R[cell_value_4].prefecture = prefecture_R[cell_value_3]
            commune_R[cell_value_4].save()
        # Canton curr_cell == 1
        if cell_value_5 not in canton_R:
            canton = Canton()
            canton.name = cell_value_5
            canton_R[cell_value_5] = canton
            canton_R[cell_value_5].commune = commune_R[cell_value_4]
            canton_R[cell_value_5].save()        
        # Localité curr_cell == 0
        if cell_value_7 not in locality_R:
            locality = Locality()
            locality.name = cell_value_7
            locality_R[cell_value_7] = locality
            locality_R[cell_value_7].canton = canton_R[cell_value_5]
            locality_R[cell_value_7].save()
            project.locality = locality
            project.save()
        if cell_value_7 in locality_R:
            project.locality = locality_R[cell_value_7]
            project.save()
        if cell_value_8 not in updatedDomain_R:
            domain = Domain()
            domain.name = cell_value_8
            domain.save()
            updatedDomain_R[cell_value_8] = domain 
            updatedDomain_R[cell_value_8].save() 
            project.updatedDomain = domain
            project.save()
        if cell_value_8 in updatedDomain_R:
            project.updatedDomain = updatedDomain_R[cell_value_8]
            project.save()
        project.code = cell_value_0
        project.foundPoints = cell_value_1
        project.name = cell_value_6
        cel = str(cell_value_9)
        pp = (cel[:4])     
        project.year = str(pp) + '-01-01'
        project.par = cell_value_10
        if cell_value_11 == '':
            project.longitude = 0
        if cell_value_11 != '':
            project.longitude = cell_value_11
        if cell_value_12 == '':
            project.longitude = 0
        if cell_value_12 != '':
            project.longitude = cell_value_12
        if cell_value_13 != '':
            project.latitude = cell_value_13 
        if cell_value_13 == '':
            project.latitude = 0
        project.save()
        curr_row = curr_row + 1 
    return Response({'ok': 'Fichier téléversé avec succès'}, status=status.HTTP_200_OK)
 

@api_view(['GET'])
def get_user(request):
    serializer = UserProfileSerializer(request.user)
    return Response(serializer.data)



 




