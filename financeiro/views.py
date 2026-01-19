from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils.timezone import now
from django.db.models import Sum, Q, Count
from datetime import timedelta
from decimal import Decimal

from .models import LancamentoFinanceiro, CategoriaFinanceira, FormaPagamento, TipoLancamento, StatusLancamento
from agendamentos.models import Agendamento
from core.decorators import plano_required


def calcular_periodo(tipo_periodo, mes=None, ano=None, trimestre=None, semestre=None):
    """
    Calcula início e fim de um período baseado no tipo
    
    Args:
        tipo_periodo: 'mes', 'trimestre', 'semestre', 'ano'
        mes: Mês (1-12) para tipo 'mes'
        ano: Ano (ex: 2026)
        trimestre: Trimestre (1-4) para tipo 'trimestre'
        semestre: Semestre (1-2) para tipo 'semestre'
    
    Returns:
        tuple: (inicio, fim, nome_periodo)
    """
    from datetime import datetime
    
    agora = now()
    
    if tipo_periodo == 'trimestre':
        # Trimestres: Q1 (Jan-Mar), Q2 (Abr-Jun), Q3 (Jul-Set), Q4 (Out-Dez)
        trimestre = int(trimestre) if trimestre else ((agora.month - 1) // 3) + 1
        ano = int(ano) if ano else agora.year
        
        mes_inicio = (trimestre - 1) * 3 + 1
        mes_fim = trimestre * 3
        
        inicio = datetime(ano, mes_inicio, 1, 0, 0, 0)
        fim = datetime(ano, mes_fim, 1, 0, 0, 0)
        fim = (fim + timedelta(days=32)).replace(day=1) - timedelta(seconds=1)
        
        nome = f"Q{trimestre}/{ano}"
        
    elif tipo_periodo == 'semestre':
        # Semestres: 1º (Jan-Jun), 2º (Jul-Dez)
        semestre = int(semestre) if semestre else (1 if agora.month <= 6 else 2)
        ano = int(ano) if ano else agora.year
        
        mes_inicio = 1 if semestre == 1 else 7
        mes_fim = 6 if semestre == 1 else 12
        
        inicio = datetime(ano, mes_inicio, 1, 0, 0, 0)
        fim = datetime(ano, mes_fim, 1, 0, 0, 0)
        fim = (fim + timedelta(days=32)).replace(day=1) - timedelta(seconds=1)
        
        nome = f"{semestre}º Semestre/{ano}"
        
    elif tipo_periodo == 'ano':
        ano = int(ano) if ano else agora.year
        
        inicio = datetime(ano, 1, 1, 0, 0, 0)
        fim = datetime(ano, 12, 31, 23, 59, 59)
        
        nome = str(ano)
        
    else:  # 'mes' (padrão)
        mes = int(mes) if mes else agora.month
        ano = int(ano) if ano else agora.year
        
        inicio = datetime(ano, mes, 1, 0, 0, 0)
        fim = (inicio + timedelta(days=32)).replace(day=1) - timedelta(seconds=1)
        
        MESES_PT = {
            1: 'Janeiro', 2: 'Fevereiro', 3: 'Março', 4: 'Abril',
            5: 'Maio', 6: 'Junho', 7: 'Julho', 8: 'Agosto',
            9: 'Setembro', 10: 'Outubro', 11: 'Novembro', 12: 'Dezembro'
        }
        nome = f"{MESES_PT[mes]}/{ano}"
    
    # Converte para timezone-aware
    from django.utils.timezone import make_aware
    inicio = make_aware(inicio)
    fim = make_aware(fim)
    
    return inicio, fim, nome


def calcular_periodo_anterior(tipo_periodo, inicio_atual, trimestre=None, semestre=None):
    """
    Calcula o período anterior baseado no tipo
    
    Returns:
        tuple: (inicio_anterior, fim_anterior)
    """
    from datetime import datetime
    from dateutil.relativedelta import relativedelta
    
    if tipo_periodo == 'trimestre':
        # 3 meses atrás
        inicio_anterior = inicio_atual - relativedelta(months=3)
        fim_anterior = inicio_atual - timedelta(seconds=1)
        
    elif tipo_periodo == 'semestre':
        # 6 meses atrás
        inicio_anterior = inicio_atual - relativedelta(months=6)
        fim_anterior = inicio_atual - timedelta(seconds=1)
        
    elif tipo_periodo == 'ano':
        # 1 ano atrás
        inicio_anterior = inicio_atual - relativedelta(years=1)
        fim_anterior = inicio_atual - timedelta(seconds=1)
        
    else:  # 'mes'
        # 1 mês atrás
        inicio_anterior = inicio_atual - relativedelta(months=1)
        fim_anterior = inicio_atual - timedelta(seconds=1)
    
    return inicio_anterior, fim_anterior


def calcular_evolucao_mensal(empresa, inicio, fim):
    """
    Calcula evolução mês a mês de receitas e despesas no período
    
    Returns:
        list: [{'mes': 'Jan/26', 'receitas': 1000, 'despesas': 500}, ...]
    """
    from datetime import datetime
    from dateutil.relativedelta import relativedelta
    
    evolucao = []
    mes_atual = inicio.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    
    MESES_CURTOS = {
        1: 'Jan', 2: 'Fev', 3: 'Mar', 4: 'Abr',
        5: 'Mai', 6: 'Jun', 7: 'Jul', 8: 'Ago',
        9: 'Set', 10: 'Out', 11: 'Nov', 12: 'Dez'
    }
    
    while mes_atual <= fim:
        fim_mes = (mes_atual + timedelta(days=32)).replace(day=1) - timedelta(seconds=1)
        
        # Receitas do mês
        receitas = LancamentoFinanceiro.objects.filter(
            empresa=empresa,
            tipo=TipoLancamento.RECEITA,
            status=StatusLancamento.PAGO,
            data_vencimento__gte=mes_atual,
            data_vencimento__lte=fim_mes
        ).aggregate(total=Sum('valor'))['total'] or 0
        
        # Despesas do mês
        despesas = LancamentoFinanceiro.objects.filter(
            empresa=empresa,
            tipo=TipoLancamento.DESPESA,
            status=StatusLancamento.PAGO,
            data_vencimento__gte=mes_atual,
            data_vencimento__lte=fim_mes
        ).aggregate(total=Sum('valor'))['total'] or 0
        
        mes_nome = f"{MESES_CURTOS[mes_atual.month]}/{str(mes_atual.year)[2:]}"
        
        evolucao.append({
            'mes': mes_nome,
            'receitas': float(receitas),
            'despesas': float(despesas)
        })
        
        mes_atual = mes_atual + relativedelta(months=1)
    
    return evolucao


@login_required
@plano_required(feature_flag='permite_financeiro', feature_name='Controle Financeiro')
def financeiro_dashboard(request):
    """Dashboard financeiro com métricas e gráficos"""
    empresa = request.user.empresa
    agora = now()
    
    # Parâmetros do período
    tipo_periodo = request.GET.get('tipo_periodo', 'mes')
    mes_selecionado = request.GET.get('mes')
    ano_selecionado = request.GET.get('ano')
    trimestre_selecionado = request.GET.get('trimestre')
    semestre_selecionado = request.GET.get('semestre')
    
    # Calcula o período atual
    inicio_periodo, fim_periodo, nome_periodo = calcular_periodo(
        tipo_periodo=tipo_periodo,
        mes=mes_selecionado,
        ano=ano_selecionado,
        trimestre=trimestre_selecionado,
        semestre=semestre_selecionado
    )
    
    # Calcula período anterior para comparativo
    inicio_anterior, fim_anterior = calcular_periodo_anterior(
        tipo_periodo, inicio_periodo, trimestre_selecionado, semestre_selecionado
    )
    
    # RECEITAS DO PERÍODO
    receitas_periodo = LancamentoFinanceiro.objects.filter(
        empresa=empresa,
        tipo=TipoLancamento.RECEITA,
        data_vencimento__gte=inicio_periodo,
        data_vencimento__lte=fim_periodo
    ).aggregate(
        total=Sum('valor'),
        pagas=Sum('valor', filter=Q(status=StatusLancamento.PAGO)),
        pendentes=Sum('valor', filter=Q(status=StatusLancamento.PENDENTE))
    )
    
    # DESPESAS DO PERÍODO
    despesas_periodo = LancamentoFinanceiro.objects.filter(
        empresa=empresa,
        tipo=TipoLancamento.DESPESA,
        data_vencimento__gte=inicio_periodo,
        data_vencimento__lte=fim_periodo
    ).aggregate(
        total=Sum('valor'),
        pagas=Sum('valor', filter=Q(status=StatusLancamento.PAGO)),
        pendentes=Sum('valor', filter=Q(status=StatusLancamento.PENDENTE))
    )
    
    # RECEITAS DO PERÍODO ANTERIOR (para comparativo)
    receitas_anterior = LancamentoFinanceiro.objects.filter(
        empresa=empresa,
        tipo=TipoLancamento.RECEITA,
        status=StatusLancamento.PAGO,
        data_vencimento__gte=inicio_anterior,
        data_vencimento__lte=fim_anterior
    ).aggregate(total=Sum('valor'))['total'] or 0
    
    # SALDO
    saldo_real = (receitas_periodo['pagas'] or 0) - (despesas_periodo['pagas'] or 0)
    saldo_previsto = (receitas_periodo['total'] or 0) - (despesas_periodo['total'] or 0)
    
    # COMPARATIVO (% de variação vs período anterior)
    receitas_pagas_atual = receitas_periodo['pagas'] or 0
    if receitas_anterior > 0:
        comparativo_percentual = ((receitas_pagas_atual - receitas_anterior) / receitas_anterior) * 100
    else:
        comparativo_percentual = 100 if receitas_pagas_atual > 0 else 0
    
    # EVOLUÇÃO MENSAL (para gráfico)
    evolucao_mensal = calcular_evolucao_mensal(empresa, inicio_periodo, fim_periodo)
    
    # MÉDIAS (apenas para períodos maiores que 1 mês)
    num_meses = len(evolucao_mensal)
    if num_meses > 1:
        receita_media_mensal = receitas_pagas_atual / num_meses if num_meses > 0 else 0
        despesa_media_mensal = (despesas_periodo['pagas'] or 0) / num_meses if num_meses > 0 else 0
    else:
        receita_media_mensal = None
        despesa_media_mensal = None
    
    # CONTAS A RECEBER (próximos 30 dias)
    proximos_30_dias = fim_periodo + timedelta(days=30)
    contas_receber = LancamentoFinanceiro.objects.filter(
        empresa=empresa,
        tipo=TipoLancamento.RECEITA,
        status=StatusLancamento.PENDENTE,
        data_vencimento__range=(inicio_periodo, proximos_30_dias)
    ).order_by('data_vencimento')[:5]
    
    # CONTAS A PAGAR (próximos 30 dias)
    contas_pagar = LancamentoFinanceiro.objects.filter(
        empresa=empresa,
        tipo=TipoLancamento.DESPESA,
        status=StatusLancamento.PENDENTE,
        data_vencimento__range=(inicio_periodo, proximos_30_dias)
    ).order_by('data_vencimento')[:5]
    
    # CONTAS VENCIDAS (no período)
    vencidas = LancamentoFinanceiro.objects.filter(
        empresa=empresa,
        status=StatusLancamento.PENDENTE,
        data_vencimento__lt=agora,
        data_vencimento__gte=inicio_periodo
    ).count()
    
    # RECEITAS POR CATEGORIA
    receitas_por_categoria = LancamentoFinanceiro.objects.filter(
        empresa=empresa,
        tipo=TipoLancamento.RECEITA,
        status=StatusLancamento.PAGO,
        data_vencimento__gte=inicio_periodo,
        data_vencimento__lte=fim_periodo
    ).values('categoria__nome', 'categoria__cor').annotate(
        total=Sum('valor')
    ).order_by('-total')
    
    # Anos disponíveis
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
    
    # Trimestres e Semestres
    TRIMESTRES = [(1, 'Q1'), (2, 'Q2'), (3, 'Q3'), (4, 'Q4')]
    SEMESTRES = [(1, '1º Semestre'), (2, '2º Semestre')]
    
    context = {
        'empresa': empresa,
        
        # Período
        'tipo_periodo': tipo_periodo,
        'periodo_nome': nome_periodo,
        'mes_selecionado': inicio_periodo.month if tipo_periodo == 'mes' else None,
        'ano_selecionado': inicio_periodo.year,
        'trimestre_selecionado': trimestre_selecionado or ((agora.month - 1) // 3) + 1,
        'semestre_selecionado': semestre_selecionado or (1 if agora.month <= 6 else 2),
        
        # Opções de seleção
        'meses_pt': MESES_PT,
        'trimestres': TRIMESTRES,
        'semestres': SEMESTRES,
        'anos_disponiveis': anos_disponiveis,
        
        # Receitas
        'receitas_total': receitas_periodo['total'] or 0,
        'receitas_pagas': receitas_periodo['pagas'] or 0,
        'receitas_pendentes': receitas_periodo['pendentes'] or 0,
        
        # Despesas
        'despesas_total': despesas_periodo['total'] or 0,
        'despesas_pagas': despesas_periodo['pagas'] or 0,
        'despesas_pendentes': despesas_periodo['pendentes'] or 0,
        
        # Saldo
        'saldo_real': saldo_real,
        'saldo_previsto': saldo_previsto,
        
        # Comparativo
        'comparativo_percentual': comparativo_percentual,
        'comparativo_positivo': comparativo_percentual >= 0,
        
        # Médias (apenas para períodos > 1 mês)
        'receita_media_mensal': receita_media_mensal,
        'despesa_media_mensal': despesa_media_mensal,
        'mostrar_medias': num_meses > 1,
        
        # Evolução (para gráfico)
        'evolucao_mensal': evolucao_mensal,
        'mostrar_grafico': num_meses > 1,
        
        # Contas
        'contas_receber': contas_receber,
        'contas_pagar': contas_pagar,
        'contas_vencidas': vencidas,
        
        # Gráficos
        'receitas_por_categoria': receitas_por_categoria,
        
        # Data de hoje
        'hoje': agora.date(),
    }
    
    return render(request, 'financeiro/dashboard.html', context)


@login_required
@plano_required(feature_flag='permite_financeiro', feature_name='Controle Financeiro')
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
@plano_required(feature_flag='permite_financeiro', feature_name='Controle Financeiro')
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
@plano_required(feature_flag='permite_financeiro', feature_name='Controle Financeiro')
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
@plano_required(feature_flag='permite_financeiro', feature_name='Controle Financeiro')
def lancamento_deletar(request, pk):
    """Deleta um lançamento"""
    empresa = request.user.empresa
    lancamento = get_object_or_404(LancamentoFinanceiro, pk=pk, empresa=empresa)
    
    if request.method == 'POST':
        lancamento.delete()
        return redirect('lancamentos_lista')
    
    return render(request, 'financeiro/lancamento_confirm_delete.html', {'lancamento': lancamento})


@login_required
@plano_required(feature_flag='permite_financeiro', feature_name='Controle Financeiro')
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