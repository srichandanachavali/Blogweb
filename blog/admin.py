from django.contrib import admin
from .models import Post, Comment, Story  # <-- 1. ADDED 'Story' HERE

# --- This is your existing Post admin (no changes) ---
@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'publish', 'created']
    list_filter = ['author', 'publish', 'created']
    search_fields = ['title', 'body']
    date_hierarchy = 'publish'

# --- This is your existing Comment admin (no changes) ---
@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'post', 'created', 'active']
    list_filter = ['active', 'created']
    search_fields = ['name', 'email', 'body']
    raw_id_fields = ['post']

# --- 2. ADDED THIS NEW BLOCK FOR STORIES ---
@admin.register(Story)
class StoryAdmin(admin.ModelAdmin):
    list_display = ('author', 'created_at', 'expires_at')
    list_filter = ('author', 'created_at', 'expires_at')