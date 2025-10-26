# accounts/forms.py

from django import forms
from django.contrib.auth.models import User
from .models import Profile # Import Profile from accounts models

# Form for updating user's username and email (used in settings)
class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'email']

# Form for updating user's profile picture (used in settings)
class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['image']