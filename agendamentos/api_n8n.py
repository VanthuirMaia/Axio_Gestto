"""
APIs para integração com n8n
Substituem as consultas ao Google Sheets
"""

from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.utils.dateparse import parse_date
from django.utils.timezone import make_aware
from datetime import datetime, timedelta, time

from empresas.models import Servico, Profissional, HorarioFuncionamento, DataEspecial, Empresa
from agendamentos.models import Agendamento
from .authentication import APIKeyAuthentication


@api_view(['GET'])
@authentication_classes([APIKeyAuthentication])
@permission_classes([AllowAny])
def listar_servicos(request):
    """
    Lista todos os serviços ativos da empresa

    GET /api/n8n/servicos/

    Response:
    {
        "sucesso": true,
        "servicos": [
            {
                "id": 1,
                "nome": "Corte de Cabelo",
                "descricao": "Corte masculino tradicional",
                "preco": "40.00",
                "duracao_minutos": 30
            },
            ...
        ]
    }
    """
    empresa = request.empresa  # Vem da autenticação

    servicos = Servico.objects.filter(
        empresa=empresa,
        ativo=True
    ).order_by('nome')

    dados_servicos = [
        {
            'id': s.id,
            'nome': s.nome,
            'descricao': s.descricao,
            'preco': str(s.preco),
            'duracao_minutos': s.duracao_minutos
        }
        for s in servicos
    ]

    return Response({
        'sucesso': True,
        'total': len(dados_servicos),
        'servicos': dados_servicos
    })


@api_view(['GET'])
@authentication_classes([APIKeyAuthentication])
@permission_classes([AllowAny])
def listar_profissionais(request):
    """
    Lista todos os profissionais ativos da empresa

    GET /api/n8n/profissionais/

    Response:
    {
        "sucesso": true,
        "profissionais": [
            {
                "id": 1,
                "nome": "Pedro Brandão",
                "email": "pedro@barbearia.com",
                "telefone": "87999998888",
                "servicos": ["Corte", "Barba"],
                "cor_hex": "#1e3a8a"
            },
            ...
        ]
    }
    """
    empresa = request.empresa

    profissionais = Profissional.objects.filter(
        empresa=empresa,
        ativo=True
    ).prefetch_related('servicos').order_by('nome')

    dados_profissionais = [
        {
            'id': p.id,
            'nome': p.nome,
            'email': p.email,
            'telefone': p.telefone,
            'servicos': [s.nome for s in p.servicos.filter(ativo=True)],
            'cor_hex': p.cor_hex
        }
        for p in profissionais
    ]

    return Response({
        'sucesso': True,
        'total': len(dados_profissionais),
        'profissionais': dados_profissionais
    })


@api_view(['GET'])
@authentication_classes([APIKeyAuthentication])
@permission_classes([AllowAny])
def consultar_horarios_funcionamento(request):
    """
    Retorna horários de funcionamento da empresa

    GET /api/n8n/horarios-funcionamento/

    Query params:
    - dia_semana (opcional): 0-6 (0=segunda, 6=domingo)

    Response:
    {
        "sucesso": true,
        "horarios": [
            {
                "dia_semana": 0,
                "dia_semana_nome": "Segunda-feira",
                "hora_abertura": "09:00",
                "hora_fechamento": "18:00",
                "intervalo_inicio": "12:00",
                "intervalo_fim": "13:00"
            },
            ...
        ]
    }
    """
    empresa = request.empresa
    dia_semana = request.GET.get('dia_semana')

    query = HorarioFuncionamento.objects.filter(
        empresa=empresa,
        ativo=True
    )

    if dia_semana is not None:
        query = query.filter(dia_semana=int(dia_semana))

    query = query.order_by('dia_semana')

    dados_horarios = [
        {
            'dia_semana': h.dia_semana,
            'dia_semana_nome': h.get_dia_semana_display(),
            'hora_abertura': h.hora_abertura.strftime('%H:%M'),
            'hora_fechamento': h.hora_fechamento.strftime('%H:%M'),
            'intervalo_inicio': h.intervalo_inicio.strftime('%H:%M') if h.intervalo_inicio else None,
            'intervalo_fim': h.intervalo_fim.strftime('%H:%M') if h.intervalo_fim else None,
        }
        for h in query
    ]

    return Response({
        'sucesso': True,
        'total': len(dados_horarios),
        'horarios': dados_horarios
    })


@api_view(['GET'])
@authentication_classes([APIKeyAuthentication])
@permission_classes([AllowAny])
def consultar_datas_especiais(request):
    """
    Retorna datas especiais (feriados, horários diferenciados)

    GET /api/n8n/datas-especiais/

    Query params:
    - data_inicio (opcional): YYYY-MM-DD
    - data_fim (opcional): YYYY-MM-DD
    - tipo (opcional): feriado ou especial

    Response:
    {
        "sucesso": true,
        "datas_especiais": [
            {
                "data": "2025-12-25",
                "descricao": "Natal",
                "tipo": "feriado",
                "hora_abertura": null,
                "hora_fechamento": null
            },
            ...
        ]
    }
    """
    empresa = request.empresa
    data_inicio = request.GET.get('data_inicio')
    data_fim = request.GET.get('data_fim')
    tipo = request.GET.get('tipo')

    query = DataEspecial.objects.filter(empresa=empresa)

    if data_inicio:
        query = query.filter(data__gte=parse_date(data_inicio))

    if data_fim:
        query = query.filter(data__lte=parse_date(data_fim))

    if tipo:
        query = query.filter(tipo=tipo)

    query = query.order_by('data')

    dados_datas = [
        {
            'data': d.data.strftime('%Y-%m-%d'),
            'data_formatada': d.data.strftime('%d/%m/%Y'),
            'descricao': d.descricao,
            'tipo': d.tipo,
            'tipo_display': d.get_tipo_display(),
            'hora_abertura': d.hora_abertura.strftime('%H:%M') if d.hora_abertura else None,
            'hora_fechamento': d.hora_fechamento.strftime('%H:%M') if d.hora_fechamento else None,
        }
        for d in query
    ]

    return Response({
        'sucesso': True,
        'total': len(dados_datas),
        'datas_especiais': dados_datas
    })


@api_view(['POST'])
@authentication_classes([APIKeyAuthentication])
@permission_classes([AllowAny])
def consultar_horarios_disponiveis(request):
    """
    Consulta horários disponíveis para agendamento

    POST /api/n8n/horarios-disponiveis/
    {
        "data": "2025-12-23",
        "profissional_id": 1,  // opcional
        "servico_id": 2        // opcional (para calcular duração)
    }

    Response:
    {
        "sucesso": true,
        "data": "2025-12-23",
        "dia_semana": "Segunda-feira",
        "profissional": "Pedro Brandão",
        "servico": "Corte + Barba",
        "duracao_minutos": 45,
        "horarios_disponiveis": [
            "09:00",
            "09:30",
            "10:00",
            ...
        ]
    }
    """
    empresa = request.empresa
    data_str = request.data.get('data')
    profissional_id = request.data.get('profissional_id')
    servico_id = request.data.get('servico_id')

    # Validar data
    try:
        data = parse_date(data_str)
        if not data:
            raise ValueError()
    except:
        return Response({
            'sucesso': False,
            'mensagem': 'Data inválida. Use formato YYYY-MM-DD'
        }, status=status.HTTP_400_BAD_REQUEST)

    # Buscar profissional (se especificado)
    profissional = None
    if profissional_id:
        try:
            profissional = Profissional.objects.get(id=profissional_id, empresa=empresa, ativo=True)
        except Profissional.DoesNotExist:
            return Response({
                'sucesso': False,
                'mensagem': 'Profissional não encontrado'
            }, status=status.HTTP_404_NOT_FOUND)

    # Buscar serviço (para duração)
    duracao_minutos = 30  # padrão
    servico_nome = None
    if servico_id:
        try:
            servico = Servico.objects.get(id=servico_id, empresa=empresa, ativo=True)
            duracao_minutos = servico.duracao_minutos
            servico_nome = servico.nome
        except Servico.DoesNotExist:
            pass

    # Verificar se é data especial (feriado)
    data_especial = DataEspecial.objects.filter(
        empresa=empresa,
        data=data
    ).first()

    if data_especial and data_especial.tipo == 'feriado':
        return Response({
            'sucesso': True,
            'data': data.strftime('%Y-%m-%d'),
            'dia_semana': get_dia_semana_nome(data.weekday()),
            'mensagem': f'Fechado: {data_especial.descricao}',
            'horarios_disponiveis': []
        })

    # Buscar horário de funcionamento
    dia_semana = data.weekday()
    horario_func = HorarioFuncionamento.objects.filter(
        empresa=empresa,
        dia_semana=dia_semana,
        ativo=True
    ).first()

    # Se é data especial com horário diferenciado
    if data_especial and data_especial.tipo == 'especial':
        hora_abertura = data_especial.hora_abertura
        hora_fechamento = data_especial.hora_fechamento
        intervalo_inicio = None
        intervalo_fim = None
    elif horario_func:
        hora_abertura = horario_func.hora_abertura
        hora_fechamento = horario_func.hora_fechamento
        intervalo_inicio = horario_func.intervalo_inicio
        intervalo_fim = horario_func.intervalo_fim
    else:
        return Response({
            'sucesso': True,
            'data': data.strftime('%Y-%m-%d'),
            'dia_semana': get_dia_semana_nome(dia_semana),
            'mensagem': 'Fechado neste dia',
            'horarios_disponiveis': []
        })

    # Gerar slots de horário
    horarios_disponiveis = gerar_slots_disponiveis(
        empresa=empresa,
        profissional=profissional,
        data=data,
        hora_abertura=hora_abertura,
        hora_fechamento=hora_fechamento,
        intervalo_inicio=intervalo_inicio,
        intervalo_fim=intervalo_fim,
        duracao_minutos=duracao_minutos
    )

    return Response({
        'sucesso': True,
        'data': data.strftime('%Y-%m-%d'),
        'data_formatada': data.strftime('%d/%m/%Y'),
        'dia_semana': get_dia_semana_nome(dia_semana),
        'profissional': profissional.nome if profissional else 'Qualquer profissional',
        'servico': servico_nome,
        'duracao_minutos': duracao_minutos,
        'total_horarios': len(horarios_disponiveis),
        'horarios_disponiveis': horarios_disponiveis
    })


# ============================================
# FUNÇÕES AUXILIARES
# ============================================

def get_dia_semana_nome(dia_semana):
    """Converte número do dia da semana para nome"""
    dias = {
        0: 'Segunda-feira',
        1: 'Terça-feira',
        2: 'Quarta-feira',
        3: 'Quinta-feira',
        4: 'Sexta-feira',
        5: 'Sábado',
        6: 'Domingo'
    }
    return dias.get(dia_semana, 'Desconhecido')


def gerar_slots_disponiveis(empresa, profissional, data, hora_abertura, hora_fechamento,
                            intervalo_inicio, intervalo_fim, duracao_minutos, slot_minutos=30):
    """
    Gera lista de horários disponíveis no dia

    Args:
        empresa: Empresa
        profissional: Profissional ou None (qualquer)
        data: date
        hora_abertura: time
        hora_fechamento: time
        intervalo_inicio: time ou None
        intervalo_fim: time ou None
        duracao_minutos: int (duração do serviço)
        slot_minutos: int (intervalo entre slots, padrão 30min)

    Returns:
        Lista de strings com horários disponíveis ['09:00', '09:30', ...]
    """
    horarios = []
    hora_atual = datetime.combine(data, hora_abertura)
    hora_fim = datetime.combine(data, hora_fechamento)

    while hora_atual < hora_fim:
        hora_slot = hora_atual.time()

        # Calcular fim do atendimento
        hora_fim_atendimento = hora_atual + timedelta(minutes=duracao_minutos)

        # Verificar se passa do horário de fechamento
        if hora_fim_atendimento > hora_fim:
            break

        # Verificar se está no intervalo (almoço)
        if intervalo_inicio and intervalo_fim:
            # Se o horário está dentro do intervalo, pular
            if intervalo_inicio <= hora_slot < intervalo_fim:
                hora_atual += timedelta(minutes=slot_minutos)
                continue

            # Se o atendimento terminaria dentro do intervalo, pular
            hora_fim_atend_time = hora_fim_atendimento.time()
            if hora_slot < intervalo_inicio < hora_fim_atend_time:
                hora_atual += timedelta(minutes=slot_minutos)
                continue

        # Verificar se está livre (sem conflito de agendamento)
        data_hora_inicio = make_aware(hora_atual)
        data_hora_fim = make_aware(hora_fim_atendimento)

        conflito_query = Agendamento.objects.filter(
            empresa=empresa,
            data_hora_inicio__lt=data_hora_fim,
            data_hora_fim__gt=data_hora_inicio,
            status__in=['pendente', 'confirmado']
        )

        # Se especificou profissional, filtrar por ele
        if profissional:
            conflito_query = conflito_query.filter(profissional=profissional)

        if not conflito_query.exists():
            horarios.append(hora_slot.strftime('%H:%M'))

        # Próximo slot
        hora_atual += timedelta(minutes=slot_minutos)

    return horarios
