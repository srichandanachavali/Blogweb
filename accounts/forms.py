
from django import forms
from django.contrib.auth.models import User
from .models import Profile # Import Profile from accounts models

# Form for updating user's username and email (used in settings)
class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'email']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})

# Form for updating user's profile picture (used in settings)
class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
    
        fields = ['image']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['image'].widget.attrs.update({'class': 'form-control'})