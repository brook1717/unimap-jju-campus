import glob
import os
from pathlib import Path

from dotenv import load_dotenv

# Load .env file when present (local dev).  Docker passes vars via environment:,
# so load_dotenv() does NOT override already-set environment variables.
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-insecure-change-me')

DEBUG = os.environ.get('DEBUG', 'True') == 'True'

ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')

# ─── Application Definition ────────────────────────────────────────────────

DJANGO_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.gis',
]

THIRD_PARTY_APPS = [
    'corsheaders',
    'rest_framework',
    'rest_framework_gis',
    'django_filters',
    'drf_spectacular',
]

LOCAL_APPS = [
    'users',
    'locations',
    'facilities',
    'routing',
]

# Custom user model — must be declared before any migration that references auth
AUTH_USER_MODEL = 'users.User'

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

MIDDLEWARE = [
    # CorsMiddleware MUST be placed as high as possible — before any middleware
    # that generates responses (e.g. CommonMiddleware, WhiteNoiseMiddleware).
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'unimap_backend.urls'

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

WSGI_APPLICATION = 'unimap_backend.wsgi.application'

# ─── Database (PostgreSQL + PostGIS) ───────────────────────────────────────

DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': os.environ.get('POSTGRES_DB', 'unimap_db'),
        'USER': os.environ.get('POSTGRES_USER', 'unimap_user'),
        'PASSWORD': os.environ.get('POSTGRES_PASSWORD', 'unimap_pass'),
        'HOST': os.environ.get('POSTGRES_HOST', 'db'),
        'PORT': os.environ.get('POSTGRES_PORT', '5432'),
    }
}

# ─── Password Validation ───────────────────────────────────────────────────

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ─── Internationalisation ──────────────────────────────────────────────────

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Africa/Addis_Ababa'
USE_I18N = True
USE_TZ = True

# ─── Static & Media Files ─────────────────────────────────────────────────
# Local defaults — used when USE_S3 is not set or False.
# To enable AWS S3, set USE_S3=True plus the AWS_* vars in .env.

USE_S3 = os.environ.get('USE_S3', 'False') == 'True'

if USE_S3:
    AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID', '')
    AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY', '')
    AWS_STORAGE_BUCKET_NAME = os.environ.get('AWS_STORAGE_BUCKET_NAME', '')
    AWS_S3_REGION_NAME = os.environ.get('AWS_S3_REGION_NAME', 'us-east-1')
    AWS_S3_CUSTOM_DOMAIN = f'{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com'
    AWS_DEFAULT_ACL = 'public-read'
    STATIC_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/static/'
    MEDIA_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/media/'
else:
    STATIC_URL = '/static/'
    STATIC_ROOT = BASE_DIR / 'staticfiles'
    MEDIA_URL = '/media/'
    MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ─── Django REST Framework ────────────────────────────────────────────────

REST_FRAMEWORK = {
    # Open for development; switch to IsAuthenticated before production
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',
    ],
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
    ],
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 100,
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}

# ─── drf-spectacular (OpenAPI 3.0) ────────────────────────────────────────

SPECTACULAR_SETTINGS = {
    'TITLE': 'UniMap API',
    'VERSION': '1.0.0',
    'DESCRIPTION': (
        'Spatial REST API powering UniMap — the smart campus navigation system '
        'for Jigjiga University (JJU). Endpoints expose GeoJSON-compliant data '
        'for campus buildings, facilities, and walkable paths, plus a '
        'PostGIS-powered nearest-building lookup and a NetworkX routing engine.'
    ),
    'SERVE_INCLUDE_SCHEMA': False,
    'COMPONENT_SPLIT_REQUEST': True,
    'SCHEMA_PATH_PREFIX': r'/api/',
    'SORT_OPERATIONS': True,
}

# ─── CORS ─────────────────────────────────────────────────────────────────
# Explicit allow-list for cross-origin requests.  In DEBUG mode the wildcard
# is also enabled for convenience; set DEBUG=False in production and update
# CORS_ALLOWED_ORIGINS with your deployed frontend URL.
CORS_ALLOWED_ORIGINS = [
    'http://localhost:5173',   # Vite dev server
    'http://127.0.0.1:5173',
    'http://localhost:3000',
]
CORS_ALLOW_ALL_ORIGINS = DEBUG  # True in dev, False in prod

# ─── GeoDjango Library Paths ──────────────────────────────────────────────
# In the Docker container (Debian Bookworm + ldconfig) Django auto-detects
# GDAL 3.6 and GEOS 3.11 via ctypes.  The glob fallback below pins the
# versioned .so when auto-detection fails (e.g. custom base images).
# Override at any time by setting GDAL_LIBRARY_PATH / GEOS_LIBRARY_PATH in .env.

_gdal_env = os.environ.get('GDAL_LIBRARY_PATH', '')
_geos_env = os.environ.get('GEOS_LIBRARY_PATH', '')

if _gdal_env:
    GDAL_LIBRARY_PATH = _gdal_env
else:
    _gdal_candidates = sorted(glob.glob('/usr/lib/x86_64-linux-gnu/libgdal.so.*'))
    if _gdal_candidates:
        GDAL_LIBRARY_PATH = _gdal_candidates[-1]

if _geos_env:
    GEOS_LIBRARY_PATH = _geos_env
else:
    _geos_candidates = sorted(glob.glob('/usr/lib/x86_64-linux-gnu/libgeos_c.so.*'))
    if _geos_candidates:
        GEOS_LIBRARY_PATH = _geos_candidates[-1]
