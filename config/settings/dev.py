"""
Django settings - DEVELOPMENT
Configurações específicas para ambiente de desenvolvimento local
"""

from .base import *
from decouple import config

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# Allowed hosts para desenvolvimento
ALLOWED_HOSTS = ['localhost', '127.0.0.1', '0.0.0.0', '*']

# Database
# Usa SQLite por padrão em desenvolvimento (mais simples)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Email Configuration (Console backend - não envia emails reais)
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
EMAIL_HOST = 'localhost'
EMAIL_PORT = 1025
EMAIL_USE_TLS = False
EMAIL_HOST_USER = ''
EMAIL_HOST_PASSWORD = ''
DEFAULT_FROM_EMAIL = 'dev@localhost'

# Logging mais verboso para desenvolvimento
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        'django.db.backends': {
            'handlers': ['console'],
            'level': 'DEBUG',  # Mostra queries SQL no console
            'propagate': False,
        },
    },
}

# Debug Toolbar (útil para desenvolvimento)
# Descomente se quiser instalar: pip install django-debug-toolbar
"""
INSTALLED_APPS += ['debug_toolbar']
MIDDLEWARE += ['debug_toolbar.middleware.DebugToolbarMiddleware']
INTERNAL_IPS = ['127.0.0.1']
"""

# CORS mais permissivo em desenvolvimento
CORS_ALLOW_ALL_ORIGINS = True

# Cache simples em memória
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
    }
}

# Desabilitar segurança HTTPS em desenvolvimento
SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
SECURE_HSTS_SECONDS = 0
SECURE_HSTS_INCLUDE_SUBDOMAINS = False
SECURE_HSTS_PRELOAD = False

# Site URL para desenvolvimento
SITE_URL = 'http://localhost:8000'

# Sandbox para gateways de pagamento
ASAAS_SANDBOX = True
STRIPE_SECRET_KEY = config('STRIPE_SECRET_KEY', default='sk_test_...')

# Evolution API (WhatsApp Integration) - IMPORTANTE: Sobrescrever valores do base.py
EVOLUTION_API_URL = config('EVOLUTION_API_URL', default='')
EVOLUTION_API_KEY = config('EVOLUTION_API_KEY', default='')

# Debug: Mostrar configurações da Evolution API no console
if EVOLUTION_API_URL:
    print(f"[OK] Evolution API URL configurada: {EVOLUTION_API_URL}")
else:
    print("[AVISO] EVOLUTION_API_URL nao configurada no .env!")

if EVOLUTION_API_KEY:
    print(f"[OK] Evolution API Key configurada: {EVOLUTION_API_KEY[:10]}...")
else:
    print("[AVISO] EVOLUTION_API_KEY nao configurada no .env!")

print("""
============================================================
   AMBIENTE DE DESENVOLVIMENTO ATIVO
   - DEBUG: Ativado
   - Database: SQLite (local)
   - Email: Console Backend (nao envia emails reais)
   - CORS: Permissivo
   - HTTPS: Desabilitado
   ATENCAO: NAO USE ESTE AMBIENTE EM PRODUCAO!
============================================================
""")
