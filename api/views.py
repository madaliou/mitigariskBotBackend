from datetime import date
#from os import name, removexattr
from re import T
from unicodedata import category
from django.shortcuts import render, get_object_or_404
from django.core.mail import EmailMultiAlternatives
from django.template.context import RequestContext
from django.urls.base import translate_url
from .models import UserProfile, Type, Category, Ticket, Reply, Gravity
from .serializers import UserProfileSerializer, UserProfileReadSerializer, ChangePasswordSerializer
from .serializers import TypeReadSerializer, CategoryReadSerializer, TicketReadSerializer, ReplyReadSerializer, GravityReadSerializer
from .serializers import TypeSerializer, CategorySerializer, TicketSerializer, RegisterSerializer, ReplySerializer, GravitySerializer
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
#import xlrd
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
    permission_classes = (AllowAny,)

    queryset = Category.objects.all().order_by('id') 

    def get_serializer_class(self):
        
        if self.request.method in ['GET']:
            
            return CategoryReadSerializer
        return CategorySerializer

class TypeViewSet(viewsets.ModelViewSet):
    permission_classes = (AllowAny,)
    queryset = Type.objects.all().order_by('id') 

    def get_serializer_class(self):
        
        if self.request.method in ['GET']:
            
            return TypeReadSerializer
        return TypeSerializer

class UserProfileViewSet(viewsets.ModelViewSet):
    queryset = UserProfile.objects.all()
    def get_serializer_class(self):
        if self.request.method in ['GET']:
            return UserProfileReadSerializer
        return UserProfileSerializer

class GravityViewSet(viewsets.ModelViewSet):
    serializer_class = GravityReadSerializer    
    def get_queryset(self):
        #if (self.request.user.role == 'admin'):
            gravities = Gravity.objects.all()
            return gravities
        #else:
            #gravities = Gravity.objects.filter(type=self.request.user.id)
            #return gravities

    def create(self, request, *args, **kwargs):    
        data = {
            'name': request.data['name'],          
            'description': request.data['description'],  
            #'type': request.data['type']            
        }
        serializer = GravityReadSerializer(data=data)
        if serializer.is_valid():
            instance = serializer.save() 
            #instance.type = Type.objects.get(id = request.data['type'] )              
            instance.save()
            show = GravityReadSerializer(instance)
            return Response(show.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        data = {
            'name': request.data['name'],          
            'description': request.data['description'],  
            #'type': request.data['type'],   
        }
        serializer = GravityReadSerializer(instance, data=data)
        if serializer.is_valid():
            instance = serializer.save()   
            #instance.type = Type.objects.get(id = request.data['type'] )  
            instance.save()
            show = GravityReadSerializer(instance)
            return Response(show.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class BotSolutionViewSet(viewsets.ModelViewSet):
    permission_classes = (AllowAny,)
    queryset = Gravity.objects.all().order_by('-id') 

    def get_serializer_class(self):
        
        if self.request.method in ['GET']:
            
            return GravityReadSerializer
        return GravitySerializer   
    

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
            'correction': request.data['correction'], 
            'proceedings': request.data['proceedings'], 
            'lostOfHumanlifes': request.data['lostOfHumanlifes'],  
            'injuries': request.data['injuries'], 
            'gravity': request.data['gravity'],   
            'type': request.data['type'],           
            'reference': uuid.uuid4().hex[:10],
            'author': request.user.id

        }
        print('ccccccccccccccccccccccccc', request.data['category'],)
        serializer = TicketReadSerializer(data=data)
        if serializer.is_valid():
            instance = serializer.save() 
            instance.category = Category.objects.get(id = request.data['category'] )  
            instance.gravity = Gravity.objects.get(id = request.data['gravity'] )      
            instance.type = Type.objects.get(id = request.data['type'] )  
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
            'gravity': request.data['gravity'], 
            'type': request.data['type'],                    
            'author': request.user.id
        }
        serializer = TicketReadSerializer(instance, data=data)
        if serializer.is_valid():
            instance = serializer.save()   
            instance.category = Category.objects.get(id = request.data['category'] )  
            instance.gravity = Gravity.objects.get(id = request.data['gravity'] )    
            instance.type = Gravity.objects.get(id = request.data['type'] )         
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
            return Response({"message": ["Vous n\'etes pas autoris?? ?? effectuer cette action"]}, status=status.HTTP_400_BAD_REQUEST) 
        userr =  UserProfile.objects.get(phoneNumber=request.data['phoneNumber'])

        print('userrrrrrrrrrrrrrrrrrrrrrrrrrrr', userr)
        
        data = {
            'category': request.data['category'],          
            'description': request.data['description'],  
            'gravity': request.data['gravity'],   
            'type': request.data['type'],     
            'lostOfHumanlifes': request.data['lostOfHumanlifes'],  
            'injuries': request.data['injuries'],               
            'reference': uuid.uuid4().hex[:10],
            'author': userr

        }    
        category =  Category.objects.filter(id=request.data['category'] ).first()
 
        if category is None:
            return Response({"message": ["Cette cat??gorie n'existe pas"]}, status=status.HTTP_400_BAD_REQUEST) 
        
        gravity =  Gravity.objects.filter(id=request.data['gravity'] ).first()
 
        if gravity is None:
            return Response({"message": ["Cette Gravit?? n'existe pas"]}, status=status.HTTP_400_BAD_REQUEST) 

        type =  Type.objects.filter(id=request.data['type']).first()
 
        if type is None:
            return Response({"message": ["Ce type n'existe pas"]}, status=status.HTTP_400_BAD_REQUEST) 

        serializer = TicketReadSerializer(data=data)
        if serializer.is_valid():
            instance = serializer.save() 
            instance.category = Category.objects.get(id = request.data['category'] )  
            instance.gravity = Gravity.objects.get(id = request.data['gravity'] )  
            instance.phoneNumber = request.data['phoneNumber']    
            instance.platform = request.data['platform']
            instance.proceedings = request.data['proceedings']
            instance.correction = request.data['correction']
            instance.lostOfHumanlifes = request.data['lostOfHumanlifes']
            instance.injuries = request.data['injuries']  
            instance.type = Type.objects.get(id = request.data['type'] ) 
            instance.urgency = 1   
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
            # Verifier le nombre de caract??re du mot de passe
            if len(request.data['password']) < 8:
                return Response({"message": ["Ce mot de passe est trop court. Il doit contenir au minimum 8 caract??res!"]}, status=status.HTTP_400_BAD_REQUEST)
            # Verifier l'ancien mot de passe
            if self.object.check_password(serializer.data.get("password")):
                return Response({"message": ["Veuillez choisir un mot de passe autre que l'ancien !"]}, status=status.HTTP_400_BAD_REQUEST)
            self.object.set_password(serializer.data.get("password"))
            self.object.passwordChanged = 1
            self.object.save()
            response = {
                'status': 'success',
                'code': status.HTTP_200_OK,
                'message': 'Mot de passe chang?? avec succ??s',
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

# tiquets trait??s
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

# tiquets urgents
@api_view(['GET'])
def urgent_tickets(request):
    tickets = Ticket.objects.filter(urgency=1)                     
    serializer = TicketReadSerializer(tickets, many=True)    
    return Response(serializer.data)

# tiquets non urgents
@api_view(['GET'])
def not_urgent_tickets(request):
    tickets = Ticket.objects.filter(urgency=0)                     
    serializer = TicketReadSerializer(tickets, many=True)    
    return Response(serializer.data)

#Dashboard Admin
@api_view(['GET'])
def dashboard(request):
    total_tickets = Ticket.objects.filter().count()
    fixed_tickets = Ticket.objects.filter(fixed=2).count()
    unfixed_tickets = Ticket.objects.filter(fixed=0).count()
    infixing_tickets = Ticket.objects.filter(fixed=1).count()
    types = Type.objects.all().count()

    return Response({
        'fixed_tickets': fixed_tickets,
        'unfixed_tickets': unfixed_tickets,
        'infixing_tickets': infixing_tickets,
        'total_tickets': total_tickets,
        'types': types,

    })


# User's type solutions
@api_view(['POST'])
@permission_classes([AllowAny])
def user_solutions(request):
    user = UserProfile.objects.filter(phoneNumber=request.data['phoneNumber'])  
    if len(user) > 0:  
        gravities = Gravity.objects.distinct().filter(type__users__phoneNumber=request.data['phoneNumber'])
    else :
        return Response({"message": ["Utilisateur inconu !"]}, status=status.HTTP_400_BAD_REQUEST)
    
    serializer = GravityReadSerializer(gravities, many=True)    
    return Response(serializer.data)

# Suivi ticket
@api_view(['POST'])
@permission_classes([AllowAny])
def track_ticket(request):
    ticket = Ticket.objects.get(reference=request.data['reference']) 
    print(ticket) 
    fixed = ticket.fixed
    
    return Response({
        'fixed': fixed        

    })
