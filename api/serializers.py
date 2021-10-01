from os import truncate
from django.utils import tree
from rest_framework import serializers
from rest_framework.fields import ReadOnlyField
from .models import UserProfile, Picture, Domain, Project
from django.contrib.auth import get_user_model
from rest_framework.validators import UniqueValidator
from django.contrib.auth.password_validation import validate_password

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

class UserProfileReadSerializer(serializers.ModelSerializer):  
    class Meta:
        model = UserProfile
        fields = ('id', 'first_name', 'last_name', 'username', 'fullName', 'email', 'phoneNumber', 'birthDate', 'role', 'passwordChanged', 'author', 'created_at', 'updated_at')   
 
class UserProfileSerializer(serializers.ModelSerializer):
    class Meta(object):
        model = UserProfile
        #extra_kwargs = {'password': {'write_only': True}}
        fields = ('first_name', 'last_name', 'username', 'email', 'phoneNumber', 'fullName', 'birthDate', 'role', 'passwordChanged')
    
    def create(self, validated_data):
        user = super().create(validated_data)
        user.set_password('admin123')
        if validated_data['role']=='admin':
            user.passwordChanged = True
        user.save()
        return user
    
    def update(self, instance, validated_data):
        user = super().update(instance, validated_data)
        try:
            user.save()
        except KeyError:
            pass
        return user  
          
class DomainReadSerializer(serializers.ModelSerializer):   
    class Meta:
        model = Domain
        fields = '__all__'   
   
class DomainSerializer(serializers.ModelSerializer):
    class Meta(object):
        model = Domain
        fields = '__all__'      
  
class ProjectReadSerializer(serializers.ModelSerializer): 
    class Meta:
        model = Project
        fields = '__all__'      
        depth = 10

class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = '__all__'      
