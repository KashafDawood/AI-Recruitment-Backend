import random
from rest_framework import serializers
from .models import User
from .models import CandidateProfile, EmployerProfile
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken

class SignupSerializer(serializers.ModelSerializer):
    # Fields for basic user registration
    role = serializers.ChoiceField(
        choices=User.ROLE_CHOICES,
        required=True,
        allow_null=False
    )
    password = serializers.CharField(write_only=True)
    
    # Optional fields for candidate profile
    skills = serializers.CharField(required=False, allow_blank=True)
    resume = serializers.FileField(required=False, allow_null=True)
    bio = serializers.CharField(required=False, allow_blank=True)
    
    # Optional fields for employer profile
    company_name = serializers.CharField(required=False, allow_blank=True)
    industry = serializers.CharField(required=False, allow_blank=True)
    logo = serializers.ImageField(required=False, allow_null=True)

    class Meta:
        model = User
        fields = [
            # Basic user fields
            'name', 'email', 'password', 'role',
            # Candidate profile fields
            'skills', 'resume', 'bio',
            # Employer profile fields
            'company_name', 'industry', 'logo'
        ]

    def validate(self, data):
        if not data.get('role'):
            raise serializers.ValidationError({
                "role": "Role is required for registration"
            })
            
        role = data.get('role')
        
        # Validate candidate-specific fields
        if role == 'candidate':
            if not data.get('skills'):
                raise serializers.ValidationError({
                    "skills": "Skills are required for candidate registration"
                })
        
        # Validate employer-specific fields
        elif role == 'employer':
            if not data.get('company_name'):
                raise serializers.ValidationError({
                    "company_name": "Company name is required for employer registration"
                })
            if not data.get('industry'):
                raise serializers.ValidationError({
                    "industry": "Industry is required for employer registration"
                })
        
        return data

    def create(self, validated_data):
        # Extract profile-specific data
        role = validated_data.get('role')
        
        # Extract and remove profile fields from validated_data
        candidate_fields = {
            'skills': validated_data.pop('skills', ''),
            'resume': validated_data.pop('resume', None),
            'bio': validated_data.pop('bio', '')
        }
        
        employer_fields = {
            'company_name': validated_data.pop('company_name', ''),
            'industry': validated_data.pop('industry', ''),
            'logo': validated_data.pop('logo', None)
        }

        # Generate username from email
        email = validated_data['email']
        username = email.split('@')[0]
        base_username = username
        num = random.randint(10, 99)
        while User.objects.filter(username=username).exists():
            username = f"{base_username}{num}"
            num = random.randint(10, 99)
        
        validated_data['username'] = username

        # Create user
        user = User.objects.create_user(**validated_data)

        # Create corresponding profile based on role
        if role == 'candidate':
            CandidateProfile.objects.create(user=user, **candidate_fields)
        elif role == 'employer':
            EmployerProfile.objects.create(user=user, **employer_fields)

        return user

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if instance.role == 'candidate':
            try:
                profile = instance.candidate_profile
                data.update({
                    'skills': profile.skills,
                    'resume': profile.resume.url if profile.resume else None,
                    'bio': profile.bio
                })
            except CandidateProfile.DoesNotExist:
                pass
        elif instance.role == 'employer':
            try:
                profile = instance.employer_profile
                data.update({
                    'company_name': profile.company_name,
                    'industry': profile.industry,
                    'logo': profile.logo.url if profile.logo else None
                })
            except EmployerProfile.DoesNotExist:
                pass
        return data

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
