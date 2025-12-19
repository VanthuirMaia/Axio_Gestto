from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from django.utils.timezone import now
from django.db.models import Count, Avg, Q, Max, Sum
from datetime import timedelta
from django.utils.timezone import now, localtime
from .models import Usuario
from empresas.models import Empresa
from agendamentos.models import Agendamento
from clientes.models import Cliente
from financeiro.models import LancamentoFinanceiro


@require_http_methods(["GET", "POST"])
def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        email_ou_usuario = request.POST.get('email_ou_usuario')
        senha = request.POST.get('senha')
        
        try:
            usuario = Usuario.objects.get(email=email_ou_usuario)
            user = authenticate(request, username=usuario.username, password=senha)
        except Usuario.DoesNotExist:
            user = authenticate(request, username=email_ou_usuario, password=senha)
        
        if user is not None and user.ativo:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, 'Email/Usuario ou senha incorretos.')
    
    return render(request, 'login.html')


@login_required
def logout_view(request):
    logout(request)
    messages.success(request, 'Você foi desconectado com sucesso.')
    return redirect('login')


@login_required
def dashboard_view(request):
    """Dashboard principal - Command Center do negócio"""
    empresa = request.user.empresa
    if not empresa:
        messages.error(request, 'Usuário não associado a nenhuma empresa.')
        return redirect('logout')
    
    agora = now()
    hoje = agora.date()
    inicio_mes = hoje.replace(day=1)
    inicio_semana = hoje - timedelta(days=hoje.weekday())
    limite_ativos = agora - timedelta(days=30)

    # ============================================
    # SAUDAÇÃO PERSONALIZADA
    # ============================================
    agora_local = localtime(now())  # ← Força timezone local
    hora = agora_local.hour

    if hora < 12:
        saudacao = "Bom dia"
    elif hora < 18:
        saudacao = "Boa tarde"
    else:
        saudacao = "Boa noite"

    # ============================================
    # AGENDAMENTOS (MANTIDO + MELHORADO)
    # ============================================
    
    # Agendamentos hoje
    agendamentos_hoje = Agendamento.objects.filter(
        empresa=empresa,
        data_hora_inicio__date=hoje
    ).exclude(
        status__in=["cancelado", "nao_compareceu"]
    ).count()

    # Próximos agendamentos
    proximos_agendamentos = Agendamento.objects.filter(
        empresa=empresa,
        data_hora_inicio__gte=agora
    ).exclude(
        status__in=["cancelado", "nao_compareceu"]
    ).select_related('cliente', 'servico', 'profissional').order_by('data_hora_inicio')[:5]
    
    # Agendamentos da semana (NOVO)
    agendamentos_semana = Agendamento.objects.filter(
        empresa=empresa,
        data_hora_inicio__gte=inicio_semana,
        data_hora_inicio__lt=inicio_semana + timedelta(days=7)
    ).exclude(status='cancelado').count()
    
    # Agendamentos pendentes de confirmação (NOVO)
    agendamentos_pendentes = Agendamento.objects.filter(
        empresa=empresa,
        status='pendente',
        data_hora_inicio__gte=agora
    ).count()

    # ============================================
    # CLIENTES (MANTIDO + MELHORADO)
    # ============================================
    
    clientes_metricas = Cliente.objects.filter(
        empresa=empresa,
        ativo=True
    ).annotate(
        total_visitas=Count(
            'agendamentos',
            filter=Q(agendamentos__status="concluido")
        ),
        ultima_visita=Max(
            'agendamentos__data_hora_inicio',
            filter=Q(agendamentos__status="concluido")
        ),
        total_gasto=Sum(
            'agendamentos__valor_cobrado',
            filter=Q(agendamentos__status="concluido")
        )
    )

    clientes_ativos = clientes_metricas.filter(
        ultima_visita__gte=limite_ativos
    ).count()

    clientes_inativos = clientes_metricas.exclude(
        ultima_visita__gte=limite_ativos
    ).count()

    ticket_medio = Agendamento.objects.filter(
        empresa=empresa,
        status="concluido"
    ).aggregate(
        media=Avg('valor_cobrado')
    )['media'] or 0
    
    # Total de clientes (NOVO)
    total_clientes = Cliente.objects.filter(empresa=empresa, ativo=True).count()
    
    # Novos clientes este mês (NOVO)
    novos_clientes_mes = Cliente.objects.filter(
        empresa=empresa,
        criado_em__gte=inicio_mes
    ).count()
    
    # Top 5 Clientes VIP (NOVO)
    top_clientes = clientes_metricas.filter(
        total_gasto__isnull=False
    ).order_by('-total_gasto')[:5]
    
    # Clientes em risco (NOVO)
    clientes_risco = clientes_metricas.filter(
        ultima_visita__lt=hoje - timedelta(days=30)
    ).count()

    # ============================================
    # FINANCEIRO (NOVO)
    # ============================================
    
    # Faturamento do mês
    faturamento_mes = LancamentoFinanceiro.objects.filter(
        empresa=empresa,
        tipo='receita',
        status='pago',
        data_pagamento__gte=inicio_mes,
        data_pagamento__lte=hoje
    ).aggregate(total=Sum('valor'))['total'] or 0
    
    # Receitas pendentes do mês
    receitas_pendentes = LancamentoFinanceiro.objects.filter(
        empresa=empresa,
        tipo='receita',
        status='pendente',
        data_vencimento__month=hoje.month,
        data_vencimento__year=hoje.year
    ).aggregate(total=Sum('valor'))['total'] or 0
    
    # Despesas do mês
    despesas_mes = LancamentoFinanceiro.objects.filter(
        empresa=empresa,
        tipo='despesa',
        status='pago',
        data_pagamento__gte=inicio_mes,
        data_pagamento__lte=hoje
    ).aggregate(total=Sum('valor'))['total'] or 0
    
    # Saldo do mês
    saldo_mes = faturamento_mes - despesas_mes
    
    # Contas vencidas
    contas_vencidas = LancamentoFinanceiro.objects.filter(
        empresa=empresa,
        status='pendente',
        data_vencimento__lt=hoje
    ).count()
    
    # ============================================
    # GRÁFICO: Faturamento últimos 7 dias (NOVO)
    # ============================================
    
    dias_labels = []
    dias_valores = []
    
    for i in range(6, -1, -1):
        dia = hoje - timedelta(days=i)
        
        faturamento_dia = LancamentoFinanceiro.objects.filter(
            empresa=empresa,
            tipo='receita',
            status='pago',
            data_pagamento=dia
        ).aggregate(total=Sum('valor'))['total'] or 0
        
        # Dia da semana em português
        dias_semana = ['Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sáb', 'Dom']
        dia_nome = dias_semana[dia.weekday()]
        
        dias_labels.append(f"{dia_nome} {dia.day}")
        dias_valores.append(float(faturamento_dia))

    # ============================================
    # CONTEXTO
    # ============================================
    
    context = {
        'empresa': empresa,
        'usuario': request.user,
        'saudacao': saudacao,
        'hoje': hoje,
        'agora': agora,
        
        # Agendamentos
        'agendamentos_hoje': agendamentos_hoje,
        'agendamentos_semana': agendamentos_semana,
        'agendamentos_pendentes': agendamentos_pendentes,
        'proximos_agendamentos': proximos_agendamentos,
        
        # Clientes
        'total_clientes': total_clientes,
        'clientes_ativos': clientes_ativos,
        'clientes_inativos': clientes_inativos,
        'novos_clientes_mes': novos_clientes_mes,
        'ticket_medio': ticket_medio,
        'top_clientes': top_clientes,
        'clientes_risco': clientes_risco,
        
        # Financeiro
        'faturamento_mes': faturamento_mes,
        'receitas_pendentes': receitas_pendentes,
        'despesas_mes': despesas_mes,
        'saldo_mes': saldo_mes,
        'contas_vencidas': contas_vencidas,
        
        # Gráfico
        'dias_labels': dias_labels,
        'dias_valores': dias_valores,
    }
    
    return render(request, 'dashboard.html', context)