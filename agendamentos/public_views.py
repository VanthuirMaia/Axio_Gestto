"""
Views públicas de agendamento (sem autenticação)
Permite que clientes finais agendem serviços diretamente pelo site
"""
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.db import transaction
from django.db.models import Q
from datetime import datetime, timedelta, time
from empresas.models import Empresa, Servico, Profissional, HorarioFuncionamento
from clientes.models import Cliente
from .models import Agendamento


def agendamento_publico(request, slug):
    """
    Página pública de agendamento
    URL: /agendar/{empresa-slug}/
    """
    import logging
    logger = logging.getLogger(__name__)
    
    try:
        logger.info(f'Acesso à página de agendamento público - slug: {slug}')
        
        # Buscar empresa pelo slug
        try:
            empresa = Empresa.objects.get(slug=slug, ativa=True)
            logger.info(f'Empresa encontrada: {empresa.nome} (ID: {empresa.id})')
        except Empresa.DoesNotExist:
            logger.warning(f'Empresa não encontrada ou inativa - slug: {slug}')
            return render(request, 'agendamentos/publico/empresa_indisponivel.html', {
                'empresa': None,
                'motivo': 'nao_encontrada',
                'slug': slug
            }, status=404)

        # Verificar se onboarding está completo
        if not empresa.onboarding_completo:
            logger.info(f'Empresa {empresa.nome} - onboarding não completo')
            return render(request, 'agendamentos/publico/empresa_indisponivel.html', {
                'empresa': empresa,
                'motivo': 'configuracao'
            })

        # Buscar serviços ativos
        servicos = empresa.servicos.filter(ativo=True).order_by('nome')
        logger.info(f'Empresa {empresa.nome} - {servicos.count()} serviços ativos')

        if not servicos.exists():
            logger.warning(f'Empresa {empresa.nome} - sem serviços ativos')
            return render(request, 'agendamentos/publico/empresa_indisponivel.html', {
                'empresa': empresa,
                'motivo': 'sem_servicos'
            })

        context = {
            'empresa': empresa,
            'servicos': servicos,
            'hoje': timezone.now().date().isoformat(),  # formato YYYY-MM-DD para input date
        }

        logger.info(f'Renderizando página de agendamento para {empresa.nome}')
        return render(request, 'agendamentos/publico/agendar.html', context)
        
    except Exception as e:
        logger.error(f'Erro inesperado na view agendamento_publico - slug: {slug}')
        logger.error(f'Tipo de erro: {type(e).__name__}')
        logger.error(f'Mensagem: {str(e)}')
        logger.exception('Stack trace completo:')
        
        # Retornar página de erro genérica em vez de 500/503
        return render(request, 'agendamentos/publico/empresa_indisponivel.html', {
            'empresa': None,
            'motivo': 'erro_sistema',
            'slug': slug
        }, status=500)


@require_http_methods(["GET"])
def api_profissionais_por_servico(request, slug):
    """
    API: Retorna profissionais que executam um serviço específico
    GET /agendar/{slug}/api/profissionais/?servico_id=123
    """
    empresa = get_object_or_404(Empresa, slug=slug, ativo=True)
    servico_id = request.GET.get('servico_id')

    if not servico_id:
        return JsonResponse({'error': 'servico_id obrigatório'}, status=400)

    servico = get_object_or_404(Servico, id=servico_id, empresa=empresa, ativo=True)

    # Buscar profissionais que executam este serviço
    profissionais = servico.profissionais.filter(ativo=True).values(
        'id', 'nome', 'email', 'cor_hex'
    )

    return JsonResponse({
        'profissionais': list(profissionais),
        'servico': {
            'id': servico.id,
            'nome': servico.nome,
            'preco': float(servico.preco),
            'duracao_minutos': servico.duracao_minutos
        }
    })


@require_http_methods(["POST"])
def api_horarios_disponiveis(request, slug):
    """
    API: Retorna horários disponíveis para agendamento
    POST /agendar/{slug}/api/horarios-disponiveis/

    Body: {
        "servico_id": 123,
        "profissional_id": 456,
        "data": "2025-01-15"
    }
    """
    import json

    empresa = get_object_or_404(Empresa, slug=slug, ativo=True)

    try:
        data = json.loads(request.body)
        servico_id = data.get('servico_id')
        profissional_id = data.get('profissional_id')
        data_str = data.get('data')  # formato: YYYY-MM-DD

        if not all([servico_id, profissional_id, data_str]):
            return JsonResponse({'error': 'Dados incompletos'}, status=400)

        servico = get_object_or_404(Servico, id=servico_id, empresa=empresa)
        profissional = get_object_or_404(Profissional, id=profissional_id, empresa=empresa)
        data_agendamento = datetime.strptime(data_str, '%Y-%m-%d').date()

        # Não permitir agendamentos no passado
        if data_agendamento < timezone.now().date():
            return JsonResponse({'horarios': []})

        # Buscar horário de funcionamento para este dia da semana
        dia_semana = data_agendamento.weekday()  # 0=segunda, 6=domingo
        horario_func = HorarioFuncionamento.objects.filter(
            empresa=empresa,
            dia_semana=dia_semana,
            ativo=True
        ).first()

        if not horario_func:
            return JsonResponse({'horarios': []})

        # Gerar slots de horários disponíveis
        horarios_disponiveis = _gerar_slots_disponiveis(
            empresa=empresa,
            profissional=profissional,
            servico=servico,
            data=data_agendamento,
            hora_abertura=horario_func.hora_abertura,
            hora_fechamento=horario_func.hora_fechamento
        )

        return JsonResponse({'horarios': horarios_disponiveis})

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def _gerar_slots_disponiveis(empresa, profissional, servico, data, hora_abertura, hora_fechamento):
    """
    Gera lista de horários disponíveis considerando:
    - Horário de funcionamento
    - Agendamentos existentes
    - Duração do serviço
    """
    slots = []
    duracao_minutos = servico.duracao_minutos

    # Converter para datetime
    dt_atual = datetime.combine(data, hora_abertura)
    dt_fim_dia = datetime.combine(data, hora_fechamento)

    # Se for hoje, não mostrar horários que já passaram
    agora = timezone.now()
    if data == agora.date():
        hora_minima = agora + timedelta(hours=1)  # Mínimo 1h de antecedência
        if dt_atual < hora_minima:
            dt_atual = hora_minima.replace(minute=0, second=0, microsecond=0)
            # Arredondar para próxima hora cheia ou meia hora
            if hora_minima.minute > 30:
                dt_atual = dt_atual + timedelta(hours=1)
            elif hora_minima.minute > 0:
                dt_atual = dt_atual.replace(minute=30)

    # Gerar slots de 30 em 30 minutos
    while dt_atual + timedelta(minutes=duracao_minutos) <= dt_fim_dia:
        dt_fim_slot = dt_atual + timedelta(minutes=duracao_minutos)

        # Verificar se há conflito com agendamentos existentes
        conflito = Agendamento.objects.filter(
            empresa=empresa,
            profissional=profissional,
            data_hora_inicio__lt=dt_fim_slot,
            data_hora_fim__gt=dt_atual,
            status__in=['pendente', 'confirmado']
        ).exists()

        if not conflito:
            slots.append({
                'hora': dt_atual.strftime('%H:%M'),
                'datetime': dt_atual.isoformat()
            })

        # Avançar 30 minutos
        dt_atual += timedelta(minutes=30)

    return slots


@require_http_methods(["POST"])
@csrf_exempt  # Permitir POST de formulário público
def confirmar_agendamento(request, slug):
    """
    Confirma o agendamento público
    POST /agendar/{slug}/confirmar/
    """
    import json

    empresa = get_object_or_404(Empresa, slug=slug, ativo=True)

    try:
        # Aceitar tanto JSON quanto form data
        if request.content_type == 'application/json':
            data = json.loads(request.body)
        else:
            data = request.POST.dict()

        # Extrair dados
        servico_id = data.get('servico_id')
        profissional_id = data.get('profissional_id')
        data_hora_str = data.get('data_hora')  # ISO format

        # Dados do cliente
        cliente_nome = data.get('cliente_nome', '').strip()
        cliente_telefone = data.get('cliente_telefone', '').strip()
        cliente_email = data.get('cliente_email', '').strip()
        notas = data.get('notas', '').strip()

        # Validações
        if not all([servico_id, profissional_id, data_hora_str, cliente_nome, cliente_telefone]):
            return JsonResponse({
                'success': False,
                'error': 'Preencha todos os campos obrigatórios'
            }, status=400)

        # Buscar ou criar cliente
        cliente, created = Cliente.objects.get_or_create(
            empresa=empresa,
            telefone=cliente_telefone,
            defaults={
                'nome': cliente_nome,
                'email': cliente_email,
                'origem': 'site',
                'ativo': True
            }
        )

        # Se cliente já existe, atualizar dados
        if not created:
            cliente.nome = cliente_nome
            if cliente_email:
                cliente.email = cliente_email
            cliente.save()

        # Buscar serviço e profissional
        servico = get_object_or_404(Servico, id=servico_id, empresa=empresa)
        profissional = get_object_or_404(Profissional, id=profissional_id, empresa=empresa)

        # Parse data/hora
        data_hora_inicio = datetime.fromisoformat(data_hora_str.replace('Z', '+00:00'))
        data_hora_inicio = timezone.make_aware(data_hora_inicio) if timezone.is_naive(data_hora_inicio) else data_hora_inicio
        data_hora_fim = data_hora_inicio + timedelta(minutes=servico.duracao_minutos)

        # Verificar conflito com proteção contra race condition
        with transaction.atomic():
            # Lock pessimista: bloqueia outros agendamentos durante a verificação
            conflito = Agendamento.objects.select_for_update().filter(
                empresa=empresa,
                profissional=profissional,
                data_hora_inicio__lt=data_hora_fim,
                data_hora_fim__gt=data_hora_inicio,
                status__in=['pendente', 'confirmado']
            ).exists()

            if conflito:
                return JsonResponse({
                    'success': False,
                    'error': 'Este horário acabou de ser reservado. Por favor, escolha outro.'
                }, status=409)

            # Criar agendamento (dentro da transação, lock ainda ativo)
            agendamento = Agendamento.objects.create(
                empresa=empresa,
                cliente=cliente,
                servico=servico,
                profissional=profissional,
                data_hora_inicio=data_hora_inicio,
                data_hora_fim=data_hora_fim,
                notas=notas,
                valor_cobrado=servico.preco,
                status='pendente',  # Aguardando confirmação da empresa
                origem='site'
            )

        # TODO: Enviar notificação para empresa (email/WhatsApp)
        # TODO: Enviar confirmação para cliente (email/SMS)

        return JsonResponse({
            'success': True,
            'mensagem': 'Agendamento realizado com sucesso!',
            'agendamento': {
                'id': agendamento.id,
                'data_hora': agendamento.data_hora_inicio.strftime('%d/%m/%Y às %H:%M'),
                'servico': servico.nome,
                'profissional': profissional.nome,
                'valor': float(servico.preco)
            }
        })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Erro ao criar agendamento: {str(e)}'
        }, status=500)
