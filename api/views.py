from datetime import date
from os import name, removexattr
from django.shortcuts import render, get_object_or_404
from django.core.mail import EmailMultiAlternatives
from django.template.context import RequestContext
from django.urls.base import translate_url
from .models import UserProfile, Company, Category, Ticket, Reply, Solution
from .serializers import UserProfileSerializer, UserProfileReadSerializer, ChangePasswordSerializer
from .serializers import CompanyReadSerializer, CategoryReadSerializer, TicketReadSerializer, ReplyReadSerializer, SolutionReadSerializer
from .serializers import CompanySerializer, CategorySerializer, TicketSerializer, RegisterSerializer, ReplySerializer, SolutionSerializer
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

class CategoryViewSet(viewsets.ModelViewSet):

    queryset = Category.objects.all().order_by('-id') 

    def get_serializer_class(self):
        
        if self.request.method in ['GET']:
            
            return CategoryReadSerializer
        return CategorySerializer

class CompanyViewSet(viewsets.ModelViewSet):
    permission_classes = (AllowAny,)
    queryset = Company.objects.all().order_by('-id') 

    def get_serializer_class(self):
        
        if self.request.method in ['GET']:
            
            return CompanyReadSerializer
        return CompanySerializer

class UserProfileViewSet(viewsets.ModelViewSet):
    queryset = UserProfile.objects.all()
    def get_serializer_class(self):
        if self.request.method in ['GET']:
            return UserProfileReadSerializer
        return UserProfileSerializer

class SolutionViewSet(viewsets.ModelViewSet):
    serializer_class = SolutionReadSerializer    
    def get_queryset(self):
        if (self.request.user.role == 'admin'):
            solutions = Solution.objects.all()
            return solutions
        else:
            solutions = Solution.objects.filter(company=self.request.user.company.id)
            return solutions

    def create(self, request, *args, **kwargs):    
        data = {
            'name': request.data['name'],          
            'description': request.data['description'],  
            'company': request.data['company']            
        }
        serializer = SolutionReadSerializer(data=data)
        if serializer.is_valid():
            instance = serializer.save() 
            instance.company = Company.objects.get(id = request.data['company'] )              
            instance.save()
            show = SolutionReadSerializer(instance)
            return Response(show.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        data = {
            'name': request.data['name'],          
            'description': request.data['description'],  
            'company': request.data['company'],   
        }
        serializer = SolutionReadSerializer(instance, data=data)
        if serializer.is_valid():
            instance = serializer.save()   
            instance.company = Company.objects.get(id = request.data['company'] )  
            instance.save()
            show = SolutionReadSerializer(instance)
            return Response(show.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TicketViewSet(viewsets.ModelViewSet):
    serializer_class = TicketReadSerializer    
    def get_queryset(self):
        if (self.request.user.role == 'admin'):
            tickets = Ticket.objects.all()
            return tickets
        else:
            tickets = Ticket.objects.filter(author=self.request.user.id)
            return tickets

    def create(self, request, *args, **kwargs):    
        data = {
            'category': request.data['category'],          
            'description': request.data['description'],  
            'solution': request.data['solution'],            
            'reference': uuid.uuid4().hex[:10],
            'author': request.user.id

        }
        print('ccccccccccccccccccccccccc', request.data['category'],)
        serializer = TicketReadSerializer(data=data)
        if serializer.is_valid():
            instance = serializer.save() 
            instance.category = Category.objects.get(id = request.data['category'] )  
            instance.solution = Solution.objects.get(id = request.data['solution'] )      
            instance.author = request.user   
            instance.save()
            show = TicketReadSerializer(instance)
            return Response(show.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        data = {
            'category': request.data['category'],
            'description': request.data['description'],  
            'solution': request.data['solution'],                   
            'author': request.user.id
        }
        serializer = TicketReadSerializer(instance, data=data)
        if serializer.is_valid():
            instance = serializer.save()   
            instance.category = Category.objects.get(id = request.data['category'] )  
            instance.solution = Solution.objects.get(id = request.data['solution'] )         
            instance.author = request.user         
            instance.save()
            show = TicketReadSerializer(instance)
            return Response(show.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class BotTicketViewSet(viewsets.ModelViewSet):
    permission_classes = (AllowAny,)
    serializer_class = TicketReadSerializer    
    def get_queryset(self):
        if (self.request.user.role == 'admin'):
            tickets = Ticket.objects.all()
            return tickets
        else:
            tickets = Ticket.objects.filter(author=self.request.user.id)
            return tickets

    def create(self, request, *args, **kwargs):   
        user =  UserProfile.objects.filter(phoneNumber=request.data['phoneNumber'] ).first()
        if user is None:
            return Response({"message": ["Vous n\'etes pas autorisé à effectuer cette action"]}, status=status.HTTP_400_BAD_REQUEST) 
        userr =  UserProfile.objects.get(phoneNumber=request.data['phoneNumber'])

        print('userrrrrrrrrrrrrrrrrrrrrrrrrrrr', userr)
        
        data = {
            'category': request.data['category'],          
            'description': request.data['description'],  
            'solution': request.data['solution'],            
            'reference': uuid.uuid4().hex[:10],
            'author': userr

        }     
        serializer = TicketReadSerializer(data=data)
        if serializer.is_valid():
            instance = serializer.save() 
            instance.category = Category.objects.get(id = request.data['category'] )  
            instance.solution = Solution.objects.get(id = request.data['solution'] )  
            instance.phoneNumber = request.data['phoneNumber']    
            instance.platform = request.data['platform']    
            instance.author = userr   
            instance.save()
            show = TicketReadSerializer(instance)
            return Response(show.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)         

class ReplyViewSet(viewsets.ModelViewSet):
    serializer_class = ReplyReadSerializer    
    def get_queryset(self):
        if (self.request.user.role == 'admin'):
            replies = Reply.objects.all()
            return replies
        else:
            replies = Reply.objects.filter(ticket__author__id=self.request.user.id)
            return replies
    
    def create(self, request, *args, **kwargs):    
        data = {
            'ticket_id': request.data['ticket'],          
            'message': request.data['message'],            
        }
        serializer = ReplyReadSerializer(data=data)
        if serializer.is_valid():
            instance = serializer.save() 
            instance.ticket = Ticket.objects.get(id = request.data['ticket'] )  
            instance.message = request.data['message']    
            instance.save()
            tic = Ticket.objects.get(id = request.data['ticket'] )
            email = tic.author.email
            print(email)
            objet = 'AppSupport'
            message = get_template('email/reply_mail_template.html').render(data)
            msg = EmailMessage(
                objet,
                message,
                'test.transvie@gmail.com',
                [email],
            )
            msg.content_subtype = "html"  # Main content is now text/html
            msg.send()
            print("Mail successfully sent")

            show = ReplyReadSerializer(instance)
            return Response(show.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        data = {
            'ticket': request.data['ticket'],          
            'message': request.data['message'],            
        }
        serializer = ReplyReadSerializer(instance, data=data)
        if serializer.is_valid():
            instance = serializer.save()   
            instance.ticket = Ticket.objects.get(id = request.data['ticket'] )  
            instance.message = request.data['message']       
            instance.save()
            show = ReplyReadSerializer(instance)
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


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = RegisterSerializer

@api_view(['GET'])
def get_user(request):
    serializer = UserProfileSerializer(request.user)
    return Response(serializer.data)

# Traiter un tiquet
@api_view(['POST'])
def begin_fixing_ticket(request):
    ticket = Ticket.objects.get(id=request.data['ticket'])   
    if ticket is not None :
        if ticket.fixed == 0:     
            ticket.fixed=1
            ticket.save()        
    serializer = TicketReadSerializer(ticket, many=False)    
    return Response(serializer.data)        

# Traiter un tiquet
@api_view(['POST'])
def begin_unfixing_ticket(request):
    ticket = Ticket.objects.get(id=request.data['ticket'])   
    if ticket is not None :
        if ticket.fixed == 1:
            ticket.fixed=0     
            ticket.save()            
    serializer = TicketReadSerializer(ticket, many=False)    
    return Response(serializer.data)

# tiquet en cours
@api_view(['POST'])
def fix_ticket(request):
    ticket = Ticket.objects.get(id=request.data['ticket'])   
    if ticket is not None :
        if ticket.fixed == 1:        
            ticket.fixed=2        
    ticket.save()                  
    serializer = TicketReadSerializer(ticket, many=False)    
    return Response(serializer.data)

# tiquet en cours
@api_view(['POST'])
def unfix_ticket(request):
    ticket = Ticket.objects.get(id=request.data['ticket'])   
    if ticket is not None :
        if ticket.fixed == 2:
            ticket.fixed=1          
    ticket.save()                  
    serializer = TicketReadSerializer(ticket, many=False)    
    return Response(serializer.data)

# tiquets traités
@api_view(['GET'])
def fixed_tickets(request):
    ticket = Ticket.objects.filter(fixed=2)                     
    serializer = TicketReadSerializer(ticket, many=True)    
    return Response(serializer.data)

# tiquets en cours de traitement
@api_view(['GET'])
def infinxing_tickets(request):
    ticket = Ticket.objects.filter(fixed=1)                     
    serializer = TicketReadSerializer(ticket, many=True)    
    return Response(serializer.data)

# tiquets en cours de traitement
@api_view(['GET'])
def unfixed_tickets(request):
    ticket = Ticket.objects.filter(fixed=0)                     
    serializer = TicketReadSerializer(ticket, many=True)    
    return Response(serializer.data)

# message lus
@api_view(['POST'])
def read_reply(request):
    ticket = Reply.objects.get(id=request.data['id'])   
    if ticket is not None :
        if ticket.read == 0:        
            ticket.read=1                
    ticket.save()                  
    serializer = ReplyReadSerializer(ticket, many=False)    
    return Response(serializer.data)

#Dashboard Admin
@api_view(['GET'])
def dashboard(request):
    fixed_tickets = Ticket.objects.filter(fixed=True).count()
    unfixed_tickets = Ticket.objects.filter(fixed=False).count()
    companies = Company.objects.all().count()

    return Response({
        'fixed_tickets': fixed_tickets,
        'unfixed_tickets': unfixed_tickets,
        'companies': companies,

    })