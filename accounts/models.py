# accounts/models.py

from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image = models.ImageField(default='default.jpg', upload_to='profile_pics')

    def __str__(self):
        return f'{self.user.username} Profile'

# Signals to auto-create/update Profile when User is created/updated
@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_profile(sender, instance, **kwargs):
    # Check if the profile exists before trying to save it
    # This handles cases where the user might exist without a profile initially
    if hasattr(instance, 'profile'):
        instance.profile.save()
    else:
        # If profile doesn't exist (e.g., for users created before this signal), create it now.
        Profile.objects.create(user=instance)