import random
from rest_framework import serializers
from .models import User
from .models import Candidate
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken

class SignupSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['name', 'email', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        # Generate username from email (part before @)
        email = validated_data['email']
        username = email.split('@')[0]
        
        # If username already exists, append numbers until we find a unique one
        base_username = username
        num = random.randint(10, 99)
        while User.objects.filter(username=username).exists():
            username = f"{base_username}{num}"
            
        # Add the generated username to validated_data
        validated_data['username'] = username
        
        # Create the user
        user = User.objects.create_user(**validated_data)
        return user

class CandidateRegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Candidate
        fields = ['username', 'photo', 'phone', 'website', 'socials',
                  'skills', 'resume', 'bio']

    def create(self, validated_data):
        # Create Candidate using multi-table inheritance
        candidate = Candidate.objects.create_user(
            username=validated_data['username'],
            photo=validated_data.get('photo'),
            phone=validated_data.get('phone', ''),
            website=validated_data.get('website', ''),
            socials=validated_data.get('socials', {}),
            role='candidate'
        )
        candidate.skills = validated_data.get('skills', '')
        candidate.resume = validated_data.get('resume')
        candidate.bio = validated_data.get('bio', '')
        candidate.save()
        return candidate

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        email = data.get("email")
        password = data.get("password")

        if not email or not password:
            raise serializers.ValidationError("Must provide both email and password")

        # Try to get the user first
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError("No user found with this email")

        # Authenticate using the username we got from the user object
        user = authenticate(username=user.username, password=password)
            
        if not user:
            raise serializers.ValidationError("Invalid credentials")

        # Generate Tokens
        refresh = RefreshToken.for_user(user)

        return {
            "user": {
                "id": user.id,
                "email": user.email,
                "role": user.role,
                "name": user.name,
            },
            "access": str(refresh.access_token),
            "refresh": str(refresh),
        }
