from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.timezone import now
from django.conf import settings
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
    Cria instância e retorna QR Code (AJAX)
    """
    from django.http import JsonResponse
    from empresas.models import ConfiguracaoWhatsApp
    from empresas.services import EvolutionAPIService

    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Método não permitido'}, status=405)

    empresa = request.user.empresa
    config = ConfiguracaoWhatsApp.objects.get(empresa=empresa)

    # Criar service
    service = EvolutionAPIService(config)

    # Criar instância
    result = service.criar_instancia()

    if not result['success']:
        return JsonResponse({
            'success': False,
            'error': result.get('error', 'Erro ao criar instância')
        })

    # Obter QR Code
    qr_result = service.obter_qrcode()

    if qr_result['success']:
        return JsonResponse({
            'success': True,
            'qrcode': qr_result['qrcode'],
            'status': config.status,
            'instance_name': config.instance_name
        })
    else:
        return JsonResponse({
            'success': False,
            'error': 'Instância criada mas QR Code não disponível. Tente novamente.'
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