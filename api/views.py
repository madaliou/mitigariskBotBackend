from datetime import date
from os import name, removexattr
from django.shortcuts import render, get_object_or_404
from django.core.mail import EmailMultiAlternatives
from django.template.context import RequestContext
from django.urls.base import translate_url
from .models import UserProfile, Project, Domain, Picture
from .serializers import UserProfileSerializer, UserProfileReadSerializer, ProjectSerializer, ProjectReadSerializer, DomainSerializer, DomainReadSerializer
from .serializers import PictureSerializer, PictureReadSerializer
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

class DomainViewSet(viewsets.ModelViewSet):
    queryset = Domain.objects.all()

    def get_serializer_class(self):
        if self.request.method in ['GET']:
            return DomainReadSerializer
        return DomainSerializer

class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.all()

    def get_serializer_class(self):
        if self.request.method in ['GET']:
            return ProjectReadSerializer
        return ProjectSerializer
    
    def create(self, request, *args, **kwargs):        
        data = { 
                'updatedDomain': request.data['updatedDomain'],
                'structure': request.data['structure'],
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
                'updatedDomain': request.data['updatedDomain'],
                'structure': request.data['structure'],
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
@api_view(['POST'])
def import_projects(request):        
    """ excel_file = request.FILES["excel_file"]  
    df = pd.read_excel(excel_file)
    index_sheet2 = 0  """
    workbook = xlrd.open_workbook('/home/moozistudio/Bureau/Table_donnees.xlsx')
    SheetNameList = workbook.sheet_names()
    worksheet = workbook.sheet_by_name(SheetNameList[0])
    num_rows = worksheet.nrows 
    num_cells = worksheet.ncols 
    print('num_rows, num_cells', num_rows, num_cells )
    updatedDomain_R={}
    curr_row = 1
    while curr_row < num_rows:
        cell_value_0 = worksheet.cell_value(curr_row, 0)
        cell_value_1 = worksheet.cell_value(curr_row, 1)
        cell_value_2 = worksheet.cell_value(curr_row, 2)
        cell_value_3 = worksheet.cell_value(curr_row, 3)
        cell_value_4 = worksheet.cell_value(curr_row, 4)
        cell_value_5 = worksheet.cell_value(curr_row, 5)
        cell_value_6 = worksheet.cell_value(curr_row, 6)
        # Région curr_cell == 3          
        project = Project()
        if cell_value_2 not in updatedDomain_R:
            domain = Domain()
            domain.name = cell_value_2
            domain.save()
            updatedDomain_R[cell_value_2] = domain 
            project.updatedDomain = domain
        if cell_value_2  in updatedDomain_R:
            project.updatedDomain = updatedDomain_R[cell_value_2]
        cel = str(cell_value_3)
        pp = (cel[:4])     
        project.year = str(pp) + '-01-01'
        project.structure  = cell_value_4
        print('pppppppppppppppppppppppppppppppppppppppppppppppp', curr_row)
        if cell_value_5 == '':
            project.longitude = 0
        if cell_value_5 != '':
            project.longitude = cell_value_5 
        if cell_value_6 == '':
            project.latitude = 0
        if cell_value_6 != '':
            project.latitude = cell_value_6 
        project.save()
        curr_row = curr_row + 1 
    #df.to_csv("/home/moozistudio/Bureau/assurtrans/mtn/" + str(your) + str(excel_file), index=False) 
    return Response({'ok': 'Fichier téléversé avec succès'}, status=status.HTTP_200_OK)
 

@api_view(['GET'])
def get_user(request):
    serializer = UserProfileSerializer(request.user)
    return Response(serializer.data)



 




