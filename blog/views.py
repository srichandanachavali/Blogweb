from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_POST
from django.db.models import Prefetch

from .forms import CommentForm, PostForm
from .models import Comment, Post


def _theme_context(request: HttpRequest) -> dict:
    return {
        "active_theme": request.session.get("theme", "light"),
        "accent_color": request.session.get("accent_color", "#ff4f70"),
        "user_profile": getattr(request.user, "profile", None) if request.user.is_authenticated else None,
    }


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

    context = {
        "posts": posts,
        "comment_form": CommentForm(),
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
    from django.contrib.auth.forms import UserCreationForm

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
