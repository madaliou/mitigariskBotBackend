from os import truncate
from django.utils import tree
from rest_framework import serializers
from rest_framework.fields import ReadOnlyField
from .models import UserProfile, Picture, Domain, Project, Region, Prefecture, Commune, Canton, Locality
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
        fields = ('id', 'first_name', 'last_name', 'username', 'fullName', 'email', 'phoneNumber', 'role', 'passwordChanged', 'value', 'label','author', 'created_at', 'updated_at')   
 
class UserProfileSerializer(serializers.ModelSerializer):
    class Meta(object):
        model = UserProfile
        #extra_kwargs = {'password': {'write_only': True}}
        fields = ('first_name', 'last_name', 'username', 'email', 'phoneNumber', 'fullName', 'role', 'passwordChanged')
    
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

class RegionReadSerializer(serializers.ModelSerializer):   
    class Meta:
        model = Region
        fields = ('id', 'name', 'label', 'value', 'nbOfProjects', 'created_at', 'updated_at')   
   
class RegionSerializer(serializers.ModelSerializer):
    class Meta(object):
        model = Region
        fields = '__all__'

class PrefectureReadSerializer(serializers.ModelSerializer):   
    class Meta:
        model = Prefecture
        fields = ('id', 'name', 'label', 'region', 'value', 'nbOfProjects', 'created_at', 'updated_at')   
        depth = 10
 
   
class PrefectureSerializer(serializers.ModelSerializer):
    class Meta(object):
        model = Prefecture
        fields = '__all__'


class CommuneReadSerializer(serializers.ModelSerializer):   
    class Meta:
        model = Commune
        fields = ('id', 'name', 'label', 'value', 'nbOfProjects', 'prefecture', 'created_at', 'updated_at')   
        depth = 10
   
class CommuneSerializer(serializers.ModelSerializer):
    class Meta(object):
        model = Commune
        fields = '__all__'

class CantonReadSerializer(serializers.ModelSerializer):   
    class Meta:
        model = Canton
        fields = ('id', 'name', 'label', 'commune', 'nbOfProjects', 'value','created_at', 'updated_at')   
        depth = 10
   
class CantonSerializer(serializers.ModelSerializer):
    class Meta(object):
        model = Canton
        fields = '__all__'

class LocalityReadSerializer(serializers.ModelSerializer):   
    class Meta:
        model = Locality
        fields = ('id', 'name', 'label', 'value', 'canton', 'nbOfProjects', 'created_at', 'updated_at')   
        depth = 10
   
class LocalitySerializer(serializers.ModelSerializer):
    class Meta(object):
        model = Locality
        fields = '__all__'
        depth = 10
          
class DomainReadSerializer(serializers.ModelSerializer):   
    class Meta:
        model = Domain
        fields = ('id', 'name', 'label', 'value', 'created_at', 'updated_at')   
   
class DomainSerializer(serializers.ModelSerializer):
    class Meta(object):
        model = Domain
        fields = '__all__'      
  
class ProjectReadSerializer(serializers.ModelSerializer): 
    projectPictures = PictureReadSerializer(many=True, read_only=True)
    class Meta:
        model = Project
        fields = ('id', 'code', 'key', 'content', 'name', 'updatedDomain', 'locality', 'year', 'number', 'par', 'longitude', 'latitude', 'position', 'value', 'projectPictures', 'created_at', 'updated_at')   
        depth = 10

class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = '__all__'      
