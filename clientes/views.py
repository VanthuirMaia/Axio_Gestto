from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Sum, Q, Max
from django.utils.timezone import now
from datetime import timedelta

from .models import Cliente
from agendamentos.models import Agendamento


# ============================================
# DASHBOARD DE CLIENTES (NOVO)
# ============================================

@login_required
def dashboard_clientes(request):
    """Dashboard principal de clientes com métricas e insights"""
    empresa = request.user.empresa
    if not empresa:
        return redirect('logout')
    
    hoje = now().date()
    mes_atual = hoje.replace(day=1)
    
    # ============================================
    # MÉTRICAS GERAIS
    # ============================================
    
    total_clientes = Cliente.objects.filter(empresa=empresa, ativo=True).count()
    total_inativos = Cliente.objects.filter(empresa=empresa, ativo=False).count()
    
    # Novos clientes este mês
    novos_mes = Cliente.objects.filter(
        empresa=empresa,
        criado_em__gte=mes_atual  # ← CORRETO
    ).count()
    
    # Clientes que agendaram nos últimos 30 dias
    clientes_ativos_30d = Cliente.objects.filter(
        empresa=empresa,
        agendamentos__data_hora_inicio__gte=hoje - timedelta(days=30)
    ).distinct().count()
    
    # Taxa de retenção
    if total_clientes > 0:
        taxa_retencao = (clientes_ativos_30d / total_clientes) * 100
    else:
        taxa_retencao = 0
    
    # Ticket médio por cliente
    stats = Agendamento.objects.filter(
        empresa=empresa,
        status='concluido'
    ).aggregate(
        total_faturado=Sum('valor_cobrado'),
        total_agendamentos=Count('id')
    )
    
    if clientes_ativos_30d > 0:
        ticket_medio = (stats['total_faturado'] or 0) / clientes_ativos_30d
    else:
        ticket_medio = 0
    
    # ============================================
    # TOP CLIENTES VIP (Maior Gasto Total)
    # ============================================
    
    top_clientes_vip = Cliente.objects.filter(
        empresa=empresa,
        ativo=True
    ).annotate(
        total_gasto=Sum('agendamentos__valor_cobrado', filter=Q(agendamentos__status='concluido')),
        total_agendamentos=Count('agendamentos', filter=Q(agendamentos__status='concluido'))
    ).filter(
        total_gasto__isnull=False
    ).order_by('-total_gasto')[:10]
    
    # ============================================
    # CLIENTES FREQUENTES (Mais Agendamentos)
    # ============================================
    
    clientes_frequentes = Cliente.objects.filter(
        empresa=empresa,
        ativo=True
    ).annotate(
        total_agendamentos=Count('agendamentos'),
        ultimo_agendamento=Max('agendamentos__data_hora_inicio')
    ).filter(
        total_agendamentos__gte=1
    ).order_by('-total_agendamentos')[:10]
    
    # ============================================
    # CLIENTES EM RISCO (Sem agendar há +30 dias)
    # ============================================
    
    clientes_risco = Cliente.objects.filter(
        empresa=empresa,
        ativo=True
    ).annotate(
        ultimo_agendamento=Max('agendamentos__data_hora_inicio')
    ).filter(
        ultimo_agendamento__lt=hoje - timedelta(days=30)
    ).order_by('ultimo_agendamento')[:10]
    
    # ============================================
    # ANIVERSARIANTES DO MÊS
    # ============================================
    
    aniversariantes = Cliente.objects.filter(
        empresa=empresa,
        ativo=True,
        data_nascimento__month=hoje.month
    ).exclude(
        data_nascimento__isnull=True
    ).order_by('data_nascimento__day')[:10]
    
    # ============================================
    # GRÁFICO: Novos Clientes (últimos 6 meses)
    # ============================================
    
    meses_labels = []
    meses_valores = []
    
    for i in range(5, -1, -1):
        mes = hoje - timedelta(days=30*i)
        mes_inicio = mes.replace(day=1)
        
        if i == 0:
            mes_fim = hoje
        else:
            mes_fim = (mes_inicio + timedelta(days=32)).replace(day=1) - timedelta(days=1)
        
        count = Cliente.objects.filter(
            empresa=empresa,
            criado_em__gte=mes_inicio,  # ← CORRETO
            criado_em__lte=mes_fim      # ← CORRETO
        ).count()
        
        # Nome do mês em português
        meses_pt = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 
                    'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']
        mes_nome = meses_pt[mes_inicio.month - 1]
        
        meses_labels.append(mes_nome)
        meses_valores.append(count)
    
    # ============================================
    # CONTEXTO
    # ============================================
    
    context = {
        'empresa': empresa,
        
        # Métricas gerais
        'total_clientes': total_clientes,
        'total_inativos': total_inativos,
        'novos_mes': novos_mes,
        'clientes_ativos_30d': clientes_ativos_30d,
        'taxa_retencao': round(taxa_retencao, 1),
        'ticket_medio': ticket_medio,
        
        # Rankings
        'top_clientes_vip': top_clientes_vip,
        'clientes_frequentes': clientes_frequentes,
        'clientes_risco': clientes_risco,
        'aniversariantes': aniversariantes,
        
        # Gráfico
        'meses_labels': meses_labels,
        'meses_valores': meses_valores,
        
        # Data atual
        'hoje': hoje,
    }
    
    return render(request, 'clientes/dashboard.html', context)


# ============================================
# CRUD DE CLIENTES (MANTIDO COM MELHORIAS)
# ============================================

@login_required
def listar_clientes(request):
    """Lista completa de clientes (renomeado para lista_clientes no template)"""
    empresa = request.user.empresa
    if not empresa:
        return redirect('logout')
    
    # Filtros
    busca = request.GET.get('busca', '')
    status = request.GET.get('status', '')
    
    clientes = Cliente.objects.filter(empresa=empresa)
    
    # Busca por nome, telefone ou email
    if busca:
        clientes = clientes.filter(
            Q(nome__icontains=busca) |
            Q(telefone__icontains=busca) |
            Q(email__icontains=busca)
        )
    
    # Filtro de status
    if status == 'ativo':
        clientes = clientes.filter(ativo=True)
    elif status == 'inativo':
        clientes = clientes.filter(ativo=False)
    
    # Adicionar métricas aos clientes
    clientes = clientes.annotate(
        total_agendamentos=Count('agendamentos'),
        ultimo_agendamento=Max('agendamentos__data_hora_inicio'),
        total_gasto=Sum('agendamentos__valor_cobrado', filter=Q(agendamentos__status='concluido'))
    ).order_by('-criado_em')  # ← CORRETO
    
    context = {
        'empresa': empresa,
        'clientes': clientes,
        'busca': busca,
        'status_filtro': status,
    }
    return render(request, 'clientes/listar.html', context)


@login_required
def criar_cliente(request):
    empresa = request.user.empresa
    if not empresa:
        return redirect('logout')
    
    if request.method == 'POST':
        nome = request.POST.get('nome')
        email = request.POST.get('email')
        telefone = request.POST.get('telefone')
        cpf = request.POST.get('cpf', '')
        data_nascimento = request.POST.get('data_nascimento', None)
        endereco = request.POST.get('endereco', '')
        cidade = request.POST.get('cidade', '')
        estado = request.POST.get('estado', '')
        cep = request.POST.get('cep', '')
        notas = request.POST.get('notas', '')
        
        try:
            cliente = Cliente.objects.create(
                empresa=empresa,
                nome=nome,
                email=email,
                telefone=telefone,
                cpf=cpf,
                data_nascimento=data_nascimento if data_nascimento else None,
                endereco=endereco,
                cidade=cidade,
                estado=estado,
                cep=cep,
                notas=notas,
            )
            messages.success(request, f'Cliente "{nome}" criado com sucesso!')
            return redirect('listar_clientes')
        except Exception as e:
            messages.error(request, f'Erro ao criar cliente: {str(e)}')
    
    context = {
        'empresa': empresa,
    }
    return render(request, 'clientes/criar.html', context)


@login_required
def editar_cliente(request, id):
    empresa = request.user.empresa
    cliente = get_object_or_404(Cliente, id=id, empresa=empresa)
    
    if request.method == 'POST':
        cliente.nome = request.POST.get('nome', cliente.nome)
        cliente.email = request.POST.get('email', cliente.email)
        cliente.telefone = request.POST.get('telefone', cliente.telefone)
        cliente.cpf = request.POST.get('cpf', cliente.cpf)
        
        data_nasc = request.POST.get('data_nascimento', '')
        cliente.data_nascimento = data_nasc if data_nasc else None
        
        cliente.endereco = request.POST.get('endereco', cliente.endereco)
        cliente.cidade = request.POST.get('cidade', cliente.cidade)
        cliente.estado = request.POST.get('estado', cliente.estado)
        cliente.cep = request.POST.get('cep', cliente.cep)
        cliente.notas = request.POST.get('notas', cliente.notas)
        cliente.ativo = request.POST.get('ativo') == 'on'
        cliente.save()
        
        messages.success(request, f'Cliente "{cliente.nome}" atualizado com sucesso!')
        return redirect('listar_clientes')
    
    context = {
        'empresa': empresa,
        'cliente': cliente,
    }
    return render(request, 'clientes/editar.html', context)


@login_required
def deletar_cliente(request, id):
    empresa = request.user.empresa
    cliente = get_object_or_404(Cliente, id=id, empresa=empresa)
    
    if request.method == 'POST':
        nome = cliente.nome
        cliente.delete()
        messages.success(request, f'Cliente "{nome}" deletado com sucesso!')
        return redirect('listar_clientes')
    
    context = {
        'empresa': empresa,
        'cliente': cliente,
    }
    return render(request, 'clientes/deletar.html', context)


# ============================================
# DETALHES DE CLIENTE (NOVO)
# ============================================

@login_required
def detalhes_cliente(request, id):
    """Visualiza perfil completo do cliente com histórico"""
    empresa = request.user.empresa
    cliente = get_object_or_404(Cliente, id=id, empresa=empresa)
    
    # Histórico de agendamentos
    agendamentos = cliente.agendamentos.all().select_related(
        'servico', 'profissional'
    ).order_by('-data_hora_inicio')[:20]
    
    # Estatísticas do cliente
    stats = cliente.agendamentos.filter(status='concluido').aggregate(
        total_gasto=Sum('valor_cobrado'),
        total_visitas=Count('id')
    )
    
    # Último agendamento
    ultimo = cliente.agendamentos.order_by('-data_hora_inicio').first()
    
    context = {
        'empresa': empresa,
        'cliente': cliente,
        'agendamentos': agendamentos,
        'total_gasto': stats['total_gasto'] or 0,
        'total_visitas': stats['total_visitas'] or 0,
        'ultimo_agendamento': ultimo,
    }
    
    return render(request, 'clientes/detalhes.html', context)