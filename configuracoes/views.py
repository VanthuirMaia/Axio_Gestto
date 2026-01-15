from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from django.utils.timezone import now
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
import logging

logger = logging.getLogger(__name__)
from datetime import timedelta

from empresas.models import Empresa, Servico, Profissional, HorarioFuncionamento, DataEspecial
from financeiro.models import CategoriaFinanceira, FormaPagamento

# Na view
from django.utils.safestring import mark_safe


@login_required
def configuracoes_dashboard(request):
    """Dashboard de configuracoes"""
    from core.models import Usuario

    empresa = request.user.empresa

    context = {
        'empresa': empresa,
        'total_servicos': Servico.objects.filter(empresa=empresa, ativo=True).count(),
        'total_profissionais': Profissional.objects.filter(empresa=empresa, ativo=True).count(),
        'total_categorias': CategoriaFinanceira.objects.filter(empresa=empresa, ativo=True).count(),
        'total_formas_pagamento': FormaPagamento.objects.filter(empresa=empresa, ativo=True).count(),
        'total_usuarios': Usuario.objects.filter(empresa=empresa, ativo=True).count(),
        'total_datas_especiais': DataEspecial.objects.filter(empresa=empresa).count(),
    }

    return render(request, 'configuracoes/dashboard.html', context)


# ==========================================
# DADOS DA EMPRESA
# ==========================================

@login_required
def empresa_dados(request):
    """Edita os dados da empresa (nome, endereço, contato, etc.)"""
    empresa = request.user.empresa

    if request.method == 'POST':
        # Dados básicos
        empresa.nome = request.POST.get('nome', empresa.nome)
        empresa.descricao = request.POST.get('descricao', '')
        empresa.telefone = request.POST.get('telefone', empresa.telefone)
        empresa.email = request.POST.get('email', empresa.email)

        # Endereço
        empresa.endereco = request.POST.get('endereco', '')
        empresa.cidade = request.POST.get('cidade', '')
        empresa.estado = request.POST.get('estado', '')
        empresa.cep = request.POST.get('cep', '')
        empresa.google_maps_link = request.POST.get('google_maps_link', '')

        empresa.save()

        messages.success(request, 'Dados da empresa atualizados com sucesso!')
        return redirect('empresa_dados')

    context = {
        'empresa': empresa,
    }

    return render(request, 'configuracoes/empresa_dados.html', context)


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
# USUARIOS DA EMPRESA
# ==========================================

@login_required
def usuarios_lista(request):
    """Lista todos os usuarios da empresa"""
    from core.models import Usuario

    empresa = request.user.empresa
    usuarios = Usuario.objects.filter(empresa=empresa).order_by('-criado_em')
    usuarios_ativos = usuarios.filter(ativo=True).count()

    # Verificar limite do plano
    assinatura = getattr(empresa, 'assinatura', None)
    if assinatura and assinatura.plano:
        max_usuarios = assinatura.plano.max_usuarios
        pode_criar = usuarios_ativos < max_usuarios
    else:
        max_usuarios = 1  # Sem plano = limite minimo
        pode_criar = usuarios_ativos < max_usuarios

    context = {
        'empresa': empresa,
        'usuarios': usuarios,
        'total_usuarios': usuarios.count(),
        'usuarios_ativos': usuarios_ativos,
        'max_usuarios': max_usuarios,
        'pode_criar': pode_criar,
    }

    return render(request, 'configuracoes/usuarios_lista.html', context)


@login_required
def usuario_criar(request):
    """Cria um novo usuario para a empresa"""
    from core.models import Usuario
    from django.contrib.auth import password_validation
    from django.core.exceptions import ValidationError

    empresa = request.user.empresa

    # Verificar limite do plano
    usuarios_ativos = Usuario.objects.filter(empresa=empresa, ativo=True).count()
    assinatura = getattr(empresa, 'assinatura', None)

    if assinatura and assinatura.plano:
        max_usuarios = assinatura.plano.max_usuarios
        plano_nome = assinatura.plano.get_nome_display()
    else:
        max_usuarios = 1
        plano_nome = 'Sem plano'

    if usuarios_ativos >= max_usuarios:
        messages.error(
            request,
            f'Limite de usuarios atingido! Seu plano ({plano_nome}) permite ate {max_usuarios} usuario(s). '
            f'Faca upgrade do plano para adicionar mais usuarios.'
        )
        return redirect('usuarios_lista')

    if request.method == 'POST':
        nome = request.POST.get('nome', '').strip()
        email = request.POST.get('email', '').strip().lower()
        telefone = request.POST.get('telefone', '').strip()
        senha = request.POST.get('senha', '')
        confirmar_senha = request.POST.get('confirmar_senha', '')
        is_admin = request.POST.get('is_admin') == 'on'

        # Validacoes
        erros = []

        if not nome:
            erros.append('Nome e obrigatorio.')

        if not email:
            erros.append('Email e obrigatorio.')
        elif Usuario.objects.filter(email=email).exists():
            erros.append('Ja existe um usuario com este email.')

        if not senha:
            erros.append('Senha e obrigatoria.')
        elif senha != confirmar_senha:
            erros.append('As senhas nao coincidem.')
        else:
            try:
                password_validation.validate_password(senha)
            except ValidationError as e:
                erros.extend(e.messages)

        if erros:
            for erro in erros:
                messages.error(request, erro)
            return render(request, 'configuracoes/usuario_form.html', {
                'empresa': empresa,
                'form_data': request.POST,
            })

        # Criar usuario
        username = email.split('@')[0]
        # Garantir username unico
        base_username = username
        counter = 1
        while Usuario.objects.filter(username=username).exists():
            username = f"{base_username}{counter}"
            counter += 1

        usuario = Usuario.objects.create_user(
            username=username,
            email=email,
            password=senha,
            first_name=nome.split()[0] if nome else '',
            last_name=' '.join(nome.split()[1:]) if len(nome.split()) > 1 else '',
            empresa=empresa,
            telefone=telefone,
            is_staff=is_admin,
            ativo=True,
        )

        messages.success(request, f'Usuario "{nome}" criado com sucesso!')
        return redirect('usuarios_lista')

    return render(request, 'configuracoes/usuario_form.html', {'empresa': empresa})


@login_required
def usuario_editar(request, pk):
    """Edita um usuario da empresa"""
    from core.models import Usuario

    empresa = request.user.empresa
    usuario = get_object_or_404(Usuario, pk=pk, empresa=empresa)

    # Nao permitir editar a si mesmo por esta tela (usar alterar senha)
    if usuario == request.user:
        messages.warning(request, 'Para editar seu proprio perfil, use a opcao "Alterar Senha".')
        return redirect('usuarios_lista')

    if request.method == 'POST':
        nome = request.POST.get('nome', '').strip()
        email = request.POST.get('email', '').strip().lower()
        telefone = request.POST.get('telefone', '').strip()
        is_admin = request.POST.get('is_admin') == 'on'
        ativo = request.POST.get('ativo') == 'on'
        nova_senha = request.POST.get('nova_senha', '').strip()

        # Validacoes
        erros = []

        if not nome:
            erros.append('Nome e obrigatorio.')

        if not email:
            erros.append('Email e obrigatorio.')
        elif Usuario.objects.filter(email=email).exclude(pk=pk).exists():
            erros.append('Ja existe outro usuario com este email.')

        if nova_senha:
            from django.contrib.auth import password_validation
            from django.core.exceptions import ValidationError
            try:
                password_validation.validate_password(nova_senha)
            except ValidationError as e:
                erros.extend(e.messages)

        if erros:
            for erro in erros:
                messages.error(request, erro)
            return render(request, 'configuracoes/usuario_form.html', {
                'empresa': empresa,
                'usuario': usuario,
                'editando': True,
            })

        # Atualizar usuario
        usuario.first_name = nome.split()[0] if nome else ''
        usuario.last_name = ' '.join(nome.split()[1:]) if len(nome.split()) > 1 else ''
        usuario.email = email
        usuario.telefone = telefone
        usuario.is_staff = is_admin
        usuario.ativo = ativo

        if nova_senha:
            usuario.set_password(nova_senha)

        usuario.save()

        messages.success(request, f'Usuario "{nome}" atualizado com sucesso!')
        return redirect('usuarios_lista')

    context = {
        'empresa': empresa,
        'usuario': usuario,
        'editando': True,
    }

    return render(request, 'configuracoes/usuario_form.html', context)


@login_required
def usuario_deletar(request, pk):
    """Deleta (desativa) um usuario da empresa"""
    from core.models import Usuario

    empresa = request.user.empresa
    usuario = get_object_or_404(Usuario, pk=pk, empresa=empresa)

    # Nao permitir deletar a si mesmo
    if usuario == request.user:
        messages.error(request, 'Voce nao pode deletar seu proprio usuario.')
        return redirect('usuarios_lista')

    # Nao deletar, apenas desativar
    if request.method == 'POST':
        usuario.ativo = False
        usuario.save()
        messages.success(request, f'Usuario "{usuario.get_full_name()}" desativado.')
        return redirect('usuarios_lista')

    return render(request, 'configuracoes/usuario_confirmar_delete.html', {
        'empresa': empresa,
        'usuario': usuario,
    })


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
        {'label': 'Configurações', 'url': reverse('configuracoes_dashboard'), 'icon': 'gear-fill'},
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
        cor_hex = request.POST.get('cor_hex', '#1e3a8a')

        profissional = Profissional.objects.create(
            empresa=empresa,
            nome=nome,
            telefone=telefone,
            email=email,
            cor_hex=cor_hex
        )

        # Associar servicos selecionados
        servicos_ids = request.POST.getlist('servicos')
        if servicos_ids:
            profissional.servicos.set(servicos_ids)

        messages.success(request, f'Profissional "{nome}" adicionado com sucesso!')
        return redirect('profissionais_lista')

    servicos = Servico.objects.filter(empresa=empresa, ativo=True)
    return render(request, 'configuracoes/profissional_form.html', {'empresa': empresa, 'servicos': servicos})


@login_required
def profissional_editar(request, pk):
    """Edita um profissional"""
    empresa = request.user.empresa
    profissional = get_object_or_404(Profissional, pk=pk, empresa=empresa)

    if request.method == 'POST':
        profissional.nome = request.POST.get('nome')
        profissional.telefone = request.POST.get('telefone', '')
        profissional.email = request.POST.get('email', '')
        profissional.cor_hex = request.POST.get('cor_hex', '#1e3a8a')
        profissional.ativo = request.POST.get('ativo') == 'on'
        profissional.save()

        # Atualizar servicos
        servicos_ids = request.POST.getlist('servicos')
        profissional.servicos.set(servicos_ids)

        messages.success(request, f'Profissional "{profissional.nome}" atualizado!')
        return redirect('profissionais_lista')

    servicos = Servico.objects.filter(empresa=empresa, ativo=True)
    context = {
        'empresa': empresa,
        'profissional': profissional,
        'servicos': servicos,
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


@login_required
def assinatura_alterar_plano(request):
    """
    Altera o plano da assinatura (upgrade ou downgrade)
    """
    from django.http import JsonResponse
    from assinaturas.models import Plano, HistoricoPagamento

    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Metodo nao permitido'}, status=405)

    empresa = request.user.empresa

    if not hasattr(empresa, 'assinatura'):
        return JsonResponse({'success': False, 'error': 'Empresa sem assinatura'}, status=400)

    assinatura = empresa.assinatura
    plano_atual = assinatura.plano

    # Obter novo plano
    novo_plano_id = request.POST.get('plano_id')
    if not novo_plano_id:
        return JsonResponse({'success': False, 'error': 'Plano nao informado'}, status=400)

    try:
        novo_plano = Plano.objects.get(id=novo_plano_id, ativo=True)
    except Plano.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Plano nao encontrado'}, status=404)

    # Verificar se e o mesmo plano
    if novo_plano.id == plano_atual.id:
        return JsonResponse({'success': False, 'error': 'Voce ja esta neste plano'}, status=400)

    # Verificar limites antes de downgrade
    if novo_plano.preco_mensal < plano_atual.preco_mensal:
        # E um downgrade - verificar se o uso atual permite
        profissionais_ativos = Profissional.objects.filter(empresa=empresa, ativo=True).count()
        servicos_ativos = Servico.objects.filter(empresa=empresa, ativo=True).count()

        erros = []
        if profissionais_ativos > novo_plano.max_profissionais:
            erros.append(f'Voce tem {profissionais_ativos} profissionais ativos, mas o plano permite apenas {novo_plano.max_profissionais}')
        if servicos_ativos > novo_plano.max_servicos:
            erros.append(f'Voce tem {servicos_ativos} servicos ativos, mas o plano permite apenas {novo_plano.max_servicos}')

        if erros:
            return JsonResponse({
                'success': False,
                'error': 'Nao e possivel fazer downgrade',
                'detalhes': erros
            }, status=400)

    # Registrar plano anterior para historico
    plano_anterior = plano_atual.get_nome_display()
    preco_anterior = plano_atual.preco_mensal

    # Alterar o plano
    assinatura.plano = novo_plano
    assinatura.save()

    # Determinar tipo de alteracao
    tipo = 'upgrade' if novo_plano.preco_mensal > preco_anterior else 'downgrade'

    logger.info(f"Plano alterado: {empresa.nome} - {plano_anterior} -> {novo_plano.get_nome_display()} ({tipo})")

    messages.success(
        request,
        f'{tipo.capitalize()} realizado com sucesso! Seu plano foi alterado para {novo_plano.get_nome_display()}.'
    )

    return JsonResponse({
        'success': True,
        'tipo': tipo,
        'plano_anterior': plano_anterior,
        'plano_novo': novo_plano.get_nome_display(),
        'preco_novo': float(novo_plano.preco_mensal)
    })


@login_required
def assinatura_cancelar(request):
    """
    Cancela a assinatura da empresa
    """
    from django.http import JsonResponse

    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Metodo nao permitido'}, status=405)

    empresa = request.user.empresa

    if not hasattr(empresa, 'assinatura'):
        return JsonResponse({'success': False, 'error': 'Empresa sem assinatura'}, status=400)

    assinatura = empresa.assinatura

    # Verificar se ja esta cancelada
    if assinatura.status == 'cancelada':
        return JsonResponse({'success': False, 'error': 'Assinatura ja esta cancelada'}, status=400)

    # Obter motivo do cancelamento
    motivo = request.POST.get('motivo', '')

    # Cancelar assinatura
    assinatura.cancelar(motivo=motivo)

    logger.info(f"Assinatura cancelada: {empresa.nome} - Motivo: {motivo}")

    messages.warning(
        request,
        'Sua assinatura foi cancelada. Voce mantera acesso ao sistema ate o final do periodo pago.'
    )

    return JsonResponse({
        'success': True,
        'message': 'Assinatura cancelada com sucesso',
        'data_acesso_final': assinatura.data_expiracao.strftime('%d/%m/%Y') if assinatura.data_expiracao else None
    })


@login_required
def assinatura_reativar(request):
    """
    Reativa uma assinatura cancelada (dentro do periodo de 90 dias)
    """
    from django.http import JsonResponse

    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Metodo nao permitido'}, status=405)

    empresa = request.user.empresa

    if not hasattr(empresa, 'assinatura'):
        return JsonResponse({'success': False, 'error': 'Empresa sem assinatura'}, status=400)

    assinatura = empresa.assinatura

    # Verificar se esta cancelada ou suspensa
    if assinatura.status not in ['cancelada', 'suspensa']:
        return JsonResponse({'success': False, 'error': 'Assinatura nao pode ser reativada'}, status=400)

    # Verificar periodo de 90 dias para canceladas
    if assinatura.status == 'cancelada' and assinatura.cancelada_em:
        dias_desde_cancelamento = (now() - assinatura.cancelada_em).days
        if dias_desde_cancelamento > 90:
            return JsonResponse({
                'success': False,
                'error': 'Periodo de reativacao expirado (90 dias)'
            }, status=400)

    # Reativar - volta para trial se ainda tinha dias, senao vai para ativa
    assinatura.status = 'ativa'
    assinatura.cancelada_em = None
    assinatura.motivo_cancelamento = ''

    # Renovar por mais 30 dias
    assinatura.data_expiracao = now() + timedelta(days=30)
    assinatura.proximo_vencimento = (now() + timedelta(days=30)).date()
    assinatura.save()

    logger.info(f"Assinatura reativada: {empresa.nome}")

    messages.success(request, 'Sua assinatura foi reativada com sucesso!')

    return JsonResponse({
        'success': True,
        'message': 'Assinatura reativada com sucesso'
    })


# ==========================================
# WHATSAPP / EVOLUTION API
# ==========================================

@login_required
def whatsapp_dashboard(request):
    """
    Dashboard de configuração do WhatsApp
    """
    empresa = request.user.empresa

    # Criar ou buscar configuração
    from empresas.models import ConfiguracaoWhatsApp
    from empresas.services import EvolutionAPIService

    config, created = ConfiguracaoWhatsApp.objects.get_or_create(
        empresa=empresa,
        defaults={
            'evolution_api_url': getattr(settings, 'EVOLUTION_API_URL', ''),
            'evolution_api_key': getattr(settings, 'EVOLUTION_API_KEY', ''),
        }
    )

    # Se acabou de criar, gerar nome da instância
    if created:
        config.gerar_instance_name()
        config.gerar_webhook_secret()

    # Se já tem instância configurada, sincronizar com Evolution API
    # para detectar se foi deletada externamente
    if config.instance_name and not created:
        service = EvolutionAPIService(config)
        sync_result = service.sincronizar_status()

        # Se foi deletada externamente, mostrar mensagem ao usuário
        if sync_result.get('action') == 'deleted_externally':
            messages.warning(
                request,
                'A instância do WhatsApp foi removida externamente. '
                'É necessário criar uma nova conexão.'
            )

    context = {
        'empresa': empresa,
        'config': config,
        'conectado': config.esta_conectado(),
        'pode_criar': config.status in ['nao_configurado', 'desconectado', 'erro'],
    }

    return render(request, 'configuracoes/whatsapp.html', context)


@login_required
def whatsapp_criar_instancia(request):
    """
    Conecta WhatsApp usando método robusto com retry (AJAX)
    """
    from django.http import JsonResponse
    from empresas.models import ConfiguracaoWhatsApp
    from empresas.services import EvolutionAPIService

    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Método não permitido'}, status=405)

    empresa = request.user.empresa
    config = ConfiguracaoWhatsApp.objects.get(empresa=empresa)

    # Criar service e usar método robusto
    service = EvolutionAPIService(config)
    result = service.conectar_whatsapp()

    if result['success']:
        response_data = {
            'success': True,
            'status': result['status'],
            'message': result['message'],
            'action': result['action'],
            'instance_name': config.instance_name
        }

        # Incluir QR Code se disponível
        if result.get('qrcode'):
            response_data['qrcode'] = result['qrcode']

        return JsonResponse(response_data)
    else:
        return JsonResponse({
            'success': False,
            'error': result.get('message', 'Erro ao conectar WhatsApp'),
            'action': result.get('action', 'error')
        })


@login_required
def whatsapp_obter_qr(request):
    """
    Obtém QR Code atualizado (AJAX polling)
    """
    from django.http import JsonResponse
    from empresas.models import ConfiguracaoWhatsApp
    from empresas.services import EvolutionAPIService

    empresa = request.user.empresa

    try:
        config = ConfiguracaoWhatsApp.objects.get(empresa=empresa)
    except ConfiguracaoWhatsApp.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Configuração não encontrada'})

    service = EvolutionAPIService(config)

    # Verificar status primeiro
    status_result = service.obter_status_conexao()

    # Se já está conectado, retornar sucesso
    if config.esta_conectado():
        return JsonResponse({
            'success': True,
            'conectado': True,
            'status': config.status,
            'numero': config.numero_conectado,
            'nome': config.nome_perfil
        })

    # Se aguardando QR, tentar obter novo
    if config.status == 'aguardando_qr':
        qr_result = service.obter_qrcode()

        return JsonResponse({
            'success': True,
            'conectado': False,
            'qrcode': qr_result.get('qrcode', config.qr_code),
            'status': config.status
        })

    return JsonResponse({
        'success': True,
        'conectado': False,
        'status': config.status,
        'qrcode': config.qr_code
    })


@login_required
def whatsapp_verificar_status(request):
    """
    Verifica status da conexão (AJAX)
    """
    from django.http import JsonResponse
    from empresas.models import ConfiguracaoWhatsApp
    from empresas.services import EvolutionAPIService

    empresa = request.user.empresa

    try:
        config = ConfiguracaoWhatsApp.objects.get(empresa=empresa)
    except ConfiguracaoWhatsApp.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Configuração não encontrada'})

    service = EvolutionAPIService(config)
    result = service.obter_status_conexao()

    return JsonResponse({
        'success': result['success'],
        'status': config.status,
        'conectado': config.esta_conectado(),
        'numero': config.numero_conectado,
        'nome': config.nome_perfil,
        'foto': config.foto_perfil_url
    })


@login_required
def whatsapp_desconectar(request):
    """
    Desconecta WhatsApp (logout)
    """
    from django.http import JsonResponse
    from empresas.models import ConfiguracaoWhatsApp
    from empresas.services import EvolutionAPIService

    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Método não permitido'}, status=405)

    empresa = request.user.empresa

    try:
        config = ConfiguracaoWhatsApp.objects.get(empresa=empresa)
    except ConfiguracaoWhatsApp.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Configuração não encontrada'})

    service = EvolutionAPIService(config)
    result = service.desconectar_instancia()

    if result['success']:
        messages.success(request, 'WhatsApp desconectado com sucesso!')
        return JsonResponse({'success': True, 'message': 'Desconectado com sucesso'})
    else:
        return JsonResponse({
            'success': False,
            'error': result.get('error', 'Erro ao desconectar')
        })


@login_required
def whatsapp_deletar_instancia(request):
    """
    Deleta instância completamente (CUIDADO: Irreversível)
    """
    from django.http import JsonResponse
    from empresas.models import ConfiguracaoWhatsApp
    from empresas.services import EvolutionAPIService

    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Método não permitido'}, status=405)

    empresa = request.user.empresa

    try:
        config = ConfiguracaoWhatsApp.objects.get(empresa=empresa)
    except ConfiguracaoWhatsApp.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Configuração não encontrada'})

    service = EvolutionAPIService(config)
    result = service.deletar_instancia()

    if result['success']:
        messages.success(request, 'Instância deletada. Você pode criar uma nova.')
        return JsonResponse({'success': True, 'message': 'Instância deletada'})
    else:
        return JsonResponse({
            'success': False,
            'error': result.get('error', 'Erro ao deletar')
        })


@login_required
def whatsapp_reconfigurar(request):
    """
    Reconfigura webhook e settings de uma instância existente (AJAX)
    """
    from django.http import JsonResponse
    from empresas.models import ConfiguracaoWhatsApp
    from empresas.services import EvolutionAPIService

    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Método não permitido'}, status=405)

    empresa = request.user.empresa

    try:
        config = ConfiguracaoWhatsApp.objects.get(empresa=empresa)
    except ConfiguracaoWhatsApp.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Configuração não encontrada'})

    service = EvolutionAPIService(config)

    # Reconfigurar webhook
    webhook_result = service.configurar_webhook()
    settings_result = service.configurar_settings()

    if webhook_result['success'] and settings_result['success']:
        messages.success(request, 'Configurações aplicadas com sucesso!')
        return JsonResponse({
            'success': True,
            'message': 'Webhook e Settings reconfigurados'
        })
    else:
        errors = []
        if not webhook_result['success']:
            errors.append(f"Webhook: {webhook_result.get('error')}")
        if not settings_result['success']:
            errors.append(f"Settings: {settings_result.get('error')}")

        return JsonResponse({
            'success': False,
            'error': ' | '.join(errors)
        })


@login_required
def whatsapp_sincronizar(request):
    """
    Sincroniza status da instância com Evolution API (AJAX)
    Detecta se a instância foi deletada externamente
    """
    from django.http import JsonResponse
    from empresas.models import ConfiguracaoWhatsApp
    from empresas.services import EvolutionAPIService

    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Método não permitido'}, status=405)

    empresa = request.user.empresa

    try:
        config = ConfiguracaoWhatsApp.objects.get(empresa=empresa)
    except ConfiguracaoWhatsApp.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Configuração não encontrada'})

    # Se não tem instância configurada, não precisa sincronizar
    if not config.instance_name:
        return JsonResponse({
            'success': True,
            'action': 'no_instance',
            'message': 'Nenhuma instância configurada'
        })

    service = EvolutionAPIService(config)
    result = service.sincronizar_status()

    if result['success']:
        # Mensagens personalizadas baseadas na ação
        if result['action'] == 'deleted_externally':
            messages.warning(
                request,
                'A instância foi removida externamente. Configuração foi resetada.'
            )
        elif result['action'] == 'status_updated':
            messages.success(request, 'Status sincronizado com sucesso!')

        return JsonResponse({
            'success': True,
            'action': result['action'],
            'message': result['message'],
            'status': config.status,
            'conectado': config.esta_conectado()
        })
    else:
        return JsonResponse({
            'success': False,
            'error': result.get('message', 'Erro ao sincronizar')
        })


@login_required
def whatsapp_resetar_config(request):
    """
    Reseta completamente a configuracao local do WhatsApp.
    AGORA TAMBEM deleta a instancia na Evolution API para evitar conflitos.
    """
    from django.http import JsonResponse
    from empresas.models import ConfiguracaoWhatsApp, WhatsAppInstance
    from empresas.services import EvolutionAPIService

    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Metodo nao permitido'}, status=405)

    empresa = request.user.empresa

    try:
        config = ConfiguracaoWhatsApp.objects.get(empresa=empresa)
    except ConfiguracaoWhatsApp.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Configuracao nao encontrada'})

    # ✅ NOVO: Tentar deletar a instância na Evolution API antes de resetar
    if config.instance_name:
        try:
            service = EvolutionAPIService(config)
            delete_result = service.deletar_instancia()
            
            if delete_result['success']:
                logger.info(f"Instância {config.instance_name} deletada na Evolution API com sucesso")
            else:
                logger.warning(f"Não foi possível deletar instância na Evolution API: {delete_result.get('error')}")
                # Continua mesmo se falhar - pode ser que já tenha sido deletada
        except Exception as e:
            logger.error(f"Erro ao tentar deletar instância: {e}")
            # Continua mesmo com erro

    # Resetar todos os campos
    config.instance_name = ''
    config.instance_token = ''
    config.status = 'nao_configurado'
    config.qr_code = ''
    config.qr_code_expira_em = None
    config.webhook_url = ''
    config.webhook_secret = ''
    config.numero_conectado = ''
    config.nome_perfil = ''
    config.foto_perfil_url = ''
    config.metadados = {}
    config.ultimo_erro = ''
    config.save()

    # Limpar instancias orfas
    WhatsAppInstance.objects.filter(empresa=empresa).delete()

    messages.success(request, 'Configuracao resetada com sucesso! Voce pode criar uma nova instancia.')

    return JsonResponse({
        'success': True,
        'message': 'Configuracao resetada e instancia deletada'
    })


# ==========================================
# WEBHOOK INTERMEDIARIO (Evolution -> Django -> n8n)
# ==========================================

@csrf_exempt
def whatsapp_webhook_n8n(request, empresa_id, secret):
    """
    Webhook intermediário que recebe mensagens da Evolution API,
    valida empresa/assinatura e encaminha para n8n.

    URL: /api/webhooks/whatsapp/<empresa_id>/<secret>/

    Fluxo:
    1. Evolution API → Django (aqui)
    2. Django valida empresa, secret, assinatura
    3. Django adiciona empresa_id ao payload
    4. Django → n8n workflow
    5. n8n processa e responde via Evolution API
    """
    import json
    import requests
    import logging
    from django.views.decorators.csrf import csrf_exempt
    from django.http import JsonResponse
    from empresas.models import Empresa, ConfiguracaoWhatsApp

    logger = logging.getLogger(__name__)

    # Apenas POST
    if request.method != 'POST':
        return JsonResponse({'error': 'Apenas POST permitido'}, status=405)

    try:
        # 1. Buscar empresa e configuração WhatsApp
        try:
            empresa = Empresa.objects.select_related('whatsapp_config').get(id=empresa_id)
            config = empresa.whatsapp_config
        except Empresa.DoesNotExist:
            logger.error(f"Webhook: Empresa {empresa_id} não encontrada")
            return JsonResponse({'error': 'Empresa não encontrada'}, status=404)
        except ConfiguracaoWhatsApp.DoesNotExist:
            logger.error(f"Webhook: Empresa {empresa_id} sem configuração WhatsApp")
            return JsonResponse({'error': 'WhatsApp não configurado'}, status=404)

        # 2. Validar secret
        if config.webhook_secret != secret:
            logger.warning(f"Webhook: Secret inválido para empresa {empresa_id}")
            return JsonResponse({'error': 'Não autorizado'}, status=403)

        # 3. Validar se assinatura está ativa
        if not empresa.assinatura_ativa:
            logger.warning(f"Webhook: Assinatura inativa para empresa {empresa_id} ({empresa.nome})")

            # TODO: Enviar mensagem informando que assinatura está vencida
            # (pode fazer isso via Evolution API direto aqui, ou deixar n8n decidir)

            return JsonResponse({
                'error': 'Assinatura inativa',
                'message': 'Entre em contato com suporte para reativar'
            }, status=402)

        # 4. Parsear payload da Evolution API
        try:
            body = json.loads(request.body.decode('utf-8'))
        except json.JSONDecodeError:
            logger.error("Webhook: Payload inválido (não é JSON)")
            return JsonResponse({'error': 'Payload inválido'}, status=400)

        # 5. Montar payload enriquecido para n8n
        payload_n8n = {
            'empresa_id': empresa.id,
            'empresa_nome': empresa.nome,
            'instance': config.instance_name,
            'body': body  # Payload original da Evolution
        }

        # Log para debug
        logger.info(f"Webhook recebido: empresa={empresa.nome} (ID={empresa.id}), instance={config.instance_name}")

        # 6. Encaminhar para n8n
        n8n_webhook_url = settings.N8N_WEBHOOK_URL

        if not n8n_webhook_url:
            logger.error("N8N_WEBHOOK_URL não configurado em settings")
            return JsonResponse({'error': 'Configuração interna incorreta'}, status=500)

        try:
            response = requests.post(
                n8n_webhook_url,
                json=payload_n8n,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )

            if response.status_code == 200:
                logger.info(f"Webhook encaminhado para n8n com sucesso: empresa={empresa.nome}")
                return JsonResponse({
                    'success': True,
                    'forwarded_to_n8n': True,
                    'empresa': empresa.nome
                })
            else:
                logger.error(f"Erro ao encaminhar para n8n: status={response.status_code}, body={response.text[:200]}")
                return JsonResponse({
                    'success': False,
                    'error': 'Erro ao processar mensagem no n8n'
                }, status=500)

        except requests.exceptions.Timeout:
            logger.error(f"Timeout ao encaminhar para n8n: empresa={empresa.nome}")
            return JsonResponse({
                'success': False,
                'error': 'Timeout ao processar mensagem'
            }, status=504)
        except requests.exceptions.RequestException as e:
            logger.error(f"Erro de conexão com n8n: {str(e)}")
            return JsonResponse({
                'success': False,
                'error': 'Erro de conexão com sistema de processamento'
            }, status=500)

    except Exception as e:
        logger.error(f"Erro inesperado no webhook: {str(e)}", exc_info=True)
        return JsonResponse({
            'success': False,
            'error': 'Erro interno do servidor'
        }, status=500)


# ==========================================
# HORÁRIOS DE FUNCIONAMENTO
# ==========================================

@login_required
def horarios_funcionamento(request):
    """
    Gerencia horários de funcionamento da empresa.
    Exibe todos os 7 dias da semana e permite editar cada um.
    """
    from datetime import time

    empresa = request.user.empresa

    DIAS_SEMANA = [
        (0, 'Segunda-feira'),
        (1, 'Terça-feira'),
        (2, 'Quarta-feira'),
        (3, 'Quinta-feira'),
        (4, 'Sexta-feira'),
        (5, 'Sábado'),
        (6, 'Domingo'),
    ]

    if request.method == 'POST':
        # Processar formulário
        for dia_num, dia_nome in DIAS_SEMANA:
            ativo = request.POST.get(f'ativo_{dia_num}') == 'on'
            hora_abertura = request.POST.get(f'abertura_{dia_num}')
            hora_fechamento = request.POST.get(f'fechamento_{dia_num}')
            intervalo_inicio = request.POST.get(f'intervalo_inicio_{dia_num}') or None
            intervalo_fim = request.POST.get(f'intervalo_fim_{dia_num}') or None

            if ativo and hora_abertura and hora_fechamento:
                # Criar ou atualizar horário
                HorarioFuncionamento.objects.update_or_create(
                    empresa=empresa,
                    dia_semana=dia_num,
                    defaults={
                        'hora_abertura': hora_abertura,
                        'hora_fechamento': hora_fechamento,
                        'intervalo_inicio': intervalo_inicio if intervalo_inicio else None,
                        'intervalo_fim': intervalo_fim if intervalo_fim else None,
                        'ativo': True,
                    }
                )
            else:
                # Desativar ou remover horário do dia
                HorarioFuncionamento.objects.filter(
                    empresa=empresa,
                    dia_semana=dia_num
                ).update(ativo=False)

        messages.success(request, 'Horários de funcionamento atualizados com sucesso!')
        return redirect('horarios_funcionamento')

    # Buscar horários existentes
    horarios_existentes = {
        h.dia_semana: h
        for h in HorarioFuncionamento.objects.filter(empresa=empresa)
    }

    # Montar lista de dias com horários
    dias = []
    for dia_num, dia_nome in DIAS_SEMANA:
        horario = horarios_existentes.get(dia_num)
        dias.append({
            'numero': dia_num,
            'nome': dia_nome,
            'ativo': horario.ativo if horario else False,
            'abertura': horario.hora_abertura.strftime('%H:%M') if horario and horario.hora_abertura else '09:00',
            'fechamento': horario.hora_fechamento.strftime('%H:%M') if horario and horario.hora_fechamento else '18:00',
            'intervalo_inicio': horario.intervalo_inicio.strftime('%H:%M') if horario and horario.intervalo_inicio else '',
            'intervalo_fim': horario.intervalo_fim.strftime('%H:%M') if horario and horario.intervalo_fim else '',
        })

    context = {
        'empresa': empresa,
        'dias': dias,
    }

    return render(request, 'configuracoes/horarios_funcionamento.html', context)


@login_required
def datas_especiais_lista(request):
    """Lista datas especiais (feriados e horários diferenciados)"""
    empresa = request.user.empresa
    datas = DataEspecial.objects.filter(empresa=empresa).order_by('data')

    context = {
        'empresa': empresa,
        'datas': datas,
    }

    return render(request, 'configuracoes/datas_especiais_lista.html', context)


@login_required
def data_especial_criar(request):
    """Cria nova data especial"""
    empresa = request.user.empresa

    if request.method == 'POST':
        data = request.POST.get('data')
        descricao = request.POST.get('descricao')
        tipo = request.POST.get('tipo', 'feriado')
        hora_abertura = request.POST.get('hora_abertura') or None
        hora_fechamento = request.POST.get('hora_fechamento') or None

        DataEspecial.objects.create(
            empresa=empresa,
            data=data,
            descricao=descricao,
            tipo=tipo,
            hora_abertura=hora_abertura if tipo == 'especial' else None,
            hora_fechamento=hora_fechamento if tipo == 'especial' else None,
        )

        messages.success(request, f'Data especial "{descricao}" adicionada!')
        return redirect('datas_especiais_lista')

    context = {
        'empresa': empresa,
    }

    return render(request, 'configuracoes/data_especial_form.html', context)


@login_required
def data_especial_editar(request, pk):
    """Edita data especial"""
    empresa = request.user.empresa
    data_especial = get_object_or_404(DataEspecial, pk=pk, empresa=empresa)

    if request.method == 'POST':
        data_especial.data = request.POST.get('data')
        data_especial.descricao = request.POST.get('descricao')
        data_especial.tipo = request.POST.get('tipo', 'feriado')

        if data_especial.tipo == 'especial':
            data_especial.hora_abertura = request.POST.get('hora_abertura') or None
            data_especial.hora_fechamento = request.POST.get('hora_fechamento') or None
        else:
            data_especial.hora_abertura = None
            data_especial.hora_fechamento = None

        data_especial.save()

        messages.success(request, f'Data especial "{data_especial.descricao}" atualizada!')
        return redirect('datas_especiais_lista')

    context = {
        'empresa': empresa,
        'data_especial': data_especial,
    }

    return render(request, 'configuracoes/data_especial_form.html', context)


@login_required
def data_especial_deletar(request, pk):
    """Deleta data especial"""
    empresa = request.user.empresa
    data_especial = get_object_or_404(DataEspecial, pk=pk, empresa=empresa)

    if request.method == 'POST':
        descricao = data_especial.descricao
        data_especial.delete()
        messages.success(request, f'Data especial "{descricao}" removida!')
        return redirect('datas_especiais_lista')

    context = {
        'empresa': empresa,
        'data_especial': data_especial,
    }

    return render(request, 'configuracoes/data_especial_confirmar_delete.html', context)