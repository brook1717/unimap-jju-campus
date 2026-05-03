import glob
import os
from pathlib import Path

import dj_database_url
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
    'leaflet',
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

# django-leaflet map widget settings (used in GIS admin)
LEAFLET_CONFIG = {
    'DEFAULT_CENTER': (9.3585, 42.8244),   # Jigjiga University
    'DEFAULT_ZOOM': 16,
    'MIN_ZOOM': 3,
    'MAX_ZOOM': 19,
    'TILES': [
        (
            'CartoDB Positron',
            'https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png',
            {
                'attribution': '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> &copy; <a href="https://carto.com/attributions">CARTO</a>',
                'subdomains': 'abcd',
                'maxZoom': 19,
            },
        ),
    ],
    'SCALE': 'both',
    'RESET_VIEW': False,
}

MIDDLEWARE = [
    # CorsMiddleware MUST be placed as high as possible — before any middleware
    # that generates responses (e.g. CommonMiddleware, WhiteNoiseMiddleware).
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
# Prefer DATABASE_URL when set (production / Docker).  Falls back to individual
# POSTGRES_* env vars for backwards-compatibility with the existing compose file.

_DATABASE_URL = os.environ.get('DATABASE_URL', '')

if _DATABASE_URL:
    DATABASES = {
        'default': dj_database_url.parse(
            _DATABASE_URL,
            engine='django.contrib.gis.db.backends.postgis',
        ),
    }
else:
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

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# WhiteNoise serves static files directly from the WSGI app — no nginx needed.
# In dev (DEBUG=True) WHITENOISE_USE_FINDERS auto-serves un-collected files.
WHITENOISE_USE_FINDERS = DEBUG
STORAGES = {
    'staticfiles': {
        'BACKEND': 'whitenoise.storage.CompressedManifestStaticFilesStorage',
    },
}

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
    'EXCEPTION_HANDLER': 'unimap_backend.exceptions.custom_exception_handler',
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

# ─── Routing / Topology ──────────────────────────────────────────────────
# Absolute path to the pre-built GeoJSON network file.  Override via the
# TOPOLOGY_GEOJSON_PATH environment variable (useful in Docker where the
# data/ volume is mounted at /data/).
TOPOLOGY_GEOJSON_PATH = os.environ.get(
    'TOPOLOGY_GEOJSON_PATH',
    str(BASE_DIR.parent / 'data' / 'topology_paths.geojson'),
)

# ─── Logging ────────────────────────────────────────────────────────────────
# App loggers ('routing', 'locations', 'unimap_backend') log at DEBUG.
# Root logger stays at WARNING to suppress noisy third-party output.

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'standard',
        },
    },
    'loggers': {
        'routing': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'locations': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'unimap_backend': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'WARNING',
    },
}

# ─── CORS ─────────────────────────────────────────────────────────────────
# In production, set CORS_ALLOWED_ORIGINS as a comma-separated string in .env.
# In DEBUG mode the wildcard is enabled for convenience.

_cors_env = os.environ.get('CORS_ALLOWED_ORIGINS', '')
CORS_ALLOWED_ORIGINS = [
    origin.strip()
    for origin in _cors_env.split(',')
    if origin.strip()
] if _cors_env else [
    'http://localhost:5173',    # Vite default
    'http://localhost:5174',    # Vite fallback (port in use)
    'http://127.0.0.1:5173',
    'http://127.0.0.1:5174',
    'http://localhost:3000',    # CRA / alternate dev server
    'http://127.0.0.1:3000',
]
CORS_ALLOW_ALL_ORIGINS = DEBUG  # True in dev, False in prod

# ─── CSRF ────────────────────────────────────────────────────────────────
# Required when the admin panel is accessed behind HTTPS in production.
# Set CSRF_TRUSTED_ORIGINS as a comma-separated string in .env, e.g.:
#   CSRF_TRUSTED_ORIGINS=https://admin.unimap.example.com,https://unimap.example.com
_csrf_env = os.environ.get('CSRF_TRUSTED_ORIGINS', '')
CSRF_TRUSTED_ORIGINS = [
    origin.strip()
    for origin in _csrf_env.split(',')
    if origin.strip()
] if _csrf_env else []

# ─── Production Security Hardening ──────────────────────────────────────
# These settings are only activated when DEBUG=False to prevent information
# leakage and enforce HTTPS-only access in production.
if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SECURE_HSTS_SECONDS = 31536000        # 1 year
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_BROWSER_XSS_FILTER = True
    X_FRAME_OPTIONS = 'DENY'

    # Remove the browsable API renderer in production
    REST_FRAMEWORK['DEFAULT_RENDERER_CLASSES'] = [
        'rest_framework.renderers.JSONRenderer',
    ]

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
