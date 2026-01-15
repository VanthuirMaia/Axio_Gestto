"""
Script para atualizar os planos existentes com os novos valores e Price IDs da Stripe
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from assinaturas.models import Plano

# Dados dos novos planos
planos_data = [
    {
        'nome': 'basico',
        'descricao': 'Ideal para profissionais autônomos que querem sair do papel. Agenda digital completa, cadastro de clientes e controle financeiro básico. Perfeito para quem está começando a se organizar.',
        'preco_mensal': '19.99',
        'max_profissionais': 1,
        'max_agendamentos_mes': 999999,
        'max_usuarios': 1,
        'max_servicos': 3,
        'stripe_price_id': 'price_1SpsmFEOfuBf9VWtcZ5uuWek',
        'trial_dias': 7,
        'permite_financeiro': False,
        'permite_dashboard_clientes': False,
        'permite_recorrencias': False,
        'permite_lembrete_1_dia': False,
        'permite_lembrete_1_hora': False,
        'permite_whatsapp_bot': False,
        'ordem_exibicao': 1,
    },
    {
        'nome': 'essencial',
        'descricao': 'Ideal para profissionais autônomos (barbeiro ou manicure solo). Bot WhatsApp inteligente, agendamentos online ilimitados e lembretes automáticos. Tudo que você precisa para automatizar seus agendamentos!',
        'preco_mensal': '79.99',
        'max_profissionais': 1,
        'max_agendamentos_mes': 999999,
        'max_usuarios': 1,
        'max_servicos': 10,
        'stripe_price_id': 'price_1SpsnJEOfuBf9VWtCECFHdIe',
        'trial_dias': 7,
        'permite_financeiro': False,
        'permite_dashboard_clientes': False,
        'permite_recorrencias': False,
        'permite_lembrete_1_dia': True,
        'permite_lembrete_1_hora': False,
        'permite_whatsapp_bot': True,
        'ordem_exibicao': 2,
    },
    {
        'nome': 'profissional',
        'descricao': 'Gestão completa para barbearias e studios com equipe! Tudo do Essencial + Controle Financeiro Completo, Dashboard de Métricas, Relatórios Avançados, Comissões Automáticas e gestão de equipe com até 4 profissionais.',
        'preco_mensal': '199.99',
        'max_profissionais': 4,
        'max_agendamentos_mes': 999999,
        'max_usuarios': 4,
        'max_servicos': 50,
        'stripe_price_id': 'price_1SpsoUEOfuBf9VWtAE6wHiVM',
        'trial_dias': 14,
        'permite_financeiro': True,
        'permite_dashboard_clientes': True,
        'permite_recorrencias': True,
        'permite_lembrete_1_dia': True,
        'permite_lembrete_1_hora': True,
        'permite_whatsapp_bot': True,
        'permite_relatorios_avancados': True,
        'ordem_exibicao': 3,
    },
]

print("🔄 Atualizando planos...")

for plano_data in planos_data:
    nome = plano_data.pop('nome')
    
    plano, created = Plano.objects.update_or_create(
        nome=nome,
        defaults=plano_data
    )
    
    if created:
        print(f"✅ Plano '{plano.get_nome_display()}' criado com sucesso!")
    else:
        print(f"✅ Plano '{plano.get_nome_display()}' atualizado com sucesso!")
    
    print(f"   - Preço: R$ {plano.preco_mensal}/mês")
    print(f"   - Stripe Price ID: {plano.stripe_price_id}")
    print()

# Desativar plano "empresarial" se existir
try:
    plano_empresarial = Plano.objects.get(nome='empresarial')
    plano_empresarial.ativo = False
    plano_empresarial.save()
    print("⚠️  Plano 'Empresarial' desativado (substituído por planos personalizados)")
except Plano.DoesNotExist:
    pass

print("\n✅ Todos os planos foram atualizados com sucesso!")
print("\n📋 Planos ativos:")
for plano in Plano.objects.filter(ativo=True).order_by('ordem_exibicao'):
    print(f"   - {plano.get_nome_display()}: R$ {plano.preco_mensal}/mês (Stripe: {plano.stripe_price_id})")
