# blog/forms.py

from django import forms
from .models import Post, Comment

# Form for creating/updating blog posts
class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'body', 'image', 'video', 'tags'] # Ensure video and tags are in models.py

# Form for adding comments
class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['name', 'email', 'body']