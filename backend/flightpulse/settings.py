import os
from pathlib import Path
from datetime import timedelta
from dotenv import load_dotenv

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Load environment variables from .env file
load_dotenv(os.path.join(BASE_DIR, '.env'))

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-default-key')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv('DEBUG', 'True').lower() in ('1', 'true', 'yes')

# Comma-separated list in the env, e.g. "example.com,api.example.com" or "*"
ALLOWED_HOSTS = [h.strip() for h in os.getenv('ALLOWED_HOSTS', '*').split(',') if h.strip()]


# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Third-party apps
    'rest_framework',
    'rest_framework_simplejwt',
    'rest_framework_simplejwt.token_blacklist',
    'corsheaders',
    'django_filters',
    'django_celery_beat',
    'django_celery_results',

    # Local apps
    'users',
    'routes',
    'alerts',
    'schedular',   # Celery tasks live here (autodiscovered by Celery)
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'flightpulse.urls'

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

WSGI_APPLICATION = 'flightpulse.wsgi.application'


# Database - Points to your Docker PostgreSQL container
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DB_NAME', 'postgres'),
        'USER': os.getenv('DB_USER', 'postgres'),
        'PASSWORD': os.getenv('DB_PASSWORD', 'postgres'),
        'HOST': os.getenv('DB_HOST', '127.0.0.1'),
        'PORT': os.getenv('DB_PORT', '5433'),
    }
}

# Custom User Model
AUTH_USER_MODEL = 'users.User'

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',},
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'   # target for `collectstatic` (served by Whitenoise)
STORAGES = {
    'default': {'BACKEND': 'django.core.files.storage.FileSystemStorage'},
    'staticfiles': {'BACKEND': 'whitenoise.storage.CompressedManifestStaticFilesStorage'},
}
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# --- CUSTOM INTEGRATIONS START HERE ---

# 1. REST Framework (JWT Default)
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
}

# 2. Simple JWT (1 Hour Access / 14 Day Refresh)
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=1),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=14),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
}

# 3. CORS (Allow React Frontend)
CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",
]

# 4. Celery (Redis Broker / Postgres Results)
CELERY_BROKER_URL = os.getenv('CELERY_BROKER_URL', 'redis://127.0.0.1:6379/0')
CELERY_RESULT_BACKEND = 'django-db'
CELERY_CACHE_BACKEND = 'django-cache'

# ============================================================
# 5. External API credentials
#    All of these are read from the environment (.env). They are
#    OPTIONAL for the app to run — without them the stack boots and
#    every screen works; only live data / real delivery needs them.
#
#    >>> API KEYS REQUIRED HERE <<<  (fill these in .env)
#      EMAIL_HOST_USER / EMAIL_HOST_PASSWORD   -> SMTP credentials
#      TWILIO_ACCOUNT_SID / TWILIO_AUTH_TOKEN  -> Twilio SMS
#      TWILIO_PHONE_NUMBER                     -> Twilio sender number
#      RAPIDAPI_KEY                            -> Sky-Scrapper flight search
# ============================================================

# --- Email (SMTP) ---
# If no SMTP host is configured, fall back to the console backend so deal
# emails are printed to the worker logs instead of failing — lets the full
# pipeline work end-to-end without credentials during development.
EMAIL_HOST = os.getenv('EMAIL_HOST')
if EMAIL_HOST:
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
else:
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
EMAIL_PORT = int(os.getenv('EMAIL_PORT', 587))
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')          # API KEY: SMTP username
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')  # API KEY: SMTP password / app password
DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL', 'FlightPulse <no-reply@flightpulse.local>')

# --- Twilio (SMS) ---
TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')    # API KEY: Twilio Account SID
TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')      # API KEY: Twilio Auth Token
TWILIO_PHONE_NUMBER = os.getenv('TWILIO_PHONE_NUMBER')  # API KEY: Twilio sender phone number

# --- Sky-Scrapper via RapidAPI (live flight search + prices) ---
RAPIDAPI_KEY  = os.getenv('RAPIDAPI_KEY')                                  # API KEY: your RapidAPI key
RAPIDAPI_HOST = os.getenv('RAPIDAPI_HOST', 'sky-scrapper.p.rapidapi.com')