# accounts/views.py

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash, logout
# Import forms from accounts.forms now
from .forms import UserUpdateForm, ProfileUpdateForm
# Import models needed for profile_view
from blog.models import Post, Comment
from django.contrib.auth.models import User # Keep this import

@login_required
def settings_view(request):
    # Ensure profile exists, create if not (handles older users)
    profile, created = Profile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = PasswordChangeForm(request.user, request.POST)
        profile_form = ProfileUpdateForm(request.POST, request.FILES, instance=profile) # Use the profile instance

        if 'update_profile' in request.POST:
            if u_form.is_valid() and profile_form.is_valid():
                u_form.save()
                profile_form.save()
                messages.success(request, 'Your profile has been updated!')
                return redirect('settings')
            # Add error handling if forms are invalid (optional but good practice)
            # else:
            #     messages.error(request, 'Please correct the errors below.')

        elif 'change_password' in request.POST:
            if p_form.is_valid():
                user = p_form.save()
                update_session_auth_hash(request, user)
                messages.success(request, 'Your password was successfully updated!')
                return redirect('settings')
            else:
                messages.error(request, 'Please correct the password errors below.')
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = PasswordChangeForm(request.user)
        profile_form = ProfileUpdateForm(instance=profile) # Use the profile instance

    context = {
        'u_form': u_form,
        'p_form': p_form,
        'profile_form': profile_form
    }
    return render(request, 'accounts/settings.html', context)

@login_required
def profile_view(request):
    my_posts = Post.objects.filter(author=request.user).order_by('-publish')
    liked_posts = Post.objects.filter(likes=request.user)
    # Assuming comments store email, might need adjustment if linking directly to user
    user_comments = Comment.objects.filter(email=request.user.email).order_by('-created')

    context = {
        'my_posts': my_posts,
        'liked_posts': liked_posts,
        'user_comments': user_comments,
    }
    return render(request, 'accounts/profile.html', context)


def logout_view(request):
    logout(request)
    messages.info(request, "You have successfully logged out.")
    return redirect('post_list')