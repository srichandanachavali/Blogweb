from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    # Add this line to include all of Django's auth views
    # (login, logout, password reset, etc.)
    path('accounts/', include('django.contrib.auth.urls')), 
    
    # Your blog urls
    path('', include('blog.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)