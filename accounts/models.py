from django.conf import settings
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
# Make sure User is imported, or use settings.AUTH_USER_MODEL
from django.contrib.auth.models import User 

class Profile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='profile',
    )
    image = models.ImageField(default='default.jpg', upload_to='profile_pics')
    
    # --- THIS IS THE NEW FIELD ---
    # This will store all the User accounts that are "following" this profile.
    followers = models.ManyToManyField(
        settings.AUTH_USER_MODEL, 
        related_name='following', 
        blank=True
    )
    # ---------------------------

    def __str__(self) -> str:
        return f'{self.user.username} Profile'

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def ensure_user_profile(sender, instance, created, **kwargs):
    """Create a profile for every user and backfill missing ones."""
    Profile.objects.get_or_create(user=instance)