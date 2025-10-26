from django.shortcuts import render, get_object_or_404, redirect # Add redirect
from .models import Post
from .forms import CommentForm
from django.http import JsonResponse
from django.contrib.auth.forms import UserCreationForm # Import this
from django.contrib import messages # Import this

# ... post_list and post_detail views remain the same ...

# Add this new view at the end of the file
def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}! You can now log in.')
            return redirect('login') # Redirect to the login page
    else:
        form = UserCreationForm()
    return render(request, 'registration/register.html', {'form': form})