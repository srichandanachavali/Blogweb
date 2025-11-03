from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone
from taggit.managers import TaggableManager
from datetime import timedelta  # <-- ADDED THIS IMPORT

User = get_user_model()


class Post(models.Model):
    title = models.CharField(max_length=250)
    body = models.TextField()
    publish = models.DateTimeField(default=timezone.now)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='blog_posts')
    image = models.ImageField(upload_to='posts/', blank=True, null=True)
    video = models.FileField(upload_to='posts/videos/', blank=True, null=True)
    likes = models.ManyToManyField(User, related_name='liked_posts', blank=True)
    saved_by = models.ManyToManyField(User, related_name='bookmarked_posts', blank=True)
    tags = TaggableManager(blank=True)

    class Meta:
        ordering = ['-publish']

    def __str__(self) -> str:
        return self.title

    def total_likes(self) -> int:
        return self.likes.count()

    def total_saves(self) -> int:
        return self.saved_by.count()

    def is_liked_by(self, user: User) -> bool:
        if not user or getattr(user, "is_anonymous", True):
            return False
        return self.likes.filter(pk=user.pk).exists()

    def is_saved_by(self, user: User) -> bool:
        if not user or getattr(user, "is_anonymous", True):
            return False
        return self.saved_by.filter(pk=user.pk).exists()

    @property
    def author_profile(self):
        return getattr(self.author, 'profile', None)


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    name = models.CharField(max_length=80, blank=True)
    email = models.EmailField(blank=True)
    body = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    active = models.BooleanField(default=True)
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, null=True, blank=True, related_name='comments'
    )

    class Meta:
        ordering = ['created']

    def __str__(self) -> str:
        display_name = self.name or (self.user.get_username() if self.user else 'Anonymous')
        return f'Comment by {display_name} on {self.post}'

# --- NEW STORY MODEL ---
class Story(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='stories')
    image = models.ImageField(upload_to='stories/')
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    def save(self, *args, **kwargs):
        # This is the magic: auto-set the expiry time to 24 hours
        if not self.id: # Only set on creation
            self.expires_at = timezone.now() + timedelta(hours=24)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Story by {self.author.username} at {self.created_at.strftime('%Y-%m-%d %H:%M')}"

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = "Stories" # Fixes the "Storys" typo in admin