from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from taggit.managers import TaggableManager
from cloudinary.models import CloudinaryField  # <-- Import CloudinaryField

User = get_user_model()


# -----------------------------
#  POST MODEL
# -----------------------------
class Post(models.Model):
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='blog_posts'
    )
    title = models.CharField(max_length=250)
    body = models.TextField()
    
    # --- UPDATED FIELDS ---
    image = CloudinaryField(
        'image',
        folder='posts/images',  # <-- Tells Cloudinary to use this folder
        blank=True,
        null=True
    )
    video = CloudinaryField(
        'video',
        resource_type='video',  # <-- Specify resource type for videos
        folder='posts/videos',  # <-- Tells Cloudinary to use this folder
        blank=True,
        null=True
    )
    # --- END UPDATED FIELDS ---
    
    publish = models.DateTimeField(default=timezone.now)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    # User Interactions
    likes = models.ManyToManyField(User, related_name='liked_posts', blank=True)
    saved_by = models.ManyToManyField(User, related_name='saved_posts', blank=True)

    # Tags
    tags = TaggableManager(blank=True)

    class Meta:
        ordering = ['-publish']

    def __str__(self):
        return self.title

    # --- Interaction Helpers ---
    def total_likes(self):
        return self.likes.count()

    def total_saves(self):
        return self.saved_by.count()

    def is_liked_by(self, user):
        return user.is_authenticated and self.likes.filter(id=user.id).exists()

    def is_saved_by(self, user):
        return user.is_authenticated and self.saved_by.filter(id=user.id).exists()

    # --- Profile Helper ---
    @property
    def author_profile(self):
        return getattr(self.author, 'profile', None)


# -----------------------------
#  COMMENT MODEL
# -----------------------------
class Comment(models.Model):
    post = models.ForeignKey(
        Post, on_delete=models.CASCADE, related_name='comments'
    )
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, null=True, blank=True, related_name='comments'
    )
    name = models.CharField(max_length=80, blank=True)
    email = models.EmailField(blank=True)
    body = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    active = models.BooleanField(default=True)

    class Meta:
        ordering = ['created']

    def __str__(self):
        display_name = self.name or (self.user.username if self.user else 'Anonymous')
        return f"Comment by {display_name} on {self.post.title}"


# -----------------------------
#  STORY MODEL
# -----------------------------
class Story(models.Model):
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='stories'
    )
    
    # --- UPDATED FIELD ---
    image = CloudinaryField(
        'image',
        folder='stories/images'  # <-- Tells Cloudinary to use this folder
    )
    # --- END UPDATED FIELD ---
    
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = "Stories"

    def __str__(self):
        return f"Story by {self.author.username} ({self.created_at.strftime('%Y-%m-%d %H:%M')})"

    def save(self, *args, **kwargs):
        # Automatically set expiry to 24 hours after creation
        if not self.id:
            self.expires_at = timezone.now() + timedelta(hours=24)
        super().save(*args, **kwargs)