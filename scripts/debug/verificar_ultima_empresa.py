#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os, sys, django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from assinaturas.models import Assinatura, HistoricoPagamento
from empresas.models import Empresa

# Última empresa
emp = Empresa.objects.latest('id')
print(f"Ultima empresa criada:")
print(f"  ID: {emp.id}")
print(f"  Nome: {emp.nome}")
print(f"  Email: {emp.email}")
print(f"  CNPJ: {emp.cnpj}")

# Assinatura
try:
    assinatura = Assinatura.objects.get(empresa=emp)
    print(f"\nAssinatura:")
    print(f"  Status: {assinatura.status}")
    print(f"  Subscription ID: {assinatura.subscription_id_externo or 'Nenhum'}")
    print(f"  Trial ativo: {assinatura.trial_ativo}")

    # Pagamentos
    pagamentos = HistoricoPagamento.objects.filter(assinatura=assinatura)
    print(f"\nPagamentos: {pagamentos.count()}")
    for p in pagamentos:
        print(f"  - R$ {p.valor} - {p.status} - {p.gateway}")
except Assinatura.DoesNotExist:
    print("\nSEM ASSINATURA!")
