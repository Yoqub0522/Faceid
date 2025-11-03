import os
from pathlib import Path

from environ import environ

env = environ.Env()
BASE_DIR = Path(__file__).resolve().parent.parent
environ.Env.read_env(os.path.join(BASE_DIR, ".env"))



SECRET_KEY = 'replace-this-with-secure-key'
DEBUG = True
ALLOWED_HOSTS = ["*"]

INSTALLED_APPS = [
    "jazzmin",
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'attendance',
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

ROOT_URLCONF = 'faceid_mvt.urls'

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

WSGI_APPLICATION = 'faceid_mvt.wsgi.application'

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': BASE_DIR / 'db.sqlite3',
#     }
# }
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': env('DB_NAME'),
        'USER': env('DB_USER'),
        'PASSWORD': env('DB_PASSWORD'),
        'HOST': env('DB_HOST'),
        'PORT': env('DB_PORT'),
    }
}

AUTH_PASSWORD_VALIDATORS = []

LANGUAGE_CODE = 'uz'
TIME_ZONE = 'Asia/Tashkent'
USE_I18N = True
USE_TZ = True

# project/settings.py (QO'SHIMCHALAR)
# Face Recognition sozlamalari
FACE_DISTANCE_THRESHOLD = 0.6  # Yuz masofasi chegarasi
MAX_IMAGE_SIZE = 5 * 1024 * 1024  # 5MB
MAX_ENCODINGS_PER_EMPLOYEE = 10

# Cache sozlamalari (Agar Redis bo'lsa)
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
    }
}


LOGS_DIR = BASE_DIR / 'logs'
LOGS_DIR.mkdir(exist_ok=True)


LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
    },
    'loggers': {
        'attendance': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}
# Xavfsizlik sozlamalari
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

# Static fayllar uchun
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']  # bu loyihadagi static papka
STATIC_ROOT = BASE_DIR / 'staticfiles'    # collectstatic natijasi

# Media fayllar
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'


# messages
from django.contrib.messages import constants as messages
MESSAGE_TAGS = {
    messages.DEBUG: 'secondary',
    messages.INFO: 'info',
    messages.SUCCESS: 'success',
    messages.WARNING: 'warning',
    messages.ERROR: 'danger',
}
FACE_DISTANCE_THRESHOLD = 1

JAZZMIN_SETTINGS = {
    "site_title": "EduEyes Admin",
    "site_header": "EduEyes",
    "site_brand": "EduEyes.io",
    "welcome_sign": "Xush kelibsiz, admin!",
    "copyright": "© EduEyes",
    "show_ui_builder": True,  # UI builder’ni yoqadi
}

JAZZMIN_UI_TWEAKS = {
    "theme": "cerulean",   # boshqa variantlar: darkly, cerulean, cosmo, minty ...
    "navbar_fixed": True,
    "sidebar_fixed": True,
    "show_ui_builder": True,
}

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
CSRF_TRUSTED_ORIGINS = [

    'https://faceid.yoqubaxmedov.xyz',
]

CORS_ALLOWED_ORIGINS = [

    "https://faceid.yoqubaxmedov.xyz",


]