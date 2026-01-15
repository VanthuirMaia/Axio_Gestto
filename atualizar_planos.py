#!/usr/bin/env python
"""
Script para atualizar os planos de assinatura no banco de dados
"""
import os
import sys
import django

# Configurar Django
sys.path.append(os.path.dirname(__file__))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from assinaturas.models import Plano
from decimal import Decimal


def atualizar_planos():
    """
    Atualiza ou cria os planos com os valores corretos
    """
    print("[*] Atualizando planos de assinatura...")
    print("-" * 50)

    # Plano Básico
    basico, created = Plano.objects.update_or_create(
        nome='basico',
        defaults={
            'descricao': 'Ideal para começar! Gerencie sua agenda e clientes de forma simples e organizada.',
            'preco_mensal': Decimal('19.99'),
            'max_profissionais': 1,
            'max_agendamentos_mes': 999999,
            'max_usuarios': 1,
            'max_servicos': 3,
            'trial_dias': 7,
            'permite_financeiro': True,  # Financeiro básico
            'permite_dashboard_clientes': False,
            'permite_recorrencias': False,
            'permite_relatorios_avancados': False,
            'permite_integracao_contabil': False,
            'permite_multi_unidades': False,
            'permite_lembrete_1_dia': False,
            'permite_lembrete_1_hora': False,
            'permite_whatsapp_bot': False,  # SEM WhatsApp
            'ativo': True,
            'ordem_exibicao': 1
        }
    )
    print(f"[OK] Plano Básico: {'criado' if created else 'atualizado'} - R$ 19,99/mes")

    # Plano Essencial
    essencial, created = Plano.objects.update_or_create(
        nome='essencial',
        defaults={
            'descricao': 'Ideal para profissionais autônomos. Bot WhatsApp inteligente, agendamentos online ilimitados e página de agendamento personalizada. Tudo que você precisa para começar!',
            'preco_mensal': Decimal('79.99'),
            'max_profissionais': 1,
            'max_agendamentos_mes': 999999,
            'max_usuarios': 1,
            'max_servicos': 3,
            'trial_dias': 7,
            'permite_financeiro': False,
            'permite_dashboard_clientes': False,
            'permite_recorrencias': False,
            'permite_relatorios_avancados': False,
            'permite_integracao_contabil': False,
            'permite_multi_unidades': False,
            'permite_lembrete_1_dia': True,
            'permite_lembrete_1_hora': False,
            'permite_whatsapp_bot': True,
            'ativo': True,
            'ordem_exibicao': 2
        }
    )
    print(f"[OK] Plano Essencial: {'criado' if created else 'atualizado'} - R$ 79,99/mes")

    # Plano Profissional
    profissional, created = Plano.objects.update_or_create(
        nome='profissional',
        defaults={
            'descricao': 'Gestao completa do seu negocio! Tudo do Essencial + Controle Financeiro, Dashboard de Metricas, Agendamentos Recorrentes e gestao de equipe com ate 4 profissionais.',
            'preco_mensal': Decimal('199.99'),
            'max_profissionais': 4,
            'max_agendamentos_mes': 999999,
            'max_usuarios': 4,
            'max_servicos': 20,
            'trial_dias': 14,
            'permite_financeiro': True,
            'permite_dashboard_clientes': True,
            'permite_recorrencias': True,
            'permite_relatorios_avancados': True,
            'permite_integracao_contabil': False,
            'permite_multi_unidades': False,
            'permite_lembrete_1_dia': True,
            'permite_lembrete_1_hora': True,
            'permite_whatsapp_bot': True,
            'ativo': True,
            'ordem_exibicao': 3
        }
    )
    print(f"[OK] Plano Profissional: {'criado' if created else 'atualizado'} - R$ 199,99/mes")

    # Plano Empresarial
    empresarial, created = Plano.objects.update_or_create(
        nome='empresarial',
        defaults={
            'descricao': 'Plano personalizado para empresas com mais de 4 profissionais. Recursos ilimitados e suporte dedicado.',
            'preco_mensal': Decimal('1000.00'),
            'max_profissionais': 999,
            'max_agendamentos_mes': 999999,
            'max_usuarios': 999,
            'max_servicos': 999,
            'trial_dias': 7,
            'permite_financeiro': True,
            'permite_dashboard_clientes': True,
            'permite_recorrencias': True,
            'permite_relatorios_avancados': True,
            'permite_integracao_contabil': True,
            'permite_multi_unidades': True,
            'ativo': True,
            'ordem_exibicao': 3
        }
    )
    print(f"[OK] Plano Empresarial: {'criado' if created else 'atualizado'} - R$ 1.000,00/mes")

    print("-" * 50)
    print("[SUCCESS] Planos atualizados com sucesso!")
    print("\nResumo dos planos:")
    print("   - Básico: R$ 19,99/mes (1 profissional, sem WhatsApp)")
    print("   - Essencial: R$ 79,99/mes (1 profissional, com WhatsApp)")
    print("   - Profissional: R$ 199,99/mes (ate 4 profissionais)")
    print("   - Empresarial: R$ 1.000,00/mes (recursos ilimitados)")


if __name__ == '__main__':
    try:
        atualizar_planos()
    except Exception as e:
        print(f"[ERRO] Erro ao atualizar planos: {e}")
        sys.exit(1)
