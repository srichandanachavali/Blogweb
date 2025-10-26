from django.contrib import admin
from .models import Post, Comment


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'publish', 'created']
    list_filter = ['author', 'publish', 'created']
    search_fields = ['title', 'body']

    date_hierarchy = 'publish'


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'post', 'created', 'active']
    list_filter = ['active', 'created']
    search_fields = ['name', 'email', 'body']
    raw_id_fields = ['post']