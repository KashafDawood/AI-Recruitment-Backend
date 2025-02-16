from django.urls import path
from .views import BlogListView, BlogDetailView, CreateBlogView

urlpatterns = [
    path("", BlogListView.as_view(), name="blog-list"),
    path("publish/", CreateBlogView.as_view(), name="blog-create"),
    path("<slug:slug>", BlogDetailView.as_view(), name="blog-detail"),
]
