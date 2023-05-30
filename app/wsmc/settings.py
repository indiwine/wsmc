"""
Django settings for wsmc project.

Generated by 'django-admin startproject' using Django 4.1.1.

For more information on this file, see
https://docs.djangoproject.com/en/4.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.1/ref/settings/
"""
import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-rj&+$ma$$l@i#r4x1f0h&kvx2)hwc)3)&nm1yy--pq5lkha&c6'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = bool(int(os.environ.get('DEBUG', '0')))

ALLOWED_HOSTS = [
    '0.0.0.0',
    'localhost'
]

# Application definition


INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.postgres',
    'django.contrib.gis',
    'encrypted_model_fields',
    'django_celery_results',
    'social_media.apps.SocialMediaConfig',
    'telegram_connection.apps.TelegramConfig',
    'phonenumber_field',
    'import_export'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'wsmc.urls'

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
                'django.template.context_processors.media'
            ],
        },
    },
]

WSGI_APPLICATION = 'wsmc.wsgi.application'

FILE_UPLOAD_HANDLERS = ['django.core.files.uploadhandler.TemporaryFileUploadHandler']

# Database
# https://docs.djangoproject.com/en/4.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        # 'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('POSTGRES_NAME'),
        'USER': os.environ.get('POSTGRES_USER'),
        'PASSWORD': os.environ.get('POSTGRES_PASSWORD'),
        'HOST': 'postgres',
        'PORT': 5432,
    }
}

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": os.environ.get('CELERY_BROKER_URL', ''),
        "TIMEOUT": 1800,
    }
}

# Password validation
# https://docs.djangoproject.com/en/4.1/ref/settings/#auth-password-validators

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

# Internationalization
# https://docs.djangoproject.com/en/4.1/topics/i18n/

LANGUAGE_CODE = 'uk-ua'

TIME_ZONE = 'EET'

USE_I18N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.1/howto/static-files/

STATIC_URL = 'static/'

STATIC_ROOT = '/app/static'

# Default primary key field type
# https://docs.djangoproject.com/en/4.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

MEDIA_URL = 'storage/'
MEDIA_ROOT = '/app/storage'

log_level = 'DEBUG' if DEBUG else 'INFO'

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'social_media': {
            'format': '[{name}]: {message}',
            'style': '{',
        }
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'social_media'
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'WARNING',
    },
    'loggers': {
        'social_media': {
            'level': log_level,
        },
        'telegram_connection': {
            'level': 'WARNING',
        },
        'hpack': {
            'level': 'WARNING'
        },
        'seleniumwire': {
            'level': 'WARNING'
        },
        # 'django.db.backends': {
        #     'level': 'DEBUG',
        #     'handlers': ['console'],
        # }
    }
}

FIXTURE_DIRS = [
    'social_media/fixtures'
]

# Celery Configuration Options
CELERY_TIMEZONE = TIME_ZONE
CELERY_RESULT_BACKEND = 'django-db'
CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL', '')
CELERY_TASK_TRACK_STARTED = True
CELERY_RESULT_EXTENDED = True
CELERY_ALWAYS_EAGER = True
CELERY_EAGER_PROPAGATES_EXCEPTIONS = True

FIELD_ENCRYPTION_KEY = os.environ.get('FIELD_ENCRYPTION_KEY', '')

NOMINATIM_USER_AGENT = os.environ.get('NOMINATIM_USER_AGENT', 'wsmc_test_app')
NOMINATIM_DOMAIN = os.environ.get('NOMINATIM_DOMAIN', 'nominatim.openstreetmap.org')
NOMINATIM_SCHEME = os.environ.get('NOMINATIM_SCHEME', 'https')
NOMINATIM_TIMEOUT = 10

# WSMC_LOAD_AI = bool(int(os.environ.get('WSMC_LOAD_AI', '1')))
WSMC_LOAD_AI = False

WSMC_WEBDRIVER_URL = os.environ.get('WEBDRIVER_URL', '')
WSMC_SELENIUM_DRIVER = os.environ.get('SELENIUM_DRIVER', 'chrome')
WSMC_SELENIUM_SCREENSHOT_DIR = 'selenium'

# Wait timeout in seconds
WSMC_SELENIUM_WAIT_TIMEOUT = 60
WSMC_SELENIUM_SCRIPT_TIMEOUT = 60

WSMC_WEBDRIVER_LOCALE = 'ru_RU'
PG_SEARCH_LANG = 'pg_catalog.russian'

PHONENUMBER_DEFAULT_REGION = 'UA'

# TDlib config
# See https://my.telegram.org/apps
TELEGRAM_API_ID = os.environ.get('TELEGRAM_API_ID', '')
TELEGRAM_API_HASH = os.environ.get('TELEGRAM_API_HASH', '')
TELEGRAM_DATABASE_ENCRYPTION_KEY = os.environ.get('TELEGRAM_DATABASE_ENCRYPTION_KEY', 'changeme1234')

# Test setting
TEST_VK_LOGIN = os.environ.get('TEST_VK_LOGIN', '')
TEST_VK_PASSWORD = os.environ.get('TEST_VK_PASSWORD', '')
