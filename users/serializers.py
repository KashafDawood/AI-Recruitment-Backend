from django.contrib.auth.hashers import make_password
from rest_framework import serializers
from .models import Users

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = Users
        fields = ['name', 'email', 'password', 'photo', 'role']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = Users(
            name = validated_data['name'],
            email = validated_data['email'],
            role = validated_data.get('role')
        )
        user.password = make_password(validated_data['password'])
        user.save()
        return user