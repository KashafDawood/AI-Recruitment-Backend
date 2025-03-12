from rest_framework import serializers
from django.utils.text import slugify
from .models import Blog

class BlogCreateSerializer(serializers.ModelSerializer):
    thumbnail = serializers.ImageField(required=False, allow_null=True)  # Update this line

    class Meta:
        model = Blog
        fields = [
            "id",
            "title",
            "content",
            "keywords",
            "thumbnail",
            "created_at",
            "updated_at",
            "status",
            "slug",
            "category",
        ]
        read_only_fields = ["id", "created_at", "updated_at", "slug"]

    def create(self, validated_data):
        # Generate slug from title
        title = validated_data["title"]
        slug = slugify(title)

        # Ensure unique slug
        if Blog.objects.filter(slug=slug).exists():
            count = 1
            while Blog.objects.filter(slug=f"{slug}-{count}").exists():
                count += 1
            slug = f"{slug}-{count}"

        # Create blog with generated slug and current user as employer
        blog = Blog.objects.create(
            **validated_data, slug=slug, employer=self.context["request"].user
        )
        return blog

class BlogSerializer(serializers.ModelSerializer):
    title = serializers.CharField(required=False)
    content = serializers.CharField(required=False)
    keywords = serializers.CharField(required=False)
    status = serializers.CharField(required=False)
    category = serializers.CharField(required=False)
    thumbnail = serializers.ImageField(required=False, allow_null=True)  # Update this line

    class Meta:
        model = Blog
        fields = [
            "id",
            "title",
            "content",
            "keywords",
            "thumbnail",
            "status",
            "slug",
            "category",
        ]
        read_only_fields = ["id", "created_at", "updated_at", "slug", "employer"]

    def update(self, instance, validated_data):
        # Update slug if title is changed
        if "title" in validated_data:
            title = validated_data["title"]
            slug = slugify(title)
            if Blog.objects.filter(slug=slug).exists():
                count = 1
                while Blog.objects.filter(slug=f"{slug}-{count}").exists():
                    count += 1
                slug = f"{slug}-{count}"
            instance.slug = slug

        return super().update(instance, validated_data)
