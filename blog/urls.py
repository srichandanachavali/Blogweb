# blog/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('', views.post_list, name='post_list'),
    path('tag/<slug:tag_slug>/', views.post_list, name='post_list_by_tag'),
    path('post/new/', views.post_create, name='post_create'), # Ensure this line exists
    path('post/<int:pk>/', views.post_detail, name='post_detail'),
    path('author/<str:username>/', views.user_post_list, name='user_posts'),
    path('like/', views.like_post, name='like_post'),
]