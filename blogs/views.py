from django.shortcuts import render
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from core.permissions import IsEmployerAndOwner, IsEmployer
from .models import Blog
from .serializers import BlogSerializer, BlogCreateSerializer
from core.pagination import CustomPageNumberPagination


class BlogListView(generics.ListAPIView):
    """View to list all published blogs"""

    serializer_class = BlogSerializer
    queryset = Blog.objects.filter(status="published").order_by("-created_at")
    pagination_class = CustomPageNumberPagination


class EmployerBlogListView(generics.ListAPIView):
    """View to list all blogs belonging to the current employer"""

    serializer_class = BlogSerializer
    permission_classes = [IsAuthenticated, IsEmployer]
    pagination_class = CustomPageNumberPagination

    def get_queryset(self):
        status_filter = self.request.query_params.get("status", None)
        queryset = Blog.objects.filter(employer=self.request.user).order_by(
            "-created_at"
        )
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        return queryset


class CreateBlogView(generics.CreateAPIView):
    """View to create a new blog post"""

    queryset = Blog.objects.all()
    serializer_class = BlogCreateSerializer
    permission_classes = [IsAuthenticated, IsEmployer]


class BlogDetailView(generics.RetrieveUpdateDestroyAPIView):
    """View to retrieve, update or delete a blog post"""

    queryset = Blog.objects.all()
    serializer_class = BlogSerializer
    lookup_field = "slug"

    def get_permissions(self):
        if self.request.method in ["PUT", "PATCH", "DELETE"]:
            self.permission_classes = [IsAuthenticated, IsEmployerAndOwner]
        return super().get_permissions()

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)


class LatestBlogsView(generics.ListAPIView):
    """View to list the latest 3 published blog posts"""

    serializer_class = BlogSerializer

    def get_queryset(self):
        return Blog.objects.filter(status="published").order_by("-created_at")[:3]
