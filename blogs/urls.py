from django.urls import path
from .views import (
    BlogListView,
    BlogDetailView,
    CreateBlogView,
    LatestBlogsView,
    EmployerBlogListView,
)

urlpatterns = [
    path("", BlogListView.as_view(), name="blog-list"),
    path("publish/", CreateBlogView.as_view(), name="blog-create"),
    path("my-blogs/", EmployerBlogListView.as_view(), name="employer-blog-list"),
    path("<slug:slug>/", BlogDetailView.as_view(), name="blog-detail"),
    path("latest/", LatestBlogsView.as_view(), name="latest-blogs"),
]
