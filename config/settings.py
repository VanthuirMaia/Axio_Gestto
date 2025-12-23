from pathlib import Path
from decouple import config, Csv
import os

BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('SECRET_KEY')
DEBUG = config('DEBUG', default=False, cast=bool)
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='localhost,127.0.0.1', cast=Csv())

INSTALLED_APPS = [
    'django.contrib.admin',  # ← Mantenha (para casos de emergência)
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Apps do projeto
    'core.apps.CoreConfig',
    'empresas.apps.EmpresasConfig',
    'clientes.apps.ClientesConfig',
    'agendamentos.apps.AgendamentosConfig',
    'financeiro.apps.FinanceiroConfig',
    'configuracoes.apps.ConfiguracoesConfig',  # ← ADICIONE
    
    # Third party
    'django_apscheduler',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
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

DATABASES = {
    'default': {
        'ENGINE': config('DB_ENGINE', default='django.db.backends.sqlite3'),
        'NAME': config('DB_NAME', default=str(BASE_DIR / 'db.sqlite3')),
        'USER': config('DB_USER', default=''),
        'PASSWORD': config('DB_PASSWORD', default=''),
        'HOST': config('DB_HOST', default=''),
        'PORT': config('DB_PORT', default=''),
    }
}


AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'pt-br'
TIME_ZONE = 'America/Recife'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

AUTH_USER_MODEL = 'core.Usuario'

LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'dashboard'
LOGOUT_REDIRECT_URL = 'login'

# Email Configuration
EMAIL_BACKEND = config('EMAIL_BACKEND', default='django.core.mail.backends.console.EmailBackend')
EMAIL_HOST = config('EMAIL_HOST', default='smtp.gmail.com')
EMAIL_PORT = config('EMAIL_PORT', default=587, cast=int)
EMAIL_USE_TLS = config('EMAIL_USE_TLS', default=True, cast=bool)
EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')
DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL', default='noreply@axiogesto.com')

# Password Reset Configuration
PASSWORD_RESET_TIMEOUT = 3600  # 1 hora em segundos

# API Configuration (n8n Bot)
N8N_API_KEY = config('N8N_API_KEY', default='desenvolvimento-inseguro-mudar-em-producao')

CORS_ALLOWED_ORIGINS = config('CORS_ALLOWED_ORIGINS', default='http://localhost:3000,http://127.0.0.1:3000', cast=Csv())

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
        'anon': '100/hour',  # 100 requests por hora para anônimos
        'user': '1000/hour',  # 1000 requests por hora para autenticados
        'bot_api': '500/hour',  # 500 requests por hora para API do bot
    }
}

if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True

# ============================================
# MATERIAL ADMIN CUSTOMIZATION
# ============================================
MATERIAL_ADMIN_SITE = {
    'HEADER': 'Axio Gestto Admin',
    'TITLE': 'Axio Gestto',
    'FAVICON': '/static/img/favicon.ico',  # Se tiver favicon
    'MAIN_BG_COLOR': '#0d6efd',  # Azul do seu sistema
    'MAIN_HOVER_COLOR': '#0a58ca',
    'PROFILE_PICTURE': '/static/img/user.png',  # Se tiver
    'PROFILE_BG': '/static/img/profile-bg.jpg',  # Se tiver
    'LOGIN_LOGO': '/static/img/logo.png',  # Se tiver
    'LOGOUT_ON_PASSWORD_CHANGE': False,
    'SHOW_THEMES': True,  # Permite trocar tema
    'SHOW_COUNTS': True,  # Mostra contadores
    'APP_ICONS': {  # Ícones customizados
        'auth': 'people',
        'core': 'dashboard',
        'empresas': 'business',
        'clientes': 'people_outline',
        'agendamentos': 'event',
        'financeiro': 'attach_money',
    }
}

APSCHEDULER_DATETIME_FORMAT = "N j, Y, f:s a"
APSCHEDULER_RUN_NOW_TIMEOUT = 25

# ============================================
# ADMIN INTERFACE
# ============================================
X_FRAME_OPTIONS = 'SAMEORIGIN'
SILENCED_SYSTEM_CHECKS = ['security.W019']

# ============================================
# CELERY CONFIGURATION
# ============================================
# Configurações comentadas para desenvolvimento local sem Redis
# Descomente quando rodar com Docker ou Redis local
"""
CELERY_BROKER_URL = config('CELERY_BROKER_URL', default='redis://redis:6379/0')
CELERY_RESULT_BACKEND = config('CELERY_RESULT_BACKEND', default='redis://redis:6379/0')
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = TIME_ZONE

# Celery Beat Schedule (tarefas agendadas)
from celery.schedules import crontab

CELERY_BEAT_SCHEDULE = {
    # Gerar agendamentos recorrentes diariamente à meia-noite
    'gerar-agendamentos-recorrentes': {
        'task': 'agendamentos.tasks.gerar_agendamentos_recorrentes',
        'schedule': crontab(hour=0, minute=0),  # Diariamente às 00:00
    },
    # Limpar recorrências expiradas semanalmente (opcional)
    'limpar-recorrencias-expiradas': {
        'task': 'agendamentos.tasks.limpar_recorrencias_expiradas',
        'schedule': crontab(hour=2, minute=0, day_of_week=0),  # Segundas às 02:00
    },
}
"""