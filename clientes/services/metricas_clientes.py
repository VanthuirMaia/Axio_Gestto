from django.db.models import Count, Sum, Avg, Max, Q
from django.utils.timezone import now

from clientes.models import Cliente
from agendamentos.models import StatusAgendamento

def listar_clientes_com_metricas():
    clientes = (
        Cliente.objects
        .filter(ativo=True)
        .annotate(
            total_visitas=Count(
                'agendamentos',
                filter=Q(agendamentos__status=StatusAgendamento.CONCLUIDO)
            ),
            total_gasto=Sum(
                'agendamentos__valor_cobrado',
                filter=Q(agendamentos__status=StatusAgendamento.CONCLUIDO)
            ),
            ticket_medio=Avg(
                'agendamentos__valor_cobrado',
                filter=Q(agendamentos__status=StatusAgendamento.CONCLUIDO)
            ),
            ultima_visita=Max(
                'agendamentos__data_hora_inicio',
                filter=Q(agendamentos__status=StatusAgendamento.CONCLUIDO)
            )
        )
    )

    hoje = now()
    for cliente in clientes:
        cliente.dias_desde_ultima_visita = (
            (hoje - cliente.ultima_visita).days
            if cliente.ultima_visita else None
        )

    return clientes
