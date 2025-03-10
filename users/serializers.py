from rest_framework import serializers
from .models import User
from .models import CandidateProfile, EmployerProfile
from django.contrib.auth import authenticate
from ai.bio_filter import filter_bio


class SignupSerializer(serializers.ModelSerializer):
    # Fields for basic user registration
    id = serializers.IntegerField(read_only=True)
    username = serializers.CharField(read_only=True)
    role = serializers.ChoiceField(
        choices=User.ROLE_CHOICES, required=True, allow_null=False
    )
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ["id", "name", "username", "email", "password", "role"]

    def create(self, validated_data):
        # Extract password and create user
        password = validated_data.pop("password")

        # Generate a unique username using email
        email = validated_data.get("email")
        username_base = email.split("@")[0]
        username = username_base
        counter = 1
        while User.objects.filter(username=username).exists():
            username = f"{username_base}{counter}"
            counter += 1
        validated_data["username"] = username

        user = User.objects.create(**validated_data)
        user.set_password(password)
        user.save()

        # Create corresponding profile based on role
        if user.role == "candidate":
            CandidateProfile.objects.create(user=user)
        elif user.role == "employer":
            EmployerProfile.objects.create(user=user)

        return user


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

        return {"user": user}


class CandidateSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    username = serializers.ReadOnlyField(source="user.username")
    email = serializers.ReadOnlyField(source="user.email")
    name = serializers.CharField(source="user.name", required=False)
    photo = serializers.ImageField(source="user.photo", required=False)
    phone = serializers.CharField(source="user.phone", required=False, allow_blank=True)
    website = serializers.URLField(
        source="user.website", required=False, allow_blank=True
    )
    socials = serializers.JSONField(
        source="user.socials", required=False, allow_null=True
    )
    address = serializers.CharField(
        source="user.address", required=False, allow_blank=True
    )
    resumes = serializers.JSONField(required=False)  # Add resumes field
    certifications = serializers.JSONField(
        read_only=True, source="user.certifications", required=False
    )
    education = serializers.JSONField(
        read_only=True, source="user.education", required=False
    )
    experience = serializers.IntegerField(required=False)  # Changed to IntegerField
    interests = serializers.CharField(
        required=False, allow_blank=True
    )  # Changed to CharField

    class Meta:
        model = CandidateProfile
        fields = [
            "id",
            "username",
            "name",
            "email",
            "photo",
            "phone",
            "website",
            "socials",
            "address",
            "skills",
            "bio",
            "resumes",  # Add resumes field
            "certifications",  # Add certifications field
            "education",  # Add education field
            "experience",
            "interests",
        ]

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["certifications"] = instance.user.certifications
        data["education"] = instance.user.education
        return data

    def update(self, instance, validated_data):
        # Retrieve nested user data
        user_data = validated_data.pop("user", {})
        if "name" in user_data:
            instance.user.name = user_data["name"]
        if "photo" in user_data:
            instance.user.photo = user_data["photo"]
        if "phone" in user_data:
            instance.user.phone = user_data["phone"]
        if "website" in user_data:
            instance.user.website = user_data["website"]
        if "socials" in user_data:
            instance.user.socials = user_data["socials"]
        if "address" in user_data:
            instance.user.address = user_data["address"]
        instance.user.certifications = user_data.get(
            "certifications", instance.user.certifications
        )
        instance.user.education = user_data.get("education", instance.user.education)
        instance.user.save()

        # Update candidate-specific fields
        instance.skills = validated_data.get("skills", instance.skills)
        instance.bio = validated_data.get("bio", instance.bio)
        instance.resumes = validated_data.get("resumes", instance.resumes)
        instance.experience = validated_data.get("experience", instance.experience)
        instance.interests = validated_data.get("interests", instance.interests)
        instance.save()
        return instance


class EmployerSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    username = serializers.ReadOnlyField(source="user.username")
    email = serializers.ReadOnlyField(source="user.email")
    name = serializers.CharField(source="user.name", required=False)
    photo = serializers.ImageField(source="user.photo", required=False)
    phone = serializers.CharField(source="user.phone", required=False, allow_blank=True)
    website = serializers.URLField(
        source="user.website", required=False, allow_blank=True
    )
    socials = serializers.JSONField(
        source="user.socials", required=False, allow_null=True
    )
    address = serializers.CharField(
        source="user.address", required=False, allow_blank=True
    )
    company_name = serializers.CharField(
        required=False
    )  # Added to allow optional update
    industry = serializers.CharField(required=False)  # Added to allow optional update

    class Meta:
        model = EmployerProfile
        fields = [
            "id",
            "username",
            "name",
            "email",
            "photo",
            "phone",
            "website",
            "socials",
            "address",
            "company_name",
            "logo",
            "industry",
        ]

    def update(self, instance, validated_data):
        # Retrieve nested user data
        user_data = validated_data.pop("user", {})
        if "name" in user_data:
            instance.user.name = user_data["name"]
        if "photo" in user_data:
            instance.user.photo = user_data["photo"]
        if "phone" in user_data:
            instance.user.phone = user_data["phone"]
        if "website" in user_data:
            instance.user.website = user_data["website"]
        if "socials" in user_data:
            instance.user.socials = user_data["socials"]
        if "address" in user_data:
            instance.user.address = user_data["address"]
        instance.user.save()

        # Update employer-specific fields
        instance.company_name = validated_data.get(
            "company_name", instance.company_name
        )
        instance.logo = validated_data.get("logo", instance.logo)
        instance.industry = validated_data.get("industry", instance.industry)
        instance.save()
        return instance


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)


class ChangeUsername(serializers.Serializer):
    username = serializers.CharField(required=True)


class VerifyEmailOTP(serializers.Serializer):
    otp = serializers.CharField(max_length=6)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "name",
            "email",
            "role",
            "photo",
            "phone",
            "website",
            "socials",
            "address",
            "certifications",
            "education",
        ]
        read_only_fields = [
            "id",
            "username",
            "email",
            "role",
            "certifications",
            "education",
        ]


class ForgetPassword(serializers.Serializer):
    email = serializers.EmailField(required=True)


class ResetPassword(serializers.Serializer):
    new_password = serializers.CharField(required=True)


class EducationSerializer(serializers.Serializer):
    degree_name = serializers.CharField(max_length=255)
    institute_name = serializers.CharField(max_length=255)
    start_date = serializers.DateField()
    end_date = serializers.DateField(required=False, allow_null=True)

    def validate(self, data):
        if data["is_studying"] and data.get("end_date"):
            raise serializers.ValidationError(
                "End date should be null if currently studying."
            )
        return data


class CertificationSerializer(serializers.Serializer):
    certification_name = serializers.CharField(max_length=255)
    source = serializers.CharField(max_length=255)
    source_url = serializers.URLField(required=False, allow_blank=True)
    date_obtained = serializers.DateField(required=False, allow_null=True)


class BioSerializer(serializers.Serializer):
    bio = serializers.CharField(required=True)
