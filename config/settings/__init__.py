"""
Django Settings Package
Carrega automaticamente o settings correto baseado na variável DJANGO_ENV
"""

import os

# Detecta o ambiente através da variável DJANGO_ENV
# Valores aceitos: 'development', 'production', 'staging'
# Default: development
DJANGO_ENV = os.environ.get('DJANGO_ENV', 'development')

if DJANGO_ENV == 'production':
    from .prod import *
elif DJANGO_ENV == 'staging':
    # Você pode criar um staging.py no futuro se necessário
    from .prod import *
    DEBUG = False  # Staging também deve ter DEBUG=False
else:
    # development (default)
    from .dev import *
