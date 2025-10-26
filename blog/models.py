# blog/models.py

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from taggit.managers import TaggableManager # <-- Import this

# This Profile model should be in accounts/models.py, but ensure it's defined somewhere.
# If it's already in accounts/models.py, you can remove it from here.
# from accounts.models import Profile 

class Post(models.Model):
    title = models.CharField(max_length=250)
    body = models.TextField()
    publish = models.DateTimeField(default=timezone.now)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='blog_posts_author')
    image = models.ImageField(upload_to='posts/', blank=True, null=True)
    video = models.FileField(upload_to='posts/videos/', blank=True, null=True) # <-- ADD THIS FIELD
    likes = models.ManyToManyField(User, related_name='blog_posts_likes', blank=True)
    tags = TaggableManager() # <-- AND ADD THIS FIELD

    class Meta:
        ordering = ['-publish']

    def __str__(self):
        return self.title

    def total_likes(self):
        return self.likes.count()

class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    name = models.CharField(max_length=80)
    email = models.EmailField()
    body = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    active = models.BooleanField(default=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)

    class Meta:
        ordering = ['created']

    def __str__(self):
        return f'Comment by {self.name} on {self.post}'