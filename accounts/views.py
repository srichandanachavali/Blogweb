from django.contrib import messages
from django.contrib.auth import logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.shortcuts import redirect, render, get_object_or_404
from django.contrib.auth.models import User
from django.http import HttpResponse

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

        elif 'change_password' in request.POST:
            u_form = UserUpdateForm(instance=request.user)
            profile_form = ProfileUpdateForm(instance=profile)
            p_form = PasswordChangeForm(request.user, request.POST)
            if p_form.is_valid():
                user = p_form.save()
                update_session_auth_hash(request, user)
                messages.success(request, 'Password changed successfully.')
                return redirect('settings')
            messages.error(request, 'Please fix the password fields below.')

    else:
        u_form = UserUpdateForm(instance=request.user)
        profile_form = ProfileUpdateForm(instance=profile)
        p_form = PasswordChangeForm(request.user)

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
    messages.info(request, "You have successfully logged out.")
    return redirect('post_list')


# --- THIS IS THE NEW, COMPLETE FUNCTION ---

def public_profile_view(request, username):
    # 1. Get the user object for the profile being viewed
    profile_user = get_object_or_404(User, username=username)
    profile, _ = Profile.objects.get_or_create(user=profile_user)
    
    # 2. Get their posts
    posts = Post.objects.filter(author=profile_user).order_by('-publish')
    
    # 3. Handle Subscribe/Unsubscribe logic (if a form was submitted)
    if request.method == 'POST':
        if not request.user.is_authenticated:
            # Send unauthenticated users to the login page
            return redirect(f"{reverse('login')}?next={request.path}")
            
        action = request.POST.get('action')
        if action == 'subscribe':
            profile.followers.add(request.user)
        elif action == 'unsubscribe':
            profile.followers.remove(request.user)
        
        # Redirect back to the same page to avoid re-posting
        return redirect('public_profile', username=username)

    # 4. Prepare context data for the template
    is_self = (request.user == profile_user)
    is_following = False
    if request.user.is_authenticated:
        # Check if the *logged-in user* is in the *profile's* follower list
        is_following = profile.followers.filter(id=request.user.id).exists()

    posts_count = posts.count()
    followers_count = profile.followers.count()
    
    # This counts how many *other* people the 'profile_user' is following.
    # This assumes your 'Profile' model has a 'followers' ManyToManyField.
    # This query finds all profiles that the 'profile_user' is a follower *of*.
    following_count = Profile.objects.filter(followers=profile_user).count()

    context = {
        'profile_user': profile_user,  # The user whose profile is being viewed
        'profile': profile,
        'posts': posts,
        'is_self': is_self,
        'is_following': is_following,
        'posts_count': posts_count,
        'followers_count': followers_count,
        'following_count': following_count,
    }
    context.update(_theme_context(request))
    
    # 5. Render the template you provided
    # (Make sure you saved your template as 'public_profile.html'
    # in 'accounts/templates/accounts/')
    return render(request, 'accounts/public_profile.html', context)