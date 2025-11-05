from django.contrib import messages
from django.db.models import Prefetch
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy  # <-- IMPORT REVERSE_LAZY
from django.views.decorators.http import require_POST
from .forms import CommentForm, PostForm, StoryForm
from .models import Comment, Post, Story
from django.utils import timezone
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
# --- IMPORTS FOR UPDATE/DELETE ---
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import UpdateView, DeleteView


User = get_user_model()

def _theme_context(request: HttpRequest) -> dict:
    return {
        "active_theme": request.session.get("theme", "light"),
        "accent_color": request.session.get("accent_color", "#ff4f70"),
        "user_profile": getattr(request.user, "profile", None) if request.user.is_authenticated else None,
    }

# --- THIS FUNCTION IS UPDATED ---
def post_list(request: HttpRequest) -> HttpResponse:
    posts = list(
        Post.objects.select_related("author", "author__profile")
        .prefetch_related(
            "likes",
            "saved_by",
            "tags",
            Prefetch("comments", queryset=Comment.objects.filter(active=True).select_related("user")),
        )
    )
    for post in posts:
        post.user_liked = post.is_liked_by(request.user)
        post.user_saved = post.is_saved_by(request.user)
        
    # --- UPDATED STORY LOGIC ---
    final_stories = [] # Start with an empty list
    
    if request.user.is_authenticated:
        # 1. Get the Profiles of users the current user is following.
        #    (Assumes related_name='following' on your Profile's followers field)
        try:
            my_followed_profiles = request.user.following.all()
            
            # 2. Get the user IDs from those profiles
            followed_user_ids = my_followed_profiles.values_list('user__id', flat=True)

            # 3. Get active stories *only* from those users
            active_stories = Story.objects.filter(
                expires_at__gt=timezone.now(),
                author__id__in=followed_user_ids
            ).select_related('author', 'author__profile')
            
            # 4. Get just the latest story for each user
            stories_by_user = {}
            for story in active_stories:
                if story.author.id not in stories_by_user:
                    stories_by_user[story.author.id] = story
            final_stories = list(stories_by_user.values())
        except AttributeError:
            # Fails gracefully if the 'following' relationship isn't set up
            # (e.g., accounts/models.py Profile model is wrong)
            final_stories = [] 
    # --- END UPDATED LOGIC ---

    context = {
        "posts": posts,
        "comment_form": CommentForm(),
        "stories": final_stories,  # This is now the *filtered* list
    }
    context.update(_theme_context(request))
    return render(request, "blog/post_list.html", context)


def post_detail(request: HttpRequest, pk: int) -> HttpResponse:
    post = get_object_or_404(
        Post.objects.select_related("author", "author__profile").prefetch_related("tags"),
        pk=pk,
    )
    comments = post.comments.filter(active=True).select_related("user")
    post.user_liked = post.is_liked_by(request.user)
    post.user_saved = post.is_saved_by(request.user)

    context = {
        "post": post,
        "comments": comments,
        "comment_form": CommentForm(),
    }
    context.update(_theme_context(request))
    return render(request, "blog/post_detail.html", context)


@login_required
def create_post(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            form.save_m2m()
            messages.success(request, "Your post is live!")
            return redirect("post_detail", pk=post.pk)
    else:
        form = PostForm()

    context = {"form": form}
    context.update(_theme_context(request))
    return render(request, "blog/post_form.html", context)

@login_required
def create_story(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        form = StoryForm(request.POST, request.FILES)
        if form.is_valid():
            story = form.save(commit=False)
            story.author = request.user
            story.save()
            messages.success(request, "Your story is live for 24 hours!")
            return redirect("post_list") # Go back home
    else:
        form = StoryForm()

    context = {"form": form}
    context.update(_theme_context(request))
    return render(request, "blog/story_form.html", context)

def story_view(request: HttpRequest, username: str) -> HttpResponse:
    story_user = get_object_or_404(User, username=username)
    
    active_stories = Story.objects.filter(
        author=story_user,
        expires_at__gt=timezone.now()
    ).select_related('author', 'author__profile')

    if not active_stories:
        messages.info(request, f"{username} has no active stories.")
        return redirect("post_list")

    context = {
        "story_user": story_user,
        "stories": active_stories,
    }
    context.update(_theme_context(request))
    return render(request, "blog/story_detail.html", context)


@login_required
@require_POST
def toggle_like(request: HttpRequest, pk: int) -> HttpResponse:
    post = get_object_or_404(Post, pk=pk)
    if post.is_liked_by(request.user):
        post.likes.remove(request.user)
    else:
        post.likes.add(request.user)
    next_url = request.POST.get("next") or reverse("post_detail", args=[pk])
    return redirect(next_url)


@login_required
@require_POST
def toggle_save(request: HttpRequest, pk: int) -> HttpResponse:
    post = get_object_or_404(Post, pk=pk)
    if post.is_saved_by(request.user):
        post.saved_by.remove(request.user)
    else:
        post.saved_by.add(request.user)
    next_url = request.POST.get("next") or reverse("post_detail", args=[pk])
    return redirect(next_url)


@login_required
@require_POST
def add_comment(request: HttpRequest, pk: int) -> HttpResponse:
    post = get_object_or_404(Post, pk=pk)
    form = CommentForm(request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.post = post
        comment.user = request.user
        comment.name = request.user.get_full_name() or request.user.get_username()
        comment.email = request.user.email
        comment.save()
    next_url = request.POST.get("next") or reverse("post_detail", args=[pk])
    return redirect(next_url)


def register(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get("username")
            messages.success(request, f"Welcome {username}! You can now log in.")
            return redirect("login")
    else:
        form = UserCreationForm()

    context = {"form": form}
    context.update(_theme_context(request))
    return render(request, "registration/register.html", context)

@login_required
@require_POST
def set_theme(request: HttpRequest) -> HttpResponse:
    theme = request.POST.get("theme", "light")
    accent_color = request.POST.get("accent_color") or request.session.get("accent_color", "#ff4f70")

    if not isinstance(accent_color, str) or not accent_color.startswith("#"):
        accent_color = "#ff4f70"
    if len(accent_color) not in {4, 7}:
        accent_color = "#ff4f70"

    if theme not in {"light", "dark", "custom"}:
        theme = "light"

    request.session["theme"] = theme
    request.session["accent_color"] = accent_color

    messages.success(request, "Your appearance preferences have been updated.")

    next_url = request.POST.get("next") or request.META.get("HTTP_REFERER") or reverse("settings")
    return redirect(next_url)

# -----------------------------------------------
# --- ADD THESE NEW CLASSES FOR UPDATE & DELETE ---
# -----------------------------------------------

class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Post
    # These are the fields the user can edit
    fields = ['title', 'body', 'image', 'video', 'tags']
    template_name = 'blog/post_form.html' # We will create this template

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def test_func(self):
        # Get the post we're trying to update
        post = self.get_object()
        # Check if the current logged-in user is the author
        return self.request.user == post.author
    
    def get_success_url(self):
        # Redirect back to the post's detail page after updating
        return reverse_lazy('post_detail', kwargs={'pk': self.object.pk})


class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Post
    template_name = 'blog/post_confirm_delete.html' # We will create this
    
    # URL to redirect to after a successful deletion
    success_url = reverse_lazy('post_list') 

    def test_func(self):
        # Get the post we're trying to delete
        post = self.get_object()
        # Check if the current logged-in user is the author
        return self.request.user == post.author