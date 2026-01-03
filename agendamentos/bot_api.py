"""
API para integração com n8n (Bot WhatsApp)
Todas as requisições vindas do n8n passam por aqui
"""

from rest_framework.decorators import api_view, authentication_classes, permission_classes, throttle_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.utils.timezone import now, make_aware
from django.utils.dateparse import parse_datetime, parse_date
from django.db import transaction
from datetime import datetime, timedelta, time
from django.db.models import Q
from django.core.exceptions import ValidationError
from django.views.decorators.csrf import csrf_exempt

from .models import Agendamento, LogMensagemBot
from clientes.models import Cliente
from empresas.models import Servico, Profissional, Empresa
from .authentication import APIKeyAuthentication
from .throttling import BotAPIThrottle


@api_view(['POST'])
@authentication_classes([APIKeyAuthentication])
@permission_classes([AllowAny])
@throttle_classes([BotAPIThrottle])
def processar_comando_bot(request):
    """
    Endpoint central que recebe comandos interpretados pela IA

    n8n envia:
    {
        "telefone": "5511999998888",
        "mensagem_original": "Quero agendar corte amanhã 14h",
        "intencao": "agendar",  // ou "cancelar", "consultar", etc
        "dados": {
            "servico": "corte de cabelo",
            "data": "2025-12-23",
            "hora": "14:00",
            "profissional": "João"  // opcional
        }
    }

    Django retorna:
    {
        "sucesso": true,
        "mensagem": "Agendamento criado com sucesso! Código: ABC123",
        "dados": {
            "agendamento_id": 123,
            "codigo": "ABC123",
            "data_hora": "23/12/2025 às 14:00",
            ...
        }
    }
    """

    # Extrair dados da requisição
    telefone = request.data.get('telefone')
    mensagem_original = request.data.get('mensagem_original', '')
    intencao = request.data.get('intencao')
    dados = request.data.get('dados', {})
    empresa = request.empresa  # Vem da autenticação

    # Criar log da interação
    log = LogMensagemBot.objects.create(
        empresa=empresa,
        telefone=telefone,
        mensagem_original=mensagem_original,
        intencao_detectada=intencao,
        dados_extraidos=dados,
        status='parcial'  # Será atualizado no final
    )

    try:
        # Roteamento por intenção
        if intencao == 'agendar':
            resultado = processar_agendamento(empresa, telefone, dados, log)

        elif intencao == 'cancelar':
            resultado = processar_cancelamento(empresa, telefone, dados, log)

        elif intencao == 'consultar':
            resultado = processar_consulta(empresa, telefone, dados, log)

        elif intencao == 'confirmar':
            resultado = processar_confirmacao(empresa, telefone, dados, log)

        else:
            resultado = {
                'sucesso': False,
                'mensagem': 'Desculpe, não entendi o que você quer fazer. Pode reformular?'
            }

        # Atualizar log
        log.status = 'sucesso' if resultado['sucesso'] else 'erro'
        log.resposta_enviada = resultado['mensagem']
        log.save()

        return Response(resultado)

    except Exception as e:
        # Registrar erro
        log.status = 'erro'
        log.erro_detalhes = str(e)
        log.resposta_enviada = 'Ops! Algo deu errado. Tente novamente ou entre em contato.'
        log.save()

        return Response({
            'sucesso': False,
            'mensagem': 'Desculpe, ocorreu um erro ao processar sua solicitação.',
            'erro': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def processar_agendamento(empresa, telefone, dados, log):
    """
    Processa solicitação de agendamento

    dados = {
        "servico": "corte de cabelo",
        "data": "2025-12-23",  // YYYY-MM-DD
        "hora": "14:00",  // HH:MM
        "profissional": "João"  // opcional
    }
    """

    # 1. Buscar ou criar cliente
    cliente = buscar_ou_criar_cliente(empresa, telefone, dados)

    # 2. Buscar serviço
    nome_servico = dados.get('servico', '').lower()
    servico = Servico.objects.filter(
        empresa=empresa,
        nome__icontains=nome_servico,
        ativo=True
    ).first()

    if not servico:
        return {
            'sucesso': False,
            'mensagem': f'Não encontrei o serviço "{dados.get("servico")}". '
                       f'Serviços disponíveis: {listar_servicos(empresa)}'
        }

    # 3. Buscar profissional (se especificado)
    profissional = None
    if dados.get('profissional'):
        nome_prof = dados['profissional'].lower()
        profissional = Profissional.objects.filter(
            empresa=empresa,
            nome__icontains=nome_prof,
            ativo=True
        ).first()

        if not profissional:
            return {
                'sucesso': False,
                'mensagem': f'Profissional "{dados["profissional"]}" não encontrado. '
                           f'Disponíveis: {listar_profissionais(empresa)}'
            }
    else:
        # Pegar primeiro profissional disponível
        profissional = Profissional.objects.filter(
            empresa=empresa,
            ativo=True
        ).first()

    # 4. Montar data/hora
    try:
        data_str = dados.get('data')
        hora_str = dados.get('hora')

        # Converte data
        data = parse_date(data_str)
        if not data:
            raise ValueError("Data inválida")

        # Converte hora
        hora_parts = hora_str.split(':')
        hora = time(int(hora_parts[0]), int(hora_parts[1]))

        # Combina data + hora
        data_hora_inicio = make_aware(datetime.combine(data, hora))
        data_hora_fim = data_hora_inicio + timedelta(minutes=servico.duracao_minutos)

    except Exception as e:
        return {
            'sucesso': False,
            'mensagem': f'Data/hora inválida: {e}. Use formato: data=AAAA-MM-DD, hora=HH:MM'
        }

    # 5. Verificar se data/hora já passou
    if data_hora_inicio < now():
        return {
            'sucesso': False,
            'mensagem': 'Não é possível agendar para o passado! Escolha uma data futura.'
        }

    # 6. Verificar disponibilidade e criar agendamento (com proteção contra race condition)
    codigo = gerar_codigo_agendamento()

    with transaction.atomic():
        # Lock pessimista: bloqueia outros agendamentos durante a verificação
        conflitos = Agendamento.objects.select_for_update().filter(
            empresa=empresa,
            profissional=profissional,
            data_hora_inicio__lt=data_hora_fim,
            data_hora_fim__gt=data_hora_inicio,
            status__in=['pendente', 'confirmado']
        )

        if conflitos.exists():
            # Buscar horários alternativos
            horarios_alt = buscar_horarios_alternativos(
                empresa,
                profissional,
                data,
                servico.duracao_minutos
            )

            return {
                'sucesso': False,
                'mensagem': f'Este horário já está ocupado! 😔\n\n'
                           f'Horários disponíveis para {data.strftime("%d/%m/%Y")}:\n'
                           f'{formatar_horarios(horarios_alt)}',
                'horarios_alternativos': horarios_alt
            }

        # 7. Criar agendamento (dentro da transação, lock ainda ativo)
        agendamento = Agendamento.objects.create(
            empresa=empresa,
            cliente=cliente,
            servico=servico,
            profissional=profissional,
            data_hora_inicio=data_hora_inicio,
            data_hora_fim=data_hora_fim,
            status='pendente',
            valor_cobrado=servico.preco,
            notas=f'Agendado via WhatsApp. Código: {codigo}'
        )

        # Vincular log ao agendamento
        log.agendamento = agendamento
        log.save()

    # 8. Retornar sucesso
    return {
        'sucesso': True,
        'mensagem': f'✅ Agendamento confirmado!\n\n'
                   f'📅 Serviço: {servico.nome}\n'
                   f'👤 Profissional: {profissional.nome}\n'
                   f'🕐 Data: {data_hora_inicio.strftime("%d/%m/%Y às %H:%M")}\n'
                   f'💰 Valor: R$ {servico.preco}\n'
                   f'📝 Código: {codigo}\n\n'
                   f'Para cancelar: CANCELAR {codigo}',
        'dados': {
            'agendamento_id': agendamento.id,
            'codigo': codigo,
            'data_hora': data_hora_inicio.strftime("%d/%m/%Y às %H:%M"),
            'valor': float(servico.preco)
        }
    }


def processar_cancelamento(empresa, telefone, dados, log):
    """
    Cancela agendamento por código

    dados = {
        "codigo": "ABC123"
    }
    """
    codigo = dados.get('codigo', '').upper()

    if not codigo:
        return {
            'sucesso': False,
            'mensagem': 'Por favor, informe o código do agendamento para cancelar.'
        }

    # Buscar agendamento pelo código (na descrição/notas)
    agendamento = Agendamento.objects.filter(
        empresa=empresa,
        notas__contains=codigo,
        status__in=['pendente', 'confirmado']
    ).first()

    if not agendamento:
        return {
            'sucesso': False,
            'mensagem': f'Não encontrei agendamento com código {codigo}. '
                       f'Verifique se digitou corretamente.'
        }

    # Verificar se é do mesmo telefone (segurança básica)
    if agendamento.cliente.telefone.replace('+55', '').replace(' ', '') != telefone.replace('+55', '').replace(' ', ''):
        return {
            'sucesso': False,
            'mensagem': 'Este agendamento não pertence a você!'
        }

    # Cancelar
    agendamento.status = 'cancelado'
    agendamento.save()

    log.agendamento = agendamento
    log.save()

    return {
        'sucesso': True,
        'mensagem': f'✅ Agendamento cancelado com sucesso!\n\n'
                   f'Código: {codigo}\n'
                   f'Data: {agendamento.data_hora_inicio.strftime("%d/%m/%Y às %H:%M")}\n\n'
                   f'Esperamos você em breve! 😊'
    }


def processar_consulta(empresa, telefone, dados, log):
    """
    Consulta horários disponíveis

    dados = {
        "data": "2025-12-23",  // opcional
        "profissional": "João"  // opcional
    }
    """
    # Se não especificou data, mostra de hoje em diante
    if dados.get('data'):
        data = parse_date(dados['data'])
    else:
        data = now().date()

    # Buscar profissional
    profissional = None
    if dados.get('profissional'):
        profissional = Profissional.objects.filter(
            empresa=empresa,
            nome__icontains=dados['profissional'],
            ativo=True
        ).first()

    # Buscar horários disponíveis
    horarios = buscar_horarios_disponiveis_dia(empresa, data, profissional)

    if not horarios:
        return {
            'sucesso': True,
            'mensagem': f'😔 Não há horários disponíveis para {data.strftime("%d/%m/%Y")}.\n\n'
                       f'Tente outra data!'
        }

    return {
        'sucesso': True,
        'mensagem': f'📅 Horários disponíveis em {data.strftime("%d/%m/%Y")}:\n\n'
                   f'{formatar_horarios(horarios)}\n\n'
                   f'Para agendar, diga: "Quero agendar [serviço] às [hora]"',
        'horarios': horarios
    }


def processar_confirmacao(empresa, telefone, dados, log):
    """
    Confirma agendamento pendente

    dados = {
        "codigo": "ABC123"
    }
    """
    codigo = dados.get('codigo', '').upper()

    agendamento = Agendamento.objects.filter(
        empresa=empresa,
        notas__contains=codigo,
        status='pendente'
    ).first()

    if not agendamento:
        return {
            'sucesso': False,
            'mensagem': 'Agendamento não encontrado ou já confirmado.'
        }

    agendamento.status = 'confirmado'
    agendamento.save()

    return {
        'sucesso': True,
        'mensagem': f'✅ Agendamento confirmado!\n\n'
                   f'Te esperamos em {agendamento.data_hora_inicio.strftime("%d/%m/%Y às %H:%M")}!'
    }


# ============================================
# WEBHOOK MULTI-TENANT (SAAS)
# ============================================

@api_view(['POST'])
@permission_classes([AllowAny])
@csrf_exempt
def whatsapp_webhook_saas(request):
    """
    Endpoint público multi-tenant para webhooks WhatsApp

    Detecta automaticamente o tenant (empresa) baseado no instance_id
    ou número de telefone da Evolution API / Z-API

    Payload esperado (Evolution API):
    {
        "instance": "empresa123",  // whatsapp_instance_id da empresa
        "event": "messages.upsert",
        "data": {
            "key": {
                "remoteJid": "5511999998888@s.whatsapp.net",
                "fromMe": false,
                "id": "..."
            },
            "message": {
                "conversation": "Quero agendar corte amanhã 14h"
            },
            "pushName": "João Silva"
        }
    }

    Payload esperado (n8n processado):
    {
        "instance": "empresa123",
        "telefone": "5511999998888",
        "mensagem_original": "Quero agendar corte amanhã 14h",
        "intencao": "agendar",
        "dados": {...}
    }
    """

    try:
        # 1. Extrair instance ID
        instance_id = request.data.get('instance') or request.data.get('instanceId')

        if not instance_id:
            return Response({
                'sucesso': False,
                'erro': 'Instance ID não fornecido. Envie campo "instance" no payload.'
            }, status=status.HTTP_400_BAD_REQUEST)

        # 2. Buscar empresa por instance_id
        try:
            empresa = Empresa.objects.get(
                whatsapp_instance_id=instance_id,
                ativa=True,
                whatsapp_conectado=True
            )
        except Empresa.DoesNotExist:
            return Response({
                'sucesso': False,
                'erro': f'Nenhuma empresa encontrada para instance "{instance_id}". '
                       'Verifique a configuração no painel de onboarding.'
            }, status=status.HTTP_404_NOT_FOUND)

        # 3. Verificar status da assinatura (CRÍTICO PARA SAAS)
        if not hasattr(empresa, 'assinatura'):
            return Response({
                'sucesso': False,
                'erro': 'Empresa sem assinatura ativa. Configure um plano.'
            }, status=status.HTTP_402_PAYMENT_REQUIRED)

        assinatura = empresa.assinatura

        # Bloquear se assinatura não está ativa ou em trial
        if assinatura.status not in ['ativa', 'trial']:
            return Response({
                'sucesso': False,
                'erro': f'Assinatura {assinatura.status}. Regularize o pagamento para continuar.',
                'status_assinatura': assinatura.status,
                'plano': assinatura.plano.nome
            }, status=status.HTTP_402_PAYMENT_REQUIRED)

        # 4. Verificar se assinatura expirou
        if assinatura.data_expiracao and assinatura.data_expiracao < now():
            # Suspender automaticamente
            assinatura.status = 'suspensa'
            assinatura.save()

            return Response({
                'sucesso': False,
                'erro': 'Assinatura expirada. Renove para continuar usando o bot.',
                'data_expiracao': assinatura.data_expiracao.strftime('%d/%m/%Y')
            }, status=status.HTTP_402_PAYMENT_REQUIRED)

        # 5. Verificar limites do plano (agendamentos do mês)
        from django.utils.timezone import now as django_now
        inicio_mes = django_now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)

        agendamentos_mes = Agendamento.objects.filter(
            empresa=empresa,
            criado_em__gte=inicio_mes,
            status__in=['pendente', 'confirmado', 'concluido']
        ).count()

        if agendamentos_mes >= assinatura.plano.max_agendamentos_mes:
            return Response({
                'sucesso': False,
                'erro': f'Limite de {assinatura.plano.max_agendamentos_mes} agendamentos/mês atingido. '
                       f'Faça upgrade do plano para continuar.',
                'agendamentos_usados': agendamentos_mes,
                'limite': assinatura.plano.max_agendamentos_mes,
                'plano_atual': assinatura.plano.nome
            }, status=status.HTTP_429_TOO_MANY_REQUESTS)

        # 6. Processar mensagem
        # Verificar se já vem processada pelo n8n (com intencao) ou se é webhook bruto
        if 'intencao' in request.data:
            # Payload já processado pelo n8n
            telefone = request.data.get('telefone')
            mensagem_original = request.data.get('mensagem_original', '')
            intencao = request.data.get('intencao')
            dados = request.data.get('dados', {})
        else:
            # Webhook bruto - retornar para n8n processar
            # Apenas validamos e retornamos OK para n8n continuar o fluxo
            return Response({
                'sucesso': True,
                'mensagem': 'Webhook recebido. Empresa validada.',
                'empresa_id': empresa.id,
                'empresa_nome': empresa.nome,
                'assinatura_status': assinatura.status,
                'plano': assinatura.plano.nome
            }, status=status.HTTP_200_OK)

        # 7. Criar log da interação
        log = LogMensagemBot.objects.create(
            empresa=empresa,
            telefone=telefone,
            mensagem_original=mensagem_original,
            intencao_detectada=intencao,
            dados_extraidos=dados,
            status='parcial'
        )

        # 8. Rotear para lógica de processamento existente
        try:
            if intencao == 'agendar':
                resultado = processar_agendamento(empresa, telefone, dados, log)

            elif intencao == 'cancelar':
                resultado = processar_cancelamento(empresa, telefone, dados, log)

            elif intencao == 'consultar':
                resultado = processar_consulta(empresa, telefone, dados, log)

            elif intencao == 'confirmar':
                resultado = processar_confirmacao(empresa, telefone, dados, log)

            else:
                resultado = {
                    'sucesso': False,
                    'mensagem': 'Desculpe, não entendi o que você quer fazer. Pode reformular?'
                }

            # Atualizar log
            log.status = 'sucesso' if resultado['sucesso'] else 'erro'
            log.resposta_enviada = resultado['mensagem']
            log.save()

            return Response(resultado)

        except Exception as e:
            # Registrar erro
            log.status = 'erro'
            log.erro_detalhes = str(e)
            log.resposta_enviada = 'Ops! Algo deu errado. Tente novamente.'
            log.save()

            return Response({
                'sucesso': False,
                'mensagem': 'Desculpe, ocorreu um erro ao processar sua solicitação.',
                'erro': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    except Exception as e:
        # Erro não tratado
        return Response({
            'sucesso': False,
            'erro': f'Erro interno: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ============================================
# FUNÇÕES AUXILIARES
# ============================================

def buscar_ou_criar_cliente(empresa, telefone, dados):
    """Busca cliente por telefone ou cria novo"""
    telefone_limpo = telefone.replace('+55', '').replace(' ', '').replace('-', '')

    cliente = Cliente.objects.filter(
        empresa=empresa,
        telefone__contains=telefone_limpo
    ).first()

    if not cliente:
        # Criar novo cliente
        nome = dados.get('nome_cliente', 'Cliente WhatsApp')
        cliente = Cliente.objects.create(
            empresa=empresa,
            nome=nome,
            telefone=telefone,
            origem='whatsapp',
            ativo=True
        )

    return cliente


def gerar_codigo_agendamento():
    """Gera código alfanumérico único"""
    import random
    import string
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))


def buscar_horarios_alternativos(empresa, profissional, data, duracao_minutos, limite=5):
    """Busca próximos horários livres no mesmo dia"""
    horarios = []
    hora_atual = time(8, 0)  # Começar às 8h
    hora_limite = time(18, 0)  # Até 18h

    while hora_atual < hora_limite and len(horarios) < limite:
        data_hora = make_aware(datetime.combine(data, hora_atual))
        data_hora_fim = data_hora + timedelta(minutes=duracao_minutos)

        # Verificar se está livre
        ocupado = Agendamento.objects.filter(
            empresa=empresa,
            profissional=profissional,
            data_hora_inicio__lt=data_hora_fim,
            data_hora_fim__gt=data_hora,
            status__in=['pendente', 'confirmado']
        ).exists()

        if not ocupado:
            horarios.append(hora_atual.strftime('%H:%M'))

        # Próximo slot (30 em 30 minutos)
        hora_atual = (datetime.combine(data, hora_atual) + timedelta(minutes=30)).time()

    return horarios


def buscar_horarios_disponiveis_dia(empresa, data, profissional=None):
    """Retorna todos os horários livres de um dia"""
    return buscar_horarios_alternativos(empresa, profissional, data, 30, limite=20)


def formatar_horarios(horarios):
    """Formata lista de horários para exibição"""
    if not horarios:
        return "Nenhum horário disponível"

    # Agrupar de 3 em 3
    linhas = []
    for i in range(0, len(horarios), 3):
        grupo = horarios[i:i+3]
        linhas.append('  '.join([f'🕐 {h}' for h in grupo]))

    return '\n'.join(linhas)


def listar_servicos(empresa):
    """Lista serviços disponíveis"""
    servicos = Servico.objects.filter(empresa=empresa, ativo=True)
    return ', '.join([s.nome for s in servicos])


def listar_profissionais(empresa):
    """Lista profissionais disponíveis"""
    profissionais = Profissional.objects.filter(empresa=empresa, ativo=True)
    return ', '.join([p.nome for p in profissionais])
