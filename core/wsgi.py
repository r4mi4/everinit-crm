import os
from django.core.wsgi import get_wsgi_application
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()

# Set the default settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings.base')

# Create a WSGI application object
application = get_wsgi_application()
