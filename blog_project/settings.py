from pathlib import Path
import os  # <-- ADD THIS
import dj_database_url  # <-- ADD THIS

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# --- 1. SECRET_KEY IS NOW HIDDEN ---
# It will get the key from an environment variable.
# If it can't find it (like on your laptop), it uses a *different*, unsafe
# key just for local testing.
SECRET_KEY = os.environ.get(
    'SECRET_KEY', 
    'django-insecure-this-is-a-backup-key-for-local-dev-only'
)

# --- 2. DEBUG IS SET SMARTLY ---
# It's 'False' unless an environment variable 'DEBUG' is set to 'True'
DEBUG = os.environ.get('DEBUG', 'False') == 'True'


# --- 3. ALLOWED_HOSTS IS READY ---
# Render will give you a URL like 'my-site.onrender.com'.
# You MUST add it to this list.
ALLOWED_HOSTS = ['127.0.0.1']

# This will be your live site's URL
RENDER_EXTERNAL_HOSTNAME = os.environ.get('RENDER_EXTERNAL_HOSTNAME')
if RENDER_EXTERNAL_HOSTNAME:
    ALLOWED_HOSTS.append(RENDER_EXTERNAL_HOSTNAME)


# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'whitenoise.runserver_nostatic',  # <-- ADD THIS
    'django.contrib.staticfiles',
    'taggit',
    'blog',
    'accounts',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # <-- ADD THIS
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'blog_project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'blog_project.wsgi.application'


# --- 4. DATABASE IS NOW PRODUCTION-READY ---
# This will use your local db.sqlite3 file by default.
# BUT, if it finds a 'DATABASE_URL' variable (which Render will provide),
# it will automatically connect to your new PostgreSQL database.
DATABASES = {
    'default': dj_database_url.config(
        default=f'sqlite:///{BASE_DIR / "db.sqlite3"}',
        conn_max_age=600
    )
}


# Password validation
AUTH_PASSWORD_VALIDATORS = [
    # ... (your validators are fine) ...
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# --- 5. STATIC & MEDIA FILES ARE READY ---
STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']
# This tells Whitenoise to be smart about caching files
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'
# WARNING: Media files will NOT work on Render yet.
# That's a separate fix using a service like Cloudinary or S3.

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
LOGIN_REDIRECT_URL = 'post_list'
LOGOUT_REDIRECT_URL = 'post_list'
LOGIN_URL = 'login'

TAGGIT_CASE_INSENSITIVE = True