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
    'axes',  # Monitoramento de segurança
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

    # Segurança - Django Axes
    'axes.middleware.AxesMiddleware',

    # Landing Page Security Monitoring
    'landing.middleware.LandingSecurityMonitoringMiddleware',

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

# API Configuration (Gestto API para integrações externas)
GESTTO_API_KEY = config('GESTTO_API_KEY', default='desenvolvimento-inseguro-mudar-em-producao')
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

# ============================================
# SEGURANÇA E LOGGING
# ============================================

# Django Axes - Proteção contra tentativas de login
AUTHENTICATION_BACKENDS = [
    'axes.backends.AxesStandaloneBackend',  # Deve vir primeiro
    'django.contrib.auth.backends.ModelBackend',
]

AXES_FAILURE_LIMIT = 5  # Bloqueia após 5 tentativas falhas
AXES_COOLOFF_TIME = 1  # Bloqueia por 1 hora
AXES_RESET_ON_SUCCESS = True
AXES_ENABLE_ACCESS_FAILURE_LOG = True
AXES_LOCKOUT_TEMPLATE = None  # Use template padrão
AXES_LOCKOUT_URL = None  # URL de redirecionamento quando bloqueado
AXES_VERBOSE = True  # Logs detalhados
# Nova configuração (v8.0+)
AXES_LOCK_OUT_AT_FAILURE = True
AXES_LOCKOUT_PARAMETERS = [["username", "ip_address"]]  # Bloqueia por combinação username+IP

# Logging Configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '[{levelname}] {asctime} {name} - {message}',
            'style': '{',
            'datefmt': '%Y-%m-%d %H:%M:%S',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse',
        },
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
        'landing_file': {
            'level': 'WARNING',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': BASE_DIR / 'data' / 'logs' / 'landing.log',
            'maxBytes': 1024 * 1024 * 10,  # 10 MB
            'backupCount': 5,
            'formatter': 'verbose',
        },
        'security_file': {
            'level': 'WARNING',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': BASE_DIR / 'data' / 'logs' / 'security.log',
            'maxBytes': 1024 * 1024 * 10,  # 10 MB
            'backupCount': 5,
            'formatter': 'verbose',
        },
        'app_file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': BASE_DIR / 'data' / 'logs' / 'app.log',
            'maxBytes': 1024 * 1024 * 10,  # 10 MB
            'backupCount': 5,
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'app_file'],
            'level': 'INFO',
            'propagate': False,
        },
        'landing': {
            'handlers': ['console', 'landing_file', 'security_file'],
            'level': 'INFO',
            'propagate': False,
        },
        'axes': {
            'handlers': ['console', 'security_file'],
            'level': 'WARNING',
            'propagate': False,
        },
        'django.security': {
            'handlers': ['console', 'security_file'],
            'level': 'WARNING',
            'propagate': False,
        },
    },
}

# Headers de Segurança Adicionais
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = 'DENY'  # Previne clickjacking
