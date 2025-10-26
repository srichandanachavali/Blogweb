# accounts/urls.py
from django.urls import path
from . import views
from django.contrib.auth import views as auth_views # Import Django's built-in auth views

urlpatterns = [
    path('settings/', views.settings_view, name='settings'),
    path('profile/', views.profile_view, name='profile'),
    
    # Add Login and Logout URLs here
    path('login/', auth_views.LoginView.as_view(template_name='blog/login.html'), name='login'),
    path('logout/', views.logout_view, name='logout'), # Use our custom logout view
]