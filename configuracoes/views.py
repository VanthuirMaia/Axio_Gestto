from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.timezone import now
from datetime import timedelta

from empresas.models import Empresa, Servico, Profissional
from financeiro.models import CategoriaFinanceira, FormaPagamento

# Na view
from django.utils.safestring import mark_safe


@login_required
def configuracoes_dashboard(request):
    """Dashboard de configurações"""
    empresa = request.user.empresa
    
    context = {
        'empresa': empresa,
        'total_servicos': Servico.objects.filter(empresa=empresa, ativo=True).count(),
        'total_profissionais': Profissional.objects.filter(empresa=empresa, ativo=True).count(),
        'total_categorias': CategoriaFinanceira.objects.filter(empresa=empresa, ativo=True).count(),
        'total_formas_pagamento': FormaPagamento.objects.filter(empresa=empresa, ativo=True).count(),
    }
    
    return render(request, 'configuracoes/dashboard.html', context)


# ==========================================
# SERVIÇOS
# ==========================================

@login_required
def servicos_lista(request):
    """Lista todos os serviços"""
    empresa = request.user.empresa
    servicos = Servico.objects.filter(empresa=empresa).order_by('nome')
    
    context = {
        'empresa': empresa,
        'servicos': servicos,
    }
    
    return render(request, 'configuracoes/servicos_lista.html', context)


@login_required
def servico_criar(request):
    """Cria um novo serviço"""
    empresa = request.user.empresa
    
    if request.method == 'POST':
        nome = request.POST.get('nome')
        descricao = request.POST.get('descricao', '')
        duracao = request.POST.get('duracao')
        preco = request.POST.get('preco')
        
        Servico.objects.create(
            empresa=empresa,
            nome=nome,
            descricao=descricao,
            duracao=duracao,
            preco=preco
        )
        
        messages.success(request, f'Serviço "{nome}" criado com sucesso!')
        return redirect('servicos_lista')
    
    return render(request, 'configuracoes/servico_form.html', {'empresa': empresa})


@login_required
def servico_editar(request, pk):
    """Edita um serviço"""
    empresa = request.user.empresa
    servico = get_object_or_404(Servico, pk=pk, empresa=empresa)
    
    if request.method == 'POST':
        servico.nome = request.POST.get('nome')
        servico.descricao = request.POST.get('descricao', '')
        servico.duracao = request.POST.get('duracao')
        servico.preco = request.POST.get('preco')
        servico.ativo = request.POST.get('ativo') == 'on'
        servico.save()
        
        messages.success(request, f'Serviço "{servico.nome}" atualizado!')
        return redirect('servicos_lista')
    
    context = {
        'empresa': empresa,
        'servico': servico,
        'editando': True,
    }
    
    return render(request, 'configuracoes/servico_form.html', context)


@login_required
def servico_deletar(request, pk):
    """Deleta um serviço"""
    empresa = request.user.empresa
    servico = get_object_or_404(Servico, pk=pk, empresa=empresa)
    
    if request.method == 'POST':
        nome = servico.nome
        servico.delete()
        messages.success(request, f'Serviço "{nome}" deletado!')
        return redirect('servicos_lista')
    
    return render(request, 'configuracoes/servico_confirm_delete.html', {
        'empresa': empresa,
        'servico': servico
    })


# ==========================================
# CATEGORIAS FINANCEIRAS
# ==========================================

@login_required
def categorias_lista(request):
    """Lista todas as categorias financeiras"""
    empresa = request.user.empresa
    categorias = CategoriaFinanceira.objects.filter(empresa=empresa).order_by('tipo', 'nome')
    
    context = {
        'empresa': empresa,
        'categorias': categorias,
    }
    
    return render(request, 'configuracoes/categorias_lista.html', context)


@login_required
def categoria_criar(request):
    """Cria uma nova categoria"""
    empresa = request.user.empresa
    
    if request.method == 'POST':
        nome = request.POST.get('nome')
        tipo = request.POST.get('tipo')
        descricao = request.POST.get('descricao', '')
        cor = request.POST.get('cor', '#6c757d')
        
        CategoriaFinanceira.objects.create(
            empresa=empresa,
            nome=nome,
            tipo=tipo,
            descricao=descricao,
            cor=cor
        )
        
        messages.success(request, f'Categoria "{nome}" criada com sucesso!')
        return redirect('categorias_lista')
    
    return render(request, 'configuracoes/categoria_form.html', {'empresa': empresa})


@login_required
def categoria_editar(request, pk):
    """Edita uma categoria"""
    empresa = request.user.empresa
    categoria = get_object_or_404(CategoriaFinanceira, pk=pk, empresa=empresa)
    
    if request.method == 'POST':
        categoria.nome = request.POST.get('nome')
        categoria.tipo = request.POST.get('tipo')
        categoria.descricao = request.POST.get('descricao', '')
        categoria.cor = request.POST.get('cor', '#6c757d')
        categoria.ativo = request.POST.get('ativo') == 'on'
        categoria.save()
        
        messages.success(request, f'Categoria "{categoria.nome}" atualizada!')
        return redirect('categorias_lista')
    
    context = {
        'empresa': empresa,
        'categoria': categoria,
        'editando': True,
    }
    
    return render(request, 'configuracoes/categoria_form.html', context)


# ==========================================
# FORMAS DE PAGAMENTO
# ==========================================

@login_required
def formas_pagamento_lista(request):
    """Lista todas as formas de pagamento"""
    empresa = request.user.empresa
    formas = FormaPagamento.objects.filter(empresa=empresa).order_by('nome')
    
    context = {
        'empresa': empresa,
        'formas_pagamento': formas,
    }
    
    return render(request, 'configuracoes/formas_pagamento_lista.html', context)


@login_required
def forma_pagamento_criar(request):
    """Cria uma nova forma de pagamento"""
    empresa = request.user.empresa
    
    if request.method == 'POST':
        nome = request.POST.get('nome')
        
        FormaPagamento.objects.create(
            empresa=empresa,
            nome=nome
        )
        
        messages.success(request, f'Forma de pagamento "{nome}" criada!')
        return redirect('formas_pagamento_lista')
    
    return render(request, 'configuracoes/forma_pagamento_form.html', {'empresa': empresa})


@login_required
def forma_pagamento_editar(request, pk):
    """Edita uma forma de pagamento"""
    empresa = request.user.empresa
    forma = get_object_or_404(FormaPagamento, pk=pk, empresa=empresa)
    
    if request.method == 'POST':
        forma.nome = request.POST.get('nome')
        forma.ativo = request.POST.get('ativo') == 'on'
        forma.save()
        
        messages.success(request, f'Forma de pagamento "{forma.nome}" atualizada!')
        return redirect('formas_pagamento_lista')
    
    context = {
        'empresa': empresa,
        'forma_pagamento': forma,
        'editando': True,
    }
    
    return render(request, 'configuracoes/forma_pagamento_form.html', context)

# ==========================================
# PROFISSIONAIS
# ==========================================

@login_required
def profissionais_lista(request):
    """Lista todos os profissionais"""
    empresa = request.user.empresa
    profissionais = Profissional.objects.filter(empresa=empresa).order_by('nome')
    
    # Breadcrumb
    breadcrumb_items = [
        {'label': 'Configurações', 'url': '/configuracoes/', 'icon': 'gear-fill'},
        {'label': 'Profissionais', 'url': '#'},
    ]
    
    context = {
        'empresa': empresa,
        'profissionais': profissionais,
        'breadcrumb_items': breadcrumb_items,
    }
    
    return render(request, 'configuracoes/profissionais_lista.html', context)

@login_required
def profissional_criar(request):
    """Cria um novo profissional"""
    empresa = request.user.empresa
    
    if request.method == 'POST':
        nome = request.POST.get('nome')
        telefone = request.POST.get('telefone', '')
        email = request.POST.get('email', '')
        especialidade = request.POST.get('especialidade', '')
        
        Profissional.objects.create(
            empresa=empresa,
            nome=nome,
            telefone=telefone,
            email=email,
            especialidade=especialidade
        )
        
        messages.success(request, f'Profissional "{nome}" adicionado com sucesso!')
        return redirect('profissionais_lista')
    
    return render(request, 'configuracoes/profissional_form.html', {'empresa': empresa})


@login_required
def profissional_editar(request, pk):
    """Edita um profissional"""
    empresa = request.user.empresa
    profissional = get_object_or_404(Profissional, pk=pk, empresa=empresa)
    
    if request.method == 'POST':
        profissional.nome = request.POST.get('nome')
        profissional.telefone = request.POST.get('telefone', '')
        profissional.email = request.POST.get('email', '')
        profissional.especialidade = request.POST.get('especialidade', '')
        profissional.ativo = request.POST.get('ativo') == 'on'
        profissional.save()
        
        messages.success(request, f'Profissional "{profissional.nome}" atualizado!')
        return redirect('profissionais_lista')
    
    context = {
        'empresa': empresa,
        'profissional': profissional,
        'editando': True,
    }
    
    return render(request, 'configuracoes/profissional_form.html', context)


@login_required
def profissional_deletar(request, pk):
    """Deleta um profissional"""
    empresa = request.user.empresa
    profissional = get_object_or_404(Profissional, pk=pk, empresa=empresa)
    
    if request.method == 'POST':
        nome = profissional.nome
        profissional.delete()
        messages.success(request, f'Profissional "{nome}" removido!')
        return redirect('profissionais_lista')
    
    return render(request, 'configuracoes/profissional_confirm_delete.html', {
        'empresa': empresa,
        'profissional': profissional
    })


# ==========================================
# ASSINATURA E PLANO (SAAS)
# ==========================================

@login_required
def assinatura_gerenciar(request):
    """
    Gerenciar assinatura e plano
    - Ver plano atual
    - Uso atual vs limites
    - Fazer upgrade/downgrade
    - Cancelar assinatura
    """
    empresa = request.user.empresa

    if not hasattr(empresa, 'assinatura'):
        messages.error(request, 'Empresa sem assinatura ativa.')
        return redirect('dashboard')

    assinatura = empresa.assinatura
    plano = assinatura.plano

    # Calcular uso do mês atual
    inicio_mes = now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    from agendamentos.models import Agendamento

    agendamentos_mes = Agendamento.objects.filter(
        empresa=empresa,
        criado_em__gte=inicio_mes,
        status__in=['pendente', 'confirmado', 'concluido']
    ).count()

    profissionais_ativos = Profissional.objects.filter(
        empresa=empresa,
        ativo=True
    ).count()

    # Calcular percentuais de uso
    percentual_agendamentos = (agendamentos_mes / plano.max_agendamentos_mes) * 100 if plano.max_agendamentos_mes > 0 else 0
    percentual_profissionais = (profissionais_ativos / plano.max_profissionais) * 100 if plano.max_profissionais > 0 else 0

    # Buscar todos os planos disponíveis
    from assinaturas.models import Plano

    planos_disponiveis = Plano.objects.filter(ativo=True).order_by('preco_mensal')

    # Dias restantes
    dias_restantes = None
    if assinatura.data_expiracao:
        dias_restantes = (assinatura.data_expiracao - now()).days

    context = {
        'empresa': empresa,
        'assinatura': assinatura,
        'plano': plano,
        'planos_disponiveis': planos_disponiveis,

        # Uso atual
        'agendamentos_mes': agendamentos_mes,
        'profissionais_ativos': profissionais_ativos,
        'percentual_agendamentos': round(percentual_agendamentos, 1),
        'percentual_profissionais': round(percentual_profissionais, 1),

        # Status
        'dias_restantes': dias_restantes,
    }

    return render(request, 'configuracoes/assinatura.html', context)