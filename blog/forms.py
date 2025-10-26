from django import forms
from .models import Comment

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        # The form will now only show the 'body' field to the user
        fields = ['body']