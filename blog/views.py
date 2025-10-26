from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.contrib.auth.models import User
from taggit.models import Tag

# Import ALL necessary forms and models
from .models import Post, Comment
from .forms import PostForm, CommentForm
from accounts.forms import UserUpdateForm # Correctly import from accounts

# --- ADD THIS VIEW FUNCTION BACK ---
@login_required
def post_create(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            form.save_m2m() # Important for saving tags
            return redirect('post_detail', pk=post.pk) # Redirect to the new post's detail page
    else:
        form = PostForm()
    return render(request, 'blog/post_form.html', {'form': form})

# --- The rest of your views ---
def post_list(request, tag_slug=None):
    object_list = Post.objects.all()
    tag = None
    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        object_list = object_list.filter(tags__in=[tag])
    query = request.GET.get('q')
    if query:
        object_list = object_list.filter(Q(title__icontains=query) | Q(body__icontains=query)).distinct()
    paginator = Paginator(object_list, 5)
    page_number = request.GET.get('page')
    posts = paginator.get_page(page_number)
    context = {'posts': posts, 'tag': tag}
    if request.user.is_authenticated:
        my_posts = Post.objects.filter(author=request.user).order_by('-publish')
        liked_posts = Post.objects.filter(likes=request.user)
        user_comments = Comment.objects.filter(email=request.user.email).order_by('-created')
        context['my_posts'] = my_posts
        context['liked_posts'] = liked_posts
        context['user_comments'] = user_comments
    return render(request, 'blog/post_list.html', context)

def post_detail(request, pk):
    post = get_object_or_404(Post, pk=pk)
    comments = post.comments.filter(active=True)
    if request.method == 'POST':
        comment_form = CommentForm(data=request.POST)
        if comment_form.is_valid():
            new_comment = comment_form.save(commit=False)
            new_comment.post = post
            if request.user.is_authenticated: new_comment.user = request.user
            new_comment.save()
            return redirect('post_detail', pk=post.pk)
    else: comment_form = CommentForm()
    return render(request, 'blog/post_detail.html', {'post': post, 'comments': comments, 'comment_form': comment_form})

def user_post_list(request, username):
    user = get_object_or_404(User, username=username)
    object_list = Post.objects.filter(author=user).order_by('-publish')
    paginator = Paginator(object_list, 5)
    page_number = request.GET.get('page')
    posts = paginator.get_page(page_number)
    return render(request, 'blog/user_posts.html', {'posts': posts, 'viewed_user': user})

@login_required
def like_post(request):
    post_id = request.POST.get('post_id')
    post = get_object_or_404(Post, id=post_id)
    if post.likes.filter(id=request.user.id).exists(): post.likes.remove(request.user)
    else: post.likes.add(request.user)
    return redirect('post_detail', pk=post.pk)