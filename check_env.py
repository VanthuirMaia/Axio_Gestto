#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para verificar qual ambiente Django está ativo
Uso: python check_env.py
"""

import os
import sys
from pathlib import Path

# Adiciona o projeto ao path
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

# Define DJANGO_ENV se não estiver definido
if 'DJANGO_ENV' not in os.environ:
    os.environ.setdefault('DJANGO_ENV', 'development')

# Configura Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

import django
django.setup()

from django.conf import settings

print("\n" + "="*60)
print("  VERIFICACAO DE AMBIENTE DJANGO")
print("="*60 + "\n")

# Detecta ambiente
env = os.environ.get('DJANGO_ENV', 'development')
print(f"Ambiente: {env.upper()}")

# Informações importantes
print(f"\nConfiguracoes Principais:")
print(f"   - DEBUG: {settings.DEBUG}")
print(f"   - ALLOWED_HOSTS: {settings.ALLOWED_HOSTS}")
print(f"   - SECRET_KEY: {'OK - Configurada' if settings.SECRET_KEY else 'ERRO - Nao configurada'}")

# Database
db_engine = settings.DATABASES['default']['ENGINE']
db_name = settings.DATABASES['default']['NAME']
print(f"\nBanco de Dados:")
if 'sqlite' in db_engine:
    print(f"   - Engine: SQLite")
    print(f"   - Arquivo: {db_name}")
elif 'postgresql' in db_engine:
    print(f"   - Engine: PostgreSQL")
    print(f"   - Nome: {db_name}")
    print(f"   - Host: {settings.DATABASES['default'].get('HOST', 'localhost')}")
    print(f"   - Port: {settings.DATABASES['default'].get('PORT', '5432')}")

# Email
print(f"\nEmail:")
print(f"   - Backend: {settings.EMAIL_BACKEND.split('.')[-1]}")
if 'console' in settings.EMAIL_BACKEND:
    print(f"   - Modo: Console (emails no terminal)")
else:
    print(f"   - Host: {settings.EMAIL_HOST}")
    print(f"   - Port: {settings.EMAIL_PORT}")
    print(f"   - From: {settings.DEFAULT_FROM_EMAIL}")

# Cache
if hasattr(settings, 'CACHES'):
    cache_backend = settings.CACHES['default']['BACKEND']
    print(f"\nCache:")
    if 'redis' in cache_backend.lower():
        print(f"   - Backend: Redis")
        print(f"   - Location: {settings.CACHES['default'].get('LOCATION', 'N/A')}")
    elif 'locmem' in cache_backend.lower():
        print(f"   - Backend: Local Memory")
    else:
        print(f"   - Backend: {cache_backend.split('.')[-1]}")

# Security
print(f"\nSeguranca:")
print(f"   - SSL Redirect: {'ATIVO' if getattr(settings, 'SECURE_SSL_REDIRECT', False) else 'INATIVO'}")
print(f"   - Session Cookie Secure: {'ATIVO' if getattr(settings, 'SESSION_COOKIE_SECURE', False) else 'INATIVO'}")
print(f"   - CSRF Cookie Secure: {'ATIVO' if getattr(settings, 'CSRF_COOKIE_SECURE', False) else 'INATIVO'}")
print(f"   - HSTS: {'ATIVO' if getattr(settings, 'SECURE_HSTS_SECONDS', 0) > 0 else 'INATIVO'}")

# Site URL
print(f"\nURLs:")
print(f"   - Site URL: {settings.SITE_URL}")

# Avisos de segurança
if env == 'production':
    issues = []

    if settings.DEBUG:
        issues.append("ERRO: DEBUG esta ativado em producao!")

    if 'MUDE-ISTO' in settings.SECRET_KEY or 'dev-secret' in settings.SECRET_KEY:
        issues.append("ERRO: SECRET_KEY nao foi alterada!")

    if not getattr(settings, 'SECURE_SSL_REDIRECT', False):
        issues.append("AVISO: SSL Redirect nao esta ativo")

    if 'sqlite' in db_engine:
        issues.append("AVISO: Usando SQLite em producao (recomenda-se PostgreSQL)")

    if issues:
        print(f"\nAVISOS DE SEGURANCA:")
        for issue in issues:
            print(f"   {issue}")
    else:
        print(f"\nOK: Configuracoes de seguranca validadas!")

elif env == 'development':
    print(f"\nOK: Ambiente de desenvolvimento configurado corretamente!")

print("\n" + "="*60 + "\n")
