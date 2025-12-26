#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para testar webhook manualmente
"""

import os
import sys
import django

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from assinaturas.models import Assinatura, HistoricoPagamento
from django.utils.timezone import now

def ativar_ultima_assinatura():
    """Ativa manualmente a última assinatura em trial"""

    # Buscar última assinatura em trial
    assinatura = Assinatura.objects.filter(status='trial').last()

    if not assinatura:
        print("[INFO] Nenhuma assinatura em trial encontrada!")
        print("\nVerificando todas as assinaturas:")
        for ass in Assinatura.objects.all().order_by('-id')[:3]:
            print(f"  - {ass.empresa.nome}: {ass.status}")
        return

    print(f"[*] Assinatura encontrada:")
    print(f"    Empresa: {assinatura.empresa.nome}")
    print(f"    Email: {assinatura.empresa.email}")
    print(f"    Status atual: {assinatura.status}")
    print(f"    Subscription ID: {assinatura.subscription_id_externo}")

    # Ativar assinatura
    assinatura.status = 'ativa'
    assinatura.trial_ativo = False
    assinatura.save()
    print(f"\n[OK] Assinatura ativada!")

    # Criar histórico de pagamento simulado
    historico = HistoricoPagamento.objects.create(
        assinatura=assinatura,
        valor=assinatura.plano.preco_mensal,
        status='aprovado',
        gateway='stripe',
        transaction_id=f'pi_test_{assinatura.id}_{now().timestamp()}',
        payment_method='card',
        data_aprovacao=now(),
        metadados={'descricao': f'Pagamento inicial - {assinatura.plano.get_nome_display()}'},
        webhook_payload={'manual': True, 'nota': 'Criado manualmente para teste'}
    )

    print(f"[OK] Histórico de pagamento criado!")
    print(f"    ID: {historico.id}")
    print(f"    Valor: R$ {historico.valor}")
    print(f"    Status: {historico.status}")

    print(f"\n[*] Resumo:")
    print(f"    Total de assinaturas ativas: {Assinatura.objects.filter(status='ativa').count()}")
    print(f"    Total de pagamentos: {HistoricoPagamento.objects.count()}")

if __name__ == '__main__':
    ativar_ultima_assinatura()
