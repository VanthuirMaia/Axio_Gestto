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
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
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