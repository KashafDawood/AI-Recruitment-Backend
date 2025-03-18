from django.shortcuts import render
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from core.permissions import IsEmployerAndOwner, IsEmployer
from .models import Blog
from .serializers import BlogSerializer, BlogCreateSerializer, BlogSerializer
from core.pagination import CustomLimitOffsetPagination 


class BlogListView(generics.ListAPIView):
    serializer_class = BlogSerializer
    queryset = Blog.objects.filter(status="published").order_by("-created_at")
    pagination_class = CustomLimitOffsetPagination

class CreateBlogView(generics.CreateAPIView):
    queryset = Blog.objects.all()
    serializer_class = BlogCreateSerializer
    permission_classes = [IsEmployer]

class BlogDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Blog.objects.all()
    serializer_class = BlogSerializer
    lookup_field = "slug"

    def get_permissions(self):
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            self.permission_classes = [IsAuthenticated, IsEmployer]
        return super().get_permissions()

class LatestBlogsView(generics.ListAPIView):
    serializer_class = BlogSerializer

    def get_queryset(self):
        return Blog.objects.filter(status="published").order_by("-created_at")[:3]



