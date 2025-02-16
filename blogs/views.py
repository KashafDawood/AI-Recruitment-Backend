from django.shortcuts import render
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from core.permissions import IsEmployerAndOwner, IsEmployer
from .models import Blog
from .serializers import BlogSerializer, BlogCreateSerializer, BlogSerializer


class BlogListView(generics.ListAPIView):
    serializer_class = BlogSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Blog.objects.filter(status="published").order_by("-created_at")


class CreateBlogView(generics.CreateAPIView):
    queryset = Blog.objects.all()
    serializer_class = BlogCreateSerializer
    permission_classes = [IsEmployer]


class BlogDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Blog.objects.all()
    serializer_class = BlogSerializer
    permission_classes = [IsEmployerAndOwner]
    lookup_field = "slug"
