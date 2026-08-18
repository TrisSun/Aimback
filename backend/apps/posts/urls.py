from django.urls import path

from . import views

app_name = "posts"

urlpatterns = [
    path("posts", views.PostListCreateView.as_view(), name="post-list"),
    path("posts/<int:pk>", views.PostDetailView.as_view(), name="post-detail"),
    path("posts/<int:pk>/publish", views.PostPublishView.as_view(), name="post-publish"),
    path("posts/<int:pk>/close", views.PostCloseView.as_view(), name="post-close"),
]
