from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils.timezone import now
from django.db.models import Sum, Q, Count
from datetime import timedelta
from decimal import Decimal

from .models import LancamentoFinanceiro, CategoriaFinanceira, FormaPagamento, TipoLancamento, StatusLancamento
from agendamentos.models import Agendamento


@login_required
def financeiro_dashboard(request):
    """Dashboard financeiro com métricas e gráficos"""
    empresa = request.user.empresa
    agora = now()
    
    # Período selecionado (padrão: mês atual)
    mes_selecionado = request.GET.get('mes')
    ano_selecionado = request.GET.get('ano')
    
    if mes_selecionado and ano_selecionado:
        try:
            mes = int(mes_selecionado)
            ano = int(ano_selecionado)
            inicio_mes = agora.replace(year=ano, month=mes, day=1, hour=0, minute=0, second=0, microsecond=0)
        except (ValueError, TypeError):
            inicio_mes = agora.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    else:
        inicio_mes = agora.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    
    fim_mes = (inicio_mes + timedelta(days=32)).replace(day=1) - timedelta(seconds=1)
    
    # RECEITAS
    receitas_mes = LancamentoFinanceiro.objects.filter(
        empresa=empresa,
        tipo=TipoLancamento.RECEITA,
        data_vencimento__gte=inicio_mes,
        data_vencimento__lte=fim_mes
    ).aggregate(
        total=Sum('valor'),
        pagas=Sum('valor', filter=Q(status=StatusLancamento.PAGO)),
        pendentes=Sum('valor', filter=Q(status=StatusLancamento.PENDENTE))
    )
    
    # DESPESAS
    despesas_mes = LancamentoFinanceiro.objects.filter(
        empresa=empresa,
        tipo=TipoLancamento.DESPESA,
        data_vencimento__gte=inicio_mes,
        data_vencimento__lte=fim_mes
    ).aggregate(
        total=Sum('valor'),
        pagas=Sum('valor', filter=Q(status=StatusLancamento.PAGO)),
        pendentes=Sum('valor', filter=Q(status=StatusLancamento.PENDENTE))
    )
    
    # SALDO
    saldo_real = (receitas_mes['pagas'] or 0) - (despesas_mes['pagas'] or 0)
    saldo_previsto = (receitas_mes['total'] or 0) - (despesas_mes['total'] or 0)
    
    # CONTAS A RECEBER (próximos 30 dias a partir do período selecionado)
    proximos_30_dias = fim_mes + timedelta(days=30)
    contas_receber = LancamentoFinanceiro.objects.filter(
        empresa=empresa,
        tipo=TipoLancamento.RECEITA,
        status=StatusLancamento.PENDENTE,
        data_vencimento__range=(inicio_mes, proximos_30_dias)
    ).order_by('data_vencimento')[:5]
    
    # CONTAS A PAGAR (próximos 30 dias a partir do período selecionado)
    contas_pagar = LancamentoFinanceiro.objects.filter(
        empresa=empresa,
        tipo=TipoLancamento.DESPESA,
        status=StatusLancamento.PENDENTE,
        data_vencimento__range=(inicio_mes, proximos_30_dias)
    ).order_by('data_vencimento')[:5]
    
    # CONTAS VENCIDAS (no período selecionado)
    vencidas = LancamentoFinanceiro.objects.filter(
        empresa=empresa,
        status=StatusLancamento.PENDENTE,
        data_vencimento__lt=fim_mes,
        data_vencimento__gte=inicio_mes
    ).count()
    
    # RECEITAS POR CATEGORIA
    receitas_por_categoria = LancamentoFinanceiro.objects.filter(
        empresa=empresa,
        tipo=TipoLancamento.RECEITA,
        status=StatusLancamento.PAGO,
        data_vencimento__gte=inicio_mes,
        data_vencimento__lte=fim_mes
    ).values('categoria__nome', 'categoria__cor').annotate(
        total=Sum('valor')
    ).order_by('-total')
    
    # Anos disponíveis (do primeiro lançamento até próximo ano)
    primeiro_lancamento = LancamentoFinanceiro.objects.filter(
        empresa=empresa
    ).order_by('data_vencimento').first()
    
    if primeiro_lancamento:
        ano_inicial = primeiro_lancamento.data_vencimento.year
    else:
        ano_inicial = agora.year
    
    ano_final = agora.year + 1
    anos_disponiveis = list(range(ano_inicial, ano_final + 1))
    
    # Meses em português
    MESES_PT = [
        (1, 'Janeiro'), (2, 'Fevereiro'), (3, 'Março'), (4, 'Abril'),
        (5, 'Maio'), (6, 'Junho'), (7, 'Julho'), (8, 'Agosto'),
        (9, 'Setembro'), (10, 'Outubro'), (11, 'Novembro'), (12, 'Dezembro')
    ]
    
    mes_nome = dict(MESES_PT).get(inicio_mes.month, '')
    
    context = {
        'empresa': empresa,
        'mes_atual': f"{mes_nome}/{inicio_mes.year}",
        'mes_selecionado': inicio_mes.month,
        'ano_selecionado': inicio_mes.year,
        'meses_pt': MESES_PT,
        'anos_disponiveis': anos_disponiveis,
        
        # Receitas
        'receitas_total': receitas_mes['total'] or 0,
        'receitas_pagas': receitas_mes['pagas'] or 0,
        'receitas_pendentes': receitas_mes['pendentes'] or 0,
        
        # Despesas
        'despesas_total': despesas_mes['total'] or 0,
        'despesas_pagas': despesas_mes['pagas'] or 0,
        'despesas_pendentes': despesas_mes['pendentes'] or 0,
        
        # Saldo
        'saldo_real': saldo_real,
        'saldo_previsto': saldo_previsto,
        
        # Contas
        'contas_receber': contas_receber,
        'contas_pagar': contas_pagar,
        'contas_vencidas': vencidas,
        
        # Gráficos
        'receitas_por_categoria': receitas_por_categoria,
        
        # Data de hoje para comparações no template
        'hoje': agora.date(),
    }
    
    return render(request, 'financeiro/dashboard.html', context)


@login_required
def lancamentos_lista(request):
    """Lista todos os lançamentos financeiros"""
    empresa = request.user.empresa
    
    # Filtros
    tipo = request.GET.get('tipo', '')
    status = request.GET.get('status', '')
    categoria = request.GET.get('categoria', '')
    
    lancamentos = LancamentoFinanceiro.objects.filter(
        empresa=empresa
    ).select_related('categoria', 'forma_pagamento', 'agendamento__cliente')
    
    if tipo:
        lancamentos = lancamentos.filter(tipo=tipo)
    if status:
        lancamentos = lancamentos.filter(status=status)
    if categoria:
        lancamentos = lancamentos.filter(categoria_id=categoria)
    
    lancamentos = lancamentos.order_by('-data_vencimento')
    
    # Para os filtros
    categorias = CategoriaFinanceira.objects.filter(empresa=empresa, ativo=True)
    
    context = {
        'empresa': empresa,
        'lancamentos': lancamentos,
        'categorias': categorias,
        'filtro_tipo': tipo,
        'filtro_status': status,
        'filtro_categoria': categoria,
    }
    
    return render(request, 'financeiro/lancamentos_lista.html', context)


@login_required
def lancamento_criar(request):
    """Cria um novo lançamento financeiro"""
    empresa = request.user.empresa
    
    if request.method == 'POST':
        tipo = request.POST.get('tipo')
        categoria_id = request.POST.get('categoria')
        descricao = request.POST.get('descricao')
        valor = request.POST.get('valor')
        data_vencimento = request.POST.get('data_vencimento')
        status = request.POST.get('status', StatusLancamento.PENDENTE)
        data_pagamento = request.POST.get('data_pagamento') or None
        forma_pagamento_id = request.POST.get('forma_pagamento') or None
        observacoes = request.POST.get('observacoes', '')
        
        LancamentoFinanceiro.objects.create(
            empresa=empresa,
            tipo=tipo,
            categoria_id=categoria_id,
            descricao=descricao,
            valor=valor,
            data_vencimento=data_vencimento,
            data_pagamento=data_pagamento,
            status=status,
            forma_pagamento_id=forma_pagamento_id,
            observacoes=observacoes,
            criado_por=request.user
        )
        
        return redirect('lancamentos_lista')
    
    # GET
    categorias = CategoriaFinanceira.objects.filter(empresa=empresa, ativo=True)
    formas_pagamento = FormaPagamento.objects.filter(empresa=empresa, ativo=True)
    
    context = {
        'empresa': empresa,
        'categorias': categorias,
        'formas_pagamento': formas_pagamento,
    }
    
    return render(request, 'financeiro/lancamento_form.html', context)


@login_required
def lancamento_editar(request, pk):
    """Edita um lançamento existente"""
    empresa = request.user.empresa
    lancamento = get_object_or_404(LancamentoFinanceiro, pk=pk, empresa=empresa)
    
    if request.method == 'POST':
        lancamento.tipo = request.POST.get('tipo')
        lancamento.categoria_id = request.POST.get('categoria')
        lancamento.descricao = request.POST.get('descricao')
        lancamento.valor = request.POST.get('valor')
        lancamento.data_vencimento = request.POST.get('data_vencimento')
        lancamento.status = request.POST.get('status')
        lancamento.data_pagamento = request.POST.get('data_pagamento') or None
        lancamento.forma_pagamento_id = request.POST.get('forma_pagamento') or None
        lancamento.observacoes = request.POST.get('observacoes', '')
        lancamento.save()
        
        return redirect('lancamentos_lista')
    
    categorias = CategoriaFinanceira.objects.filter(empresa=empresa, ativo=True)
    formas_pagamento = FormaPagamento.objects.filter(empresa=empresa, ativo=True)
    
    context = {
        'empresa': empresa,
        'lancamento': lancamento,
        'categorias': categorias,
        'formas_pagamento': formas_pagamento,
        'editando': True,
    }
    
    return render(request, 'financeiro/lancamento_form.html', context)


@login_required
def lancamento_deletar(request, pk):
    """Deleta um lançamento"""
    empresa = request.user.empresa
    lancamento = get_object_or_404(LancamentoFinanceiro, pk=pk, empresa=empresa)
    
    if request.method == 'POST':
        lancamento.delete()
        return redirect('lancamentos_lista')
    
    return render(request, 'financeiro/lancamento_confirm_delete.html', {'lancamento': lancamento})


@login_required
def marcar_como_pago(request, pk):
    """Marca um lançamento como pago"""
    empresa = request.user.empresa
    lancamento = get_object_or_404(LancamentoFinanceiro, pk=pk, empresa=empresa)
    
    if request.method == 'POST':
        forma_pagamento_id = request.POST.get('forma_pagamento')
        data_pagamento = request.POST.get('data_pagamento', now().date())
        
        # Busca a forma de pagamento se foi informada
        forma_pagamento = None
        if forma_pagamento_id:
            forma_pagamento = FormaPagamento.objects.get(id=forma_pagamento_id)
        
        # Marca como pago
        lancamento.marcar_como_pago(
            data_pagamento=data_pagamento,
            forma_pagamento=forma_pagamento  # ← Passa o objeto, não o ID
        )
    
    return redirect(request.META.get('HTTP_REFERER', 'financeiro_dashboard'))
    """Marca um lançamento como pago"""
    empresa = request.user.empresa
    lancamento = get_object_or_404(LancamentoFinanceiro, pk=pk, empresa=empresa)
    
    if request.method == 'POST':
        forma_pagamento_id = request.POST.get('forma_pagamento')
        data_pagamento = request.POST.get('data_pagamento', now().date())
        
        lancamento.marcar_como_pago(
            data_pagamento=data_pagamento,
            forma_pagamento_id=forma_pagamento_id
        )
    
    return redirect(request.META.get('HTTP_REFERER', 'financeiro_dashboard'))