"""
Django settings - BASE CONFIGURATION
Configurações compartilhadas entre todos os ambientes (dev, prod, staging, etc)
"""

from pathlib import Path
from decouple import config, Csv
import os

# Build paths inside the project
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('SECRET_KEY')

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Apps do projeto
    'landing.apps.LandingConfig',
    'core.apps.CoreConfig',
    'empresas.apps.EmpresasConfig',
    'clientes.apps.ClientesConfig',
    'agendamentos.apps.AgendamentosConfig',
    'financeiro.apps.FinanceiroConfig',
    'configuracoes.apps.ConfiguracoesConfig',
    'assinaturas.apps.AssinaturasConfig',

    # Third party
    'django_apscheduler',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

    # SaaS Middlewares
    'core.middleware.AssinaturaExpiracaoMiddleware',
    'core.middleware.LimitesPlanoMiddleware',
    'core.middleware.UsageTrackingMiddleware',
]

ROOT_URLCONF = 'config.urls'

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

WSGI_APPLICATION = 'config.wsgi.application'

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Internationalization
LANGUAGE_CODE = 'pt-br'
TIME_ZONE = 'America/Recife'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Media files (uploads)
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# WhiteNoise - Servir arquivos estáticos em produção
STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

# WhiteNoise - Configuração de MIME types para PWA
WHITENOISE_MIMETYPES = {
    '.json': 'application/manifest+json',
}

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Custom user model
AUTH_USER_MODEL = 'core.Usuario'

# Authentication URLs
LOGIN_URL = '/app/login/'
LOGIN_REDIRECT_URL = '/app/dashboard/'
LOGOUT_REDIRECT_URL = 'login'

# Password Reset Configuration
PASSWORD_RESET_TIMEOUT = 3600  # 1 hora em segundos

# CORS Configuration
CORS_ALLOWED_ORIGINS = config('CORS_ALLOWED_ORIGINS', default='http://localhost:3000,http://127.0.0.1:3000', cast=Csv())

# REST Framework Configuration
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle',
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/hour',
        'user': '1000/hour',
        'bot_api': '500/hour',
    }
}

# ============================================
# SaaS CONFIGURATION
# ============================================

# Site URL (para emails e redirects)
SITE_URL = config('SITE_URL', default='http://localhost:8000')

# API Configuration (n8n Bot)
N8N_API_KEY = config('N8N_API_KEY', default='desenvolvimento-inseguro-mudar-em-producao')
N8N_WEBHOOK_URL = config('N8N_WEBHOOK_URL', default='')

# Stripe (Cartão de Crédito - Internacional)
STRIPE_PUBLIC_KEY = config('STRIPE_PUBLIC_KEY', default='')
STRIPE_SECRET_KEY = config('STRIPE_SECRET_KEY', default='')
STRIPE_WEBHOOK_SECRET = config('STRIPE_WEBHOOK_SECRET', default='')

# Asaas (Boleto/PIX/Cartão - Brasil)
ASAAS_API_KEY = config('ASAAS_API_KEY', default='')
ASAAS_SANDBOX = config('ASAAS_SANDBOX', default=True, cast=bool)

# Evolution API (WhatsApp Integration)
EVOLUTION_API_URL = config('EVOLUTION_API_URL', default='')
EVOLUTION_API_KEY = config('EVOLUTION_API_KEY', default='')

# ============================================
# ADMIN INTERFACE
# ============================================

X_FRAME_OPTIONS = 'SAMEORIGIN'
SILENCED_SYSTEM_CHECKS = ['security.W019']

# Material Admin Customization
MATERIAL_ADMIN_SITE = {
    'HEADER': 'Axio Gestto Admin',
    'TITLE': 'Axio Gestto',
    'FAVICON': '/static/img/favicon.ico',
    'MAIN_BG_COLOR': '#0d6efd',
    'MAIN_HOVER_COLOR': '#0a58ca',
    'PROFILE_PICTURE': '/static/img/user.png',
    'PROFILE_BG': '/static/img/profile-bg.jpg',
    'LOGIN_LOGO': '/static/img/logo.png',
    'LOGOUT_ON_PASSWORD_CHANGE': False,
    'SHOW_THEMES': True,
    'SHOW_COUNTS': True,
    'APP_ICONS': {
        'auth': 'people',
        'core': 'dashboard',
        'empresas': 'business',
        'clientes': 'people_outline',
        'agendamentos': 'event',
        'financeiro': 'attach_money',
    }
}

# ============================================
# APSCHEDULER CONFIGURATION
# ============================================

APSCHEDULER_DATETIME_FORMAT = "N j, Y, f:s a"
APSCHEDULER_RUN_NOW_TIMEOUT = 25
