from django.shortcuts import render, redirect
from django.contrib.auth.decorators import user_passes_test
from django.conf import settings
from django.contrib import messages
from django.db.models import Count
from django.utils import timezone
import psutil
import os
import datetime

# Models para monitoramento
from empresas.models import Empresa, Profissional
from core.models import Usuario
from assinaturas.models import Assinatura

# Função de verificação (apenas superuser)
def is_superuser(user):
    return user.is_authenticated and user.is_superuser

from django.db.models import Count, Sum

# ...
@user_passes_test(is_superuser, login_url='/login/')
def dashboard_view(request):
    """
    Dashboard principal com métricas de infra e negócio.
    """
    # 1. Hardware Metrics (Mantido)
    infra = {
        'cpu_percent': psutil.cpu_percent(interval=None),
        'ram_percent': psutil.virtual_memory().percent,
        'disk_percent': psutil.disk_usage('/').percent,
    }
    
    # 2. Business Metrics (exclui empresas demo)
    total_empresas = Empresa.objects.filter(is_demo=False).count()
    total_usuarios = Usuario.objects.filter(empresa__is_demo=False).count()
    total_profissionais = Profissional.objects.filter(empresa__is_demo=False).count()

    # Empresas ativas (com assinatura válida/ativa) - exclui demo
    # CORREÇÃO: Status no model é 'ativa', não 'active'
    assinaturas_ativas = Assinatura.objects.filter(status='ativa', empresa__is_demo=False)
    count_ativas = assinaturas_ativas.count()
    
    # 3. Financial Metrics (KPIs)
    # MRR = Soma dos valores mensais dos planos ativos
    # O modelo Plano deve ter um campo 'valor' (Decimal/Float)
    mrr_data = assinaturas_ativas.aggregate(total_mrr=Sum('plano__preco_mensal'))
    mrr = mrr_data['total_mrr'] or 0
    
    # ARR = MRR * 12
    arr = mrr * 12
    
    # Ticket Médio (ARPU)
    ticket_medio = mrr / count_ativas if count_ativas > 0 else 0

    # 4. BI Insights (v3)
    # A. Risco de Churn (Empresas sem login há > 7 dias) - exclui demo
    data_limite_churn = timezone.now() - datetime.timedelta(days=7)
    # Buscando usuários master (donos) inativos
    risco_churn = Usuario.objects.filter(
        empresa__isnull=False,
        empresa__is_demo=False,
        last_login__lt=data_limite_churn,
        is_active=True
    ).select_related('empresa').order_by('last_login')[:10] # Top 10 riscos

    # B. Segmentação de Planos (Funil) - exclui demo
    status_counts = Assinatura.objects.filter(empresa__is_demo=False).values('status').annotate(total=Count('id'))
    funil = {s['status']: s['total'] for s in status_counts}
    
    # C. Top Payers (Clientes VIP) - exclui demo
    top_clientes = Assinatura.objects.filter(status='ativa', empresa__is_demo=False).select_related('empresa', 'plano').order_by('-plano__preco_mensal', '-criado_em')[:5]

    # D. Distribuição de Planos - exclui demo
    planos_dist = Assinatura.objects.filter(empresa__is_demo=False).values('plano__nome').annotate(total=Count('id')).order_by('-total')

    # Novos cadastros (últimos 30 dias) - exclui demo
    data_30_dias = timezone.now() - datetime.timedelta(days=30)
    novas_empresas = Empresa.objects.filter(criada_em__gte=data_30_dias, is_demo=False).count()
    
    # ============================================
    # 5. ANALYTICS AVANÇADO (NOVO)
    # ============================================
    
    # A. Evolução MRR (últimos 30 dias) - exclui demo
    mrr_historico = []
    hoje = timezone.now().date()
    for i in range(29, -1, -1):  # 30 dias (de 29 dias atrás até hoje)
        data = hoje - datetime.timedelta(days=i)
        mrr_dia = Assinatura.objects.filter(
            status='ativa',
            data_inicio__lte=data,
            empresa__is_demo=False
        ).aggregate(total=Sum('plano__preco_mensal'))['total'] or 0
        mrr_historico.append({
            'data': data.strftime('%d/%m'),
            'mrr': float(mrr_dia)
        })
    
    # B. Taxa de Conversão Trial → Pago (últimos 30 dias) - exclui demo
    trials_iniciados = Assinatura.objects.filter(
        status='trial',
        data_inicio__gte=data_30_dias,
        empresa__is_demo=False
    ).count()

    # Convertidos = assinaturas que eram trial e viraram ativas
    # (simplificação: contar ativas criadas nos últimos 30 dias) - exclui demo
    convertidos = Assinatura.objects.filter(
        status='ativa',
        data_inicio__gte=data_30_dias,
        empresa__is_demo=False
    ).count()
    
    taxa_conversao = (convertidos / trials_iniciados * 100) if trials_iniciados > 0 else 0
    
    # C. Churn Rate (últimos 30 dias) - exclui demo
    inicio_mes = (timezone.now() - datetime.timedelta(days=30)).replace(day=1)
    fim_mes = timezone.now()

    assinaturas_inicio_periodo = Assinatura.objects.filter(
        status='ativa',
        data_inicio__lte=inicio_mes,
        empresa__is_demo=False
    ).count()

    canceladas_periodo = Assinatura.objects.filter(
        status='cancelada',
        data_cancelamento__gte=inicio_mes,
        data_cancelamento__lte=fim_mes,
        empresa__is_demo=False
    ).count() if hasattr(Assinatura, 'data_cancelamento') else 0
    
    churn_rate = (canceladas_periodo / assinaturas_inicio_periodo * 100) if assinaturas_inicio_periodo > 0 else 0
    
    # Assinaturas em risco (expandido - sem login há 7 dias) - exclui demo
    # Contar assinaturas ativas cujas empresas têm usuários inativos
    empresas_com_usuarios_inativos = Usuario.objects.filter(
        last_login__lt=data_limite_churn,
        is_active=True,
        empresa__isnull=False,
        empresa__is_demo=False
    ).values_list('empresa_id', flat=True).distinct()

    assinaturas_risco = Assinatura.objects.filter(
        status='ativa',
        empresa_id__in=empresas_com_usuarios_inativos,
        empresa__is_demo=False
    ).count()
    
    # D. Comparação com Período Anterior (MRR mês anterior) - exclui demo
    inicio_mes_anterior = inicio_mes - datetime.timedelta(days=30)
    mrr_mes_anterior = Assinatura.objects.filter(
        status='ativa',
        data_inicio__lte=inicio_mes_anterior,
        empresa__is_demo=False
    ).aggregate(total=Sum('plano__preco_mensal'))['total'] or 0
    
    crescimento_mrr = ((mrr - mrr_mes_anterior) / mrr_mes_anterior * 100) if mrr_mes_anterior > 0 else 0
    
    # E. Top 5 Clientes com % de Receita
    receita_total = mrr
    top_clientes_expandido = []
    for assinatura in top_clientes:
        percentual = (assinatura.plano.preco_mensal / receita_total * 100) if receita_total > 0 else 0
        top_clientes_expandido.append({
            'empresa': assinatura.empresa,
            'plano': assinatura.plano,
            'valor': assinatura.plano.preco_mensal,
            'percentual': round(percentual, 1)
        })

    # Configurar contexto de retorno
    context = {
        'infra': infra,
        'metrics': {
            'empresas_total': total_empresas,
            'empresas_ativas': count_ativas,
            'usuarios': total_usuarios,
            'profissionais': total_profissionais,
            'novas_empresas_30d': novas_empresas, # Corrigido: usando a variável calculada anteriormente
        },
        'financial': {
            'mrr': float(mrr),
            'arr': float(arr),
            'ticket_medio': float(ticket_medio),
            'crescimento_mrr': round(crescimento_mrr, 1),  # NOVO
            'mrr_mes_anterior': float(mrr_mes_anterior)  # NOVO
        },
        'bi': {
            'risco_churn': risco_churn,
            'funil': funil,
            'top_clientes': top_clientes_expandido,  # ATUALIZADO
            'planos_dist': planos_dist,
            # NOVOS
            'taxa_conversao': round(taxa_conversao, 1),
            'churn_rate': round(churn_rate, 1),
            'assinaturas_risco': assinaturas_risco,
            'trials_iniciados': trials_iniciados,
            'convertidos': convertidos
        },
        'analytics': {  # NOVO
            'mrr_historico': mrr_historico
        },
        'menu_active': 'dashboard'
    }
    return render(request, 'backoffice/dashboard.html', context)

@user_passes_test(is_superuser, login_url='/login/')
def logs_view(request):
    """
    Leitor de logs do sistema (app.log).
    """
    # Log Path (ajuste conforme seu settings de LOGGING)
    log_dir = os.path.join(settings.BASE_DIR, 'data', 'logs')
    log_file_path = os.path.join(log_dir, 'app.log')
    logs = []
    
    # Criar diretório se não existir
    os.makedirs(log_dir, exist_ok=True)
    
    if os.path.exists(log_file_path):
        try:
            # Ler últimas 200 linhas
            with open(log_file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                # Reverter para mostrar mais recentes primeiro
                for line in reversed(lines[-200:]):
                    # Tentar parsear ou apenas passar raw
                    nivel = 'INFO'
                    if 'ERROR' in line: nivel = 'ERROR'
                    elif 'WARNING' in line: nivel = 'WARNING'
                    elif 'CRITICAL' in line: nivel = 'CRITICAL'
                    
                    logs.append({
                        'raw': line,
                        'nivel': nivel
                    })
        except Exception as e:
            messages.error(request, f"Erro ao ler arquivo de log: {e}")
    else:
        messages.warning(request, f"Arquivo de log não encontrado: {log_file_path}. Configure LOGGING no settings ou aguarde a geração de logs.")

    return render(request, 'backoffice/logs.html', {'logs': logs, 'menu_active': 'logs'})

@user_passes_test(is_superuser, login_url='/login/')
def infra_view(request):
    """
    Detalhes de infraestrutura e database stats.
    """
    # Exemplo: Contagem por tabela (exclui empresas demo)
    db_stats = [
        {'table': 'Empresas', 'count': Empresa.objects.filter(is_demo=False).count()},
        {'table': 'Usuarios', 'count': Usuario.objects.filter(empresa__is_demo=False).count()},
        {'table': 'Profissionais', 'count': Profissional.objects.filter(empresa__is_demo=False).count()},
        {'table': 'Assinaturas', 'count': Assinatura.objects.filter(empresa__is_demo=False).count()},
    ]
    
    return render(request, 'backoffice/infra.html', {'db_stats': db_stats, 'menu_active': 'infra'})
