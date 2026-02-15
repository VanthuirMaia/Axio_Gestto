#!/usr/bin/env python
"""Script para verificar planos e assinaturas"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from assinaturas.models import Plano, Assinatura
from empresas.models import Empresa

print("\n=== PLANOS ===")
for p in Plano.objects.all():
    status = "OK" if p.stripe_price_id else "SEM PRICE ID"
    print(f"  {p.nome}: stripe_price_id={p.stripe_price_id or '(VAZIO)'} [{status}]")

print("\n=== ULTIMAS 5 EMPRESAS ===")
for e in Empresa.objects.order_by('-id')[:5]:
    print(f"  ID={e.id} | {e.nome} | {e.email} | origem={e.origem_cadastro}")

print("\n=== ASSINATURAS SEM CUSTOMER_ID_EXTERNO ===")
for a in Assinatura.objects.filter(customer_id_externo='').order_by('-id')[:10]:
    print(f"  Empresa: {a.empresa.nome} (ID={a.empresa.id}) | gateway={a.gateway} | status={a.status}")
