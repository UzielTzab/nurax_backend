from datetime import timedelta
import os
from pathlib import Path

import cloudinary
import dj_database_url
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent

# Load environment variables from both config files
# In Docker: Docker Compose loads these via env_file, but we still load locally for safety
# In development: Must have both .env and config/postgres.env
load_dotenv(BASE_DIR / 'config' / 'postgres.env')  # Database variables
load_dotenv(BASE_DIR / '.env')  # Application variables

SECRET_KEY = os.getenv('SECRET_KEY', 'dev-key-change-in-prod-insecure')
DEBUG = os.getenv('DEBUG', 'True') == 'True'

ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', '*').split(',')


def _split_csv_env(name: str, default: str = ''):
    raw = os.getenv(name, default)
    return [item.strip() for item in raw.split(',') if item.strip()]


INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Third party
    'rest_framework',
    'rest_framework_simplejwt',
    'corsheaders',
    'cloudinary',
    'cloudinary_storage',
    'django_filters',
    'drf_spectacular',
    # Local apps - ARCHITECTURE_V2 (in apps/)
    'apps.accounts.apps.AccountsConfig',
    'apps.products.apps.ProductsConfig',
    'apps.sales.apps.SalesConfig',
    'apps.inventory.apps.InventoryConfig',
    'apps.expenses.apps.ExpensesConfig',
    'apps.carts.apps.CartsConfig',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',  # CORS must be first
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'core.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'core.wsgi.application'


def _database_config():
    database_url = os.getenv('DATABASE_URL')
    if database_url:
        return dj_database_url.config(default=database_url)

    db_host = os.getenv('DB_HOST')
    if db_host:
        return {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': os.getenv('DB_NAME'),
            'USER': os.getenv('DB_USER'),
            'PASSWORD': os.getenv('DB_PASSWORD'),
            'HOST': db_host,
            'PORT': os.getenv('DB_PORT', '5432'),
            'OPTIONS': {
                'sslmode': os.getenv('DB_SSLMODE', 'require'),
            },
        }

    return {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }


DATABASES = {
    'default': _database_config(),
}

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

# AUTH USER MODEL
AUTH_USER_MODEL = 'accounts.User'

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'utils.authentication.CookieJWTAuthentication',  # HttpOnly cookies
        'rest_framework_simplejwt.authentication.JWTAuthentication',  # Fallback para API clients con header
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'DEFAULT_PAGINATION_CLASS': 'utils.pagination.StandardResultsSetPagination',
    'PAGE_SIZE': 50,
    'DEFAULT_FILTER_BACKENDS': (
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ),
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=8),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=30),
}

CORS_ALLOWED_ORIGINS = _split_csv_env(
    'CORS_ALLOWED_ORIGINS',
    'http://localhost:5173,https://nurax.netlify.app'
)

# Permitir previews sin tener que actualizar settings en cada deploy.
CORS_ALLOWED_ORIGIN_REGEXES = _split_csv_env(
    'CORS_ALLOWED_ORIGIN_REGEXES',
    r"^https://.*\.netlify\.app$"
)

# CORS credentials - permitir envio de cookies
CORS_ALLOW_CREDENTIALS = True

# HttpOnly cookies (OWASP best practice)
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = os.getenv('SESSION_COOKIE_SAMESITE', 'Lax' if DEBUG else 'None')
SESSION_COOKIE_SECURE = not DEBUG

# Same for CSRF cookie
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SAMESITE = os.getenv('CSRF_COOKIE_SAMESITE', 'Lax' if DEBUG else 'None')
CSRF_COOKIE_SECURE = not DEBUG

# Agregar frontend a lista de sitios seguros para CSRF
CSRF_TRUSTED_ORIGINS = _split_csv_env(
    'CSRF_TRUSTED_ORIGINS',
    'http://localhost:5173,https://nurax.netlify.app,https://*.netlify.app'
)

CLOUDINARY_STORAGE = {
    'CLOUD_NAME': os.getenv('CLOUDINARY_CLOUD_NAME'),
    'API_KEY': os.getenv('CLOUDINARY_API_KEY'),
    'API_SECRET': os.getenv('CLOUDINARY_API_SECRET'),
}
DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'

cloudinary.config(
    cloud_name=os.getenv('CLOUDINARY_CLOUD_NAME'),
    api_key=os.getenv('CLOUDINARY_API_KEY'),
    api_secret=os.getenv('CLOUDINARY_API_SECRET'),
    secure=True,
)

SPECTACULAR_SETTINGS = {
    'TITLE': 'Nurax API',
    'DESCRIPTION': 'Documentación de la API de Nurax - Sistema de Gestión de Tiendas',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
    'SCHEMA_PATH_PREFIX': '/api/v1/',
    'ENUM_ADD_EXPLICIT_BLANK_NULLS': False,
    'COERCE_DECIMAL_TO_STRING': False,
    # Swagger UI Customization - Mejora de experiencia de búsqueda
    'SWAGGER_UI_SETTINGS': {
        'persistAuthorization': True,  # Mantener autenticación en refresh
        'displayOperationId': False,   # No mostrar operation IDs
        'filter': True,                # Habilitar filtro/buscador en los endpoints
        'showExtensions': False,       # Ocultar extensiones OpenAPI
        'deepLinking': True,           # Permitir deep linking a endpoints específicos
    },
}

# Pusher
PUSHER_APP_ID = os.getenv('PUSHER_APP_ID')
PUSHER_KEY = os.getenv('PUSHER_KEY')
PUSHER_SECRET = os.getenv('PUSHER_SECRET')
PUSHER_CLUSTER = os.getenv('PUSHER_CLUSTER')

