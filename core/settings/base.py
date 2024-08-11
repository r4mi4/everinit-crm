"""
Base settings for the Django project.

This file contains settings that are common across all environments (development, staging, production).
"""

import os
from pathlib import Path
from dotenv import load_dotenv
from core.utils.env_variable import get_env_variable

# Base directory of the project
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Load environment variables from a .env file if it exists
env_path = BASE_DIR / '.env'
load_dotenv(dotenv_path=env_path)

# Secret key for Django security. Should be kept secret in production.
SECRET_KEY = get_env_variable("SECRET_KEY", required=True)

# Debug mode flag. Should be False in production.
DEBUG = get_env_variable("DEBUG", "False") == "True"

# Allowed hosts for the application
ALLOWED_HOSTS = get_env_variable("ALLOWED_HOSTS", "").split(",")

# Installed apps include Django's default apps and custom apps


INTERNAL_APPS = [
    'apps.accounts.apps.AccountsConfig',
]
INSTALLED_APPS = [
                     'django.contrib.admin',
                     'django.contrib.auth',
                     'django.contrib.contenttypes',
                     'django.contrib.sessions',
                     'django.contrib.messages',
                     'django.contrib.staticfiles',
                 ] + INTERNAL_APPS

AUTH_USER_MODEL = 'accounts.CustomUser'

# Middleware configuration
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',  # Language Management Middleware
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# Database configuration. Default to SQLite for development.
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
# Templates configuration
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
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

# URL configuration
ROOT_URLCONF = 'core.urls'  # Make sure this matches your actual project structure

# WSGI application path
WSGI_APPLICATION = 'core.wsgi.application'  # Ensure this path is correct for your project

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]
# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Media files (Uploaded files)
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Internationalization settings
LANGUAGE_CODE = 'fa-ir'
TIME_ZONE = 'Asia/Tehran'

USE_I18N = True
USE_L10N = True
USE_TZ = True

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Load environment-specific settings
if DEBUG:
    try:
        from .local import *  # Load local development settings
    except ImportError:
        pass
else:
    try:
        from .production import *  # Load production settings
    except ImportError:
        pass

# Directory where the applications are located
APPS_DIR = os.path.join(BASE_DIR, 'apps')

APPS_TRANSLATION_NAME = 'locale'

# Filter to include only directories that contain 'apps.py', indicating a Django app
APPS = [
    name for name in os.listdir(APPS_DIR)
    if os.path.isdir(os.path.join(APPS_DIR, name)) and  # Ensure it's a directory
       os.path.exists(os.path.join(APPS_DIR, name, 'apps.py'))  # Check if 'apps.py' exists
]
# Dynamically generate LOCALE_PATHS
LOCALE_PATHS = []
for app_name in APPS:
    locale_path = os.path.join(APPS_DIR, app_name, 'locale')

    # Create the 'locale' directory if it doesn't exist
    if not os.path.isdir(locale_path):
        os.makedirs(locale_path)

        # Add to LOCALE_PATHS only if 'locale' directory exists or was successfully created
    LOCALE_PATHS.append(locale_path)
