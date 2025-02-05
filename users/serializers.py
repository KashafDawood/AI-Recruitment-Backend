import random
from rest_framework import serializers
from .models import User

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
