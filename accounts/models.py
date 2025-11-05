from django.conf import settings
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from cloudinary.models import CloudinaryField  # <-- 1. IMPORT THIS

# Using settings.AUTH_USER_MODEL is good practice
User = settings.AUTH_USER_MODEL 

class Profile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='profile',
    )
    
    # --- THIS IS THE FIXED FIELD ---
    image = CloudinaryField(
        'image',
        folder='profile_pics',   # <-- 3. SET THE FOLDER
        default='v1730825368/profile_pics/default_k3mjna.jpg'  # <-- 4. USE A CLOUDINARY DEFAULT
    )
    # --- END FIXED FIELD ---
    
    # This field is correct
    followers = models.ManyToManyField(
        settings.AUTH_USER_MODEL, 
        related_name='following', 
        blank=True
    )

    def __str__(self) -> str:
        return f'{self.user.username} Profile'

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def ensure_user_profile(sender, instance, created, **kwargs):
    """Create a profile for every user and backfill missing ones."""
    Profile.objects.get_or_create(user=instance)
    