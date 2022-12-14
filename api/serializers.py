from logging.config import valid_ident
from os import truncate
from django.utils import tree
from rest_framework import serializers
from rest_framework.fields import ReadOnlyField
from .models import UserProfile, Picture, Type, Category, Ticket, Reply, Gravity
from django.contrib.auth import get_user_model
from rest_framework.validators import UniqueValidator
from django.contrib.auth.password_validation import validate_password
from django.template.loader import render_to_string, get_template
from django.core.mail import EmailMessage


class PictureSerializer(serializers.ModelSerializer):
    class Meta:
        model = Picture
        fields = '__all__'

class PictureReadSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField('get_picture_url')
    class Meta:
        model = Picture
        exclude = ('name', ) 

    def get_picture_url(self, request):
        name = request.name.url
        return name
        
class CustomTokenSerializer(serializers.Serializer):
    token = serializers.CharField()


class TypeReadSerializer(serializers.ModelSerializer):  
    #users = UserProfileReadSerializer(many=True, read_only=True) 
    class Meta:
        model = Type
        fields = ('id', 'name', 'description', 'created_at', 'updated_at')   
   
class TypeSerializer(serializers.ModelSerializer):
    class Meta(object):
        model = Type
        fields = '__all__'

class TicketReadSerializer(serializers.ModelSerializer):  
    class Meta:
        model = Ticket
        fields = '__all__'          
        depth = 10

class UserProfileReadSerializer(serializers.ModelSerializer):  
    #type = TypeReadSerializer(many=False, read_only=True)
    tickets = TicketReadSerializer(many=True, read_only=True)
    class Meta:
        model = UserProfile
        fields = ('id',  'first_name', 'last_name', 'email', 'role', 'passwordChanged', 'author', 'tickets', 'phoneNumber', 'created_at', 'updated_at') 
        depth = 10  
 
class UserProfileSerializer(serializers.ModelSerializer):
    class Meta(object):
        model = UserProfile
        #extra_kwargs = {'password': {'write_only': True}}
        fields = ('first_name', 'last_name', 'email', 'phoneNumber', 'role', 'passwordChanged')
    
    def create(self, validated_data):    

        if validated_data['role']=='admin':
            user = UserProfile()
            user.passwordChanged = True
            user.first_name = validated_data['first_name']
            user.last_name = validated_data['last_name']
            user.username = validated_data['email']
            user.email = validated_data['email']
            user.role = validated_data['role']
            user.phoneNumber = (validated_data['phoneNumber']).replace(" ", "")
            #user = super().create(validated_data)
            user.set_password('admin123')
            user.save()
            print('.strip().strip().strip().strip()', user.phoneNumber)
        if validated_data['role'] == 'user':
            user = UserProfile()
            user.first_name = validated_data['first_name']
            user.last_name = validated_data['last_name']
            #user.type = validated_data['type']
            user.username = validated_data['email']
            user.email = validated_data['email']
            user.role = validated_data['role']
            user.phoneNumber = (validated_data['phoneNumber']).replace(" ", "")

            #user = super().create(validated_data)
            password = UserProfile.objects.make_random_password(length=8,
                                                                allowed_chars='abcdefghijklmnopqrstuvwxyz'
                                                                'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789')
            print('password', password)
            objet = 'AppSupport'
                #passwordSend = password

                ##context={'user_name': validated_data['username']}

            ctx = {
                'first_name': validated_data['first_name'],
                'last_name': validated_data['last_name'],
                'user_name': validated_data['email'],
                'password': password
            }
            message = get_template('email/mail_template.html').render(ctx)
            msg = EmailMessage(
                objet,
                message,
                'test.transvie@gmail.com',
                [validated_data['email']],
            )
            msg.content_subtype = "html"  # Main content is now text/html
            msg.send()
            user.set_password(password)
            user.save()
            print("Mail successfully sent")
        user.save()
        

        return user
    
    def update(self, instance, validated_data):    
        tmp = instance.passwordChanged
        user = super().update(instance, validated_data)
        user.username = user.email
        user.phoneNumber = (validated_data['phoneNumber']).replace(" ", "")
        user.passwordChanged = tmp
        try:
            user.save()
        except KeyError:
            pass
        return user  


class RegisterSerializer(serializers.ModelSerializer):
    
    email = serializers.EmailField(
            required=True,
            validators=[UniqueValidator(queryset=UserProfile.objects.all())]
            )

    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = UserProfile
        fields = ('id','first_name', 'last_name', 'email', 'password' )
        extra_kwargs = {
            'first_name': {'required': True},
            'last_name': {'required': True}
        }


    def create(self, validated_data):
        user = UserProfile.objects.create(
            email=validated_data['email'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],

        )        
        user.set_password(validated_data['password'])
        user.role = 'contributor'
        user.save()

        return user     


class TicketReadSerializer(serializers.ModelSerializer):   
    class Meta:
        model = Ticket
        fields = '__all__'          
        

class CategoryReadSerializer(serializers.ModelSerializer):   
    tickets = TicketReadSerializer(many=True, read_only=True)
    class Meta:
        model = Category
        fields = '__all__'          
        depth = 10
  
   
class CategorySerializer(serializers.ModelSerializer):
    class Meta(object):
        model = Category
        fields = '__all__'    

class GravityReadSerializer(serializers.ModelSerializer):   
    class Meta:
        model = Gravity
        fields = '__all__'          
        depth = 10
  
   
class GravitySerializer(serializers.ModelSerializer):
    class Meta(object):
        model = Gravity
        fields = '__all__'          

class TicketReadSerializer(serializers.ModelSerializer):  
    author = UserProfileReadSerializer(many=False, read_only=True) 
    gravity = GravityReadSerializer(many=False, read_only=True) 

    class Meta:
        model = Ticket
        fields = '__all__'          
        depth = 10
   
class TicketSerializer(serializers.ModelSerializer):
    class Meta(object):
        model = Ticket
        fields = ('id','description', 'category', 'gravity')

class ReplyReadSerializer(serializers.ModelSerializer):  
    author = UserProfileReadSerializer(many=False, read_only=True) 
    ticket = TicketReadSerializer(many=False, read_only=True) 
    class Meta:
        model = Reply
        fields = '__all__'          
        depth = 10
   
class ReplySerializer(serializers.ModelSerializer):
    class Meta(object):
        model = Reply
        fields = ('id','message', 'ticket')

class ChangePasswordSerializer(serializers.Serializer):
    model = UserProfile

    password = serializers.CharField(required=True)