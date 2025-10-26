from django.contrib import messages
from django.contrib.auth import logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.shortcuts import redirect, render

from blog.models import Comment, Post
from .forms import ProfileUpdateForm, UserUpdateForm
from .models import Profile


def _theme_context(request):
    return {
        'active_theme': request.session.get('theme', 'light'),
        'accent_color': request.session.get('accent_color', '#ff4f70'),
        'user_profile': getattr(request.user, 'profile', None) if request.user.is_authenticated else None,
    }


@login_required
def settings_view(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
       
        if 'update_profile' in request.POST:
            u_form = UserUpdateForm(request.POST, instance=request.user)
            profile_form = ProfileUpdateForm(request.POST, request.FILES, instance=profile)
            p_form = PasswordChangeForm(request.user)
            if u_form.is_valid() and profile_form.is_valid():
                u_form.save()
                profile_form.save()
               
                messages.success(request, 'Profile updated successfully.')
                return redirect('settings')
           
            messages.error(request, 'Please fix the highlighted profile fields.')
        elif 'change_password' in request.POST:
            u_form = UserUpdateForm(instance=request.user)
            profile_form = ProfileUpdateForm(instance=profile)
            p_form = PasswordChangeForm(request.user, request.POST)
            if p_form.is_valid():
                user = p_form.save()
                update_session_auth_hash(request, user)
                
                messages.success(request, 'Password changed successfully.')
                return redirect('settings')
            else:
              messages.error(request, 'Please fix the password fields below.')
        else:
            u_form = UserUpdateForm(instance=request.user)
            profile_form = ProfileUpdateForm(instance=profile)
            p_form = PasswordChangeForm(request.user)
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = PasswordChangeForm(request.user)
        profile_form = ProfileUpdateForm(instance=profile)

    context = {
        'u_form': u_form,
        'p_form': p_form,
        'profile_form': profile_form,
    }
    context.update(_theme_context(request))
    return render(request, 'accounts/settings.html', context)


@login_required
def profile_view(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)
    my_posts = (
        Post.objects.filter(author=request.user)
        .select_related('author', 'author__profile')
        .prefetch_related('likes', 'saved_by')
        .order_by('-publish')
    )
    liked_posts = request.user.liked_posts.select_related('author', 'author__profile').order_by('-publish')
    saved_posts = request.user.bookmarked_posts.select_related('author', 'author__profile').order_by('-publish')
    user_comments = Comment.objects.filter(user=request.user).select_related('post').order_by('-created')

    context = {
        'profile': profile,
        'my_posts': my_posts,
        'liked_posts': liked_posts,
        'saved_posts': saved_posts,
        'user_comments': user_comments,
    }
    context.update(_theme_context(request))
    return render(request, 'accounts/profile.html', context)


def logout_view(request):
    logout(request)
   
    messages.info(request, 'You have successfully logged out.')
    return redirect('post_list')