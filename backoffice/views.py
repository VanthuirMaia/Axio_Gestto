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
    
    # 2. Business Metrics
    total_empresas = Empresa.objects.count()
    total_usuarios = Usuario.objects.count()
    total_profissionais = Profissional.objects.count()
    
    # Empresas ativas (com assinatura válida/ativa)
    # CORREÇÃO: Status no model é 'ativa', não 'active'
    assinaturas_ativas = Assinatura.objects.filter(status='ativa')
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
    # A. Risco de Churn (Empresas sem login há > 7 dias)
    data_limite_churn = timezone.now() - datetime.timedelta(days=7)
    # Buscando usuários master (donos) inativos
    risco_churn = Usuario.objects.filter(
        empresa__isnull=False, 
        last_login__lt=data_limite_churn,
        is_active=True
    ).select_related('empresa').order_by('last_login')[:10] # Top 10 riscos

    # B. Segmentação de Planos (Funil)
    status_counts = Assinatura.objects.values('status').annotate(total=Count('id'))
    funil = {s['status']: s['total'] for s in status_counts}
    
    # C. Top Payers (Clientes VIP)
    top_clientes = Assinatura.objects.filter(status='ativa').select_related('empresa', 'plano').order_by('-plano__preco_mensal', '-criado_em')[:5]

    # D. Distribuição de Planos
    planos_dist = Assinatura.objects.values('plano__nome').annotate(total=Count('id')).order_by('-total')

    # Novos cadastros (últimos 30 dias)
    data_30_dias = timezone.now() - datetime.timedelta(days=30)
    novas_empresas = Empresa.objects.filter(criada_em__gte=data_30_dias).count()

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
            'ticket_medio': float(ticket_medio)
        },
        'bi': {
            'risco_churn': risco_churn,
            'funil': funil,
            'top_clientes': top_clientes,
            'planos_dist': planos_dist
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
    # Exemplo: Contagem por tabela
    db_stats = [
        {'table': 'Empresas', 'count': Empresa.objects.count()},
        {'table': 'Usuarios', 'count': Usuario.objects.count()},
        {'table': 'Profissionais', 'count': Profissional.objects.count()},
        {'table': 'Assinaturas', 'count': Assinatura.objects.count()},
    ]
    
    return render(request, 'backoffice/infra.html', {'db_stats': db_stats, 'menu_active': 'infra'})
