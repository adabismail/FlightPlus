from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import User
 
class RegisterSerializer(serializers.ModelSerializer):
    password  = serializers.CharField(write_only=True, min_length=8)
    password2 = serializers.CharField(write_only=True)
 
    class Meta:
        model  = User
        fields = ('email','name','phone','password','password2',
                  'currency','notify_email','notify_sms')
 
    def validate(self, attrs):
        # called automatically — raises error if passwords don't match
        if attrs['password'] != attrs.pop('password2'):
            raise serializers.ValidationError({'password': 'Passwords do not match.'})
        return attrs
 
    def create(self, validated_data):
        # calls our custom create_user which hashes the password
        return User.objects.create_user(**validated_data)
 
 
class LoginSerializer(serializers.Serializer):
    email    = serializers.EmailField()
    password = serializers.CharField()
 
    def validate(self, attrs):
        # authenticate() checks email+password against the database
        user = authenticate(username=attrs['email'], password=attrs['password'])
        if not user:
            raise serializers.ValidationError('Invalid email or password.')
        attrs['user'] = user
        return attrs
 
 
class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model  = User
        fields = ('id','email','name','phone','currency',
                  'notify_email','notify_sms','date_joined')
        read_only_fields = ('id','email','date_joined')  # can't change these
