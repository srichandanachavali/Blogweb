from django.urls import path

from . import views

urlpatterns = [
    path('', views.post_list, name='post_list'),
    path('post/new/', views.create_post, name='post_create'),
    path('post/<int:pk>/', views.post_detail, name='post_detail'),
    
    path('post/<int:pk>/like/', views.toggle_like, name='post_toggle_like'),
    path('post/<int:pk>/save/', views.toggle_save, name='post_toggle_save'),
    path('post/<int:pk>/comment/', views.add_comment, name='post_add_comment'),
    path('theme/', views.set_theme, name='set_theme'),
    path('register/', views.register, name='register'),
]