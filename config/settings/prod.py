"""
Django settings - PRODUCTION
Configurações específicas para ambiente de produção
Foco em segurança, performance e estabilidade
"""

from .base import *
from decouple import config
import dj_database_url

# SECURITY: Debug MUST be False in production
DEBUG = False

# Allowed hosts - APENAS domínios de produção
ALLOWED_HOSTS = config('ALLOWED_HOSTS', cast=Csv())

# Database Configuration
# Usa PostgreSQL em produção (mais robusto e escalável)
# Suporta DATABASE_URL (Supabase/Heroku style) ou variáveis individuais
DATABASE_URL = config('DATABASE_URL', default=None)

if DATABASE_URL:
    # Produção: Usa DATABASE_URL do Supabase/Heroku
    DATABASES = {
        'default': dj_database_url.parse(DATABASE_URL, conn_max_age=600)
    }
else:
    # Produção: Usa variáveis individuais
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': config('DB_NAME'),
            'USER': config('DB_USER'),
            'PASSWORD': config('DB_PASSWORD'),
            'HOST': config('DB_HOST'),
            'PORT': config('DB_PORT', default='5432'),
            'CONN_MAX_AGE': 600,  # Mantém conexões abertas por 10 min
            'OPTIONS': {
                'connect_timeout': 10,
            },
        }
    }

# Email Configuration (SMTP real)
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = config('EMAIL_HOST')
EMAIL_PORT = config('EMAIL_PORT', cast=int)
EMAIL_USE_TLS = config('EMAIL_USE_TLS', cast=bool)
EMAIL_HOST_USER = config('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD')
DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL')

# Logging para produção (mais restrito, foco em erros)
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': BASE_DIR / 'logs' / 'django.log',
            'maxBytes': 1024 * 1024 * 10,  # 10 MB
            'backupCount': 5,
            'formatter': 'verbose',
        },
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['file', 'console'],
        'level': 'WARNING',
    },
    'loggers': {
        'django': {
            'handlers': ['file', 'console'],
            'level': 'WARNING',
            'propagate': False,
        },
        'django.security': {
            'handlers': ['file', 'console'],
            'level': 'ERROR',
            'propagate': False,
        },
    },
}

# Cache com Redis (performance)
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': config('REDIS_URL', default='redis://redis:6379/1'),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'SOCKET_CONNECT_TIMEOUT': 5,
            'SOCKET_TIMEOUT': 5,
            'CONNECTION_POOL_KWARGS': {
                'max_connections': 50,
                'retry_on_timeout': True,
            },
        },
        'KEY_PREFIX': 'gestto',
        'TIMEOUT': 300,  # 5 minutos default
    }
}

# Session usando cache (Redis) para performance
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS = 'default'

# ============================================
# SECURITY SETTINGS - PRODUÇÃO
# ============================================

# HTTPS/SSL
SECURE_SSL_REDIRECT = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Permite healthcheck em HTTP (vem de 127.0.0.1 interno)
SECURE_REDIRECT_EXEMPT = [r'^health/$']

# HSTS (HTTP Strict Transport Security)
SECURE_HSTS_SECONDS = 31536000  # 1 ano
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Cookies seguros
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'
CSRF_COOKIE_SAMESITE = 'Lax'

# Content Security Policy
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = 'DENY'

# ============================================
# CELERY CONFIGURATION (PRODUÇÃO)
# ============================================

CELERY_BROKER_URL = config('CELERY_BROKER_URL', default='redis://redis:6379/0')
CELERY_RESULT_BACKEND = config('CELERY_RESULT_BACKEND', default='redis://redis:6379/0')
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = TIME_ZONE
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_TIME_LIMIT = 30 * 60  # 30 minutos
CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP = True

# Celery Beat Schedule (tarefas agendadas)
from celery.schedules import crontab

CELERY_BEAT_SCHEDULE = {
    'gerar-agendamentos-recorrentes': {
        'task': 'agendamentos.tasks.gerar_agendamentos_recorrentes',
        'schedule': crontab(hour=0, minute=0),  # Diariamente às 00:00
    },
    'limpar-recorrencias-expiradas': {
        'task': 'agendamentos.tasks.limpar_recorrencias_expiradas',
        'schedule': crontab(hour=2, minute=0, day_of_week=0),  # Segundas às 02:00
    },
}

# ============================================
# ADMIN ACCESS - PRODUÇÃO
# ============================================

# Admin URL customizada (segurança por obscuridade)
# Defina no .env: ADMIN_URL=sua-url-secreta-admin
ADMIN_URL = config('ADMIN_URL', default='admin/')

# ============================================
# PERFORMANCE - PRODUÇÃO
# ============================================

# Template caching
# IMPORTANTE: Quando loaders é definido, APP_DIRS deve ser False
TEMPLATES[0]['APP_DIRS'] = False
TEMPLATES[0]['OPTIONS']['loaders'] = [
    ('django.template.loaders.cached.Loader', [
        'django.template.loaders.filesystem.Loader',
        'django.template.loaders.app_directories.Loader',
    ]),
]

# Compress static files
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

print("""
============================================================
   AMBIENTE DE PRODUCAO ATIVO
   - DEBUG: Desabilitado
   - Database: PostgreSQL
   - Email: SMTP Real
   - Cache: Redis
   - HTTPS: Ativado
   - Security: Maxima
   Ambiente seguro e otimizado
============================================================
""")
