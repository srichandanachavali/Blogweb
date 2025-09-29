from django.shortcuts import render, get_object_or_404
from .models import Post
from .forms import CommentForm

# The post_list view remains the same
def post_list(request):
    posts = Post.objects.all()
    return render(request, 'blog/post_list.html', {'posts': posts})

# The post_detail view is now corrected
def post_detail(request, pk): # Changed 'slug' to 'pk' here
    post = get_object_or_404(Post, pk=pk) # Changed 'slug=slug' to 'pk=pk' here
    
    # Get all active comments for this post
    comments = post.comments.filter(active=True)
    
    # Form for users to comment
    form = CommentForm()
    
    if request.method == 'POST':
        # A comment was posted
        form = CommentForm(data=request.POST)
        if form.is_valid():
            # Create Comment object but don't save to database yet
            new_comment = form.save(commit=False)
            # Assign the current post to the comment
            new_comment.post = post
            # Save the comment to the database
            new_comment.save()
            # Reset the form after a successful comment
            form = CommentForm()
    
    return render(request, 
                  'blog/post_detail.html', 
                  {'post': post,
                   'comments': comments,
                   'form': form})