import dotenv
dotenv.load_dotenv()


import os

from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'blog_project.settings')

application = get_asgi_application()
