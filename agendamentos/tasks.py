"""
Tasks Celery para agendamentos recorrentes
"""
from celery import shared_task
from django.utils import timezone
from django.utils.timezone import make_aware
from datetime import datetime, timedelta
from .models import AgendamentoRecorrente, Agendamento


@shared_task
def gerar_agendamentos_recorrentes():
    """
    Task que roda diariamente às 00:00
    Gera agendamentos para os próximos 60 dias baseado nas recorrências ativas

    Configurar no celery beat:
    CELERY_BEAT_SCHEDULE = {
        'gerar-agendamentos-recorrentes': {
            'task': 'agendamentos.tasks.gerar_agendamentos_recorrentes',
            'schedule': crontab(hour=0, minute=0),  # Diariamente à meia-noite
        },
    }
    """
    from django.db import transaction

    hoje = timezone.now().date()
    limite = hoje + timedelta(days=60)  # Gerar para os próximos 60 dias

    recorrencias = AgendamentoRecorrente.objects.filter(
        ativo=True,
        data_inicio__lte=limite  # Começou antes do limite
    ).select_related('empresa', 'cliente', 'servico', 'profissional')

    total_criados = 0
    total_pulados = 0

    for rec in recorrencias:
        # Se tem data_fim e já passou, desativar
        if rec.data_fim and rec.data_fim < hoje:
            rec.ativo = False
            rec.save()
            continue

        # Gerar datas baseado na frequência
        datas_para_gerar = calcular_datas_recorrencia(rec, hoje, limite)

        for data in datas_para_gerar:
            # Criar data/hora completa
            data_hora_inicio = make_aware(datetime.combine(data, rec.hora_inicio))
            data_hora_fim = data_hora_inicio + timedelta(minutes=rec.servico.duracao_minutos)

            # Verificar se já existe agendamento exatamente igual
            existe = Agendamento.objects.filter(
                empresa=rec.empresa,
                cliente=rec.cliente,
                profissional=rec.profissional,
                data_hora_inicio=data_hora_inicio
            ).exists()

            if existe:
                total_pulados += 1
                continue

            # Verificar conflito de horário com mesmo profissional
            conflito = Agendamento.objects.filter(
                empresa=rec.empresa,
                profissional=rec.profissional,
                data_hora_inicio__lt=data_hora_fim,
                data_hora_fim__gt=data_hora_inicio,
                status__in=['pendente', 'confirmado']
            ).exists()

            if conflito:
                total_pulados += 1
                continue

            # Criar agendamento
            with transaction.atomic():
                Agendamento.objects.create(
                    empresa=rec.empresa,
                    cliente=rec.cliente,
                    servico=rec.servico,
                    profissional=rec.profissional,
                    data_hora_inicio=data_hora_inicio,
                    data_hora_fim=data_hora_fim,
                    status='confirmado',  # Recorrentes já são confirmados
                    valor_cobrado=rec.servico.preco,
                    notas=f'📅 Agendamento recorrente gerado automaticamente\n'
                          f'Recorrência: {rec.get_descricao_frequencia()}\n'
                          f'ID: {rec.id}'
                )
                total_criados += 1

    return {
        'total_criados': total_criados,
        'total_pulados': total_pulados,
        'data_execucao': timezone.now().isoformat()
    }


def calcular_datas_recorrencia(recorrencia, data_inicio, data_limite):
    """
    Calcula todas as datas em que o agendamento deve ocorrer

    Args:
        recorrencia: Instância de AgendamentoRecorrente
        data_inicio: Data inicial para buscar (normalmente hoje)
        data_limite: Data limite (normalmente hoje + 60 dias)

    Returns:
        Lista de datas (date objects)
    """
    datas = []

    # Começar da data de início da recorrência ou hoje (o que for maior)
    data_atual = max(recorrencia.data_inicio, data_inicio)

    # Limitar pela data_fim da recorrência se existir
    if recorrencia.data_fim:
        data_limite = min(data_limite, recorrencia.data_fim)

    if recorrencia.frequencia == 'diaria':
        # Todos os dias
        while data_atual <= data_limite:
            datas.append(data_atual)
            data_atual += timedelta(days=1)

    elif recorrencia.frequencia == 'semanal':
        # Dias específicos da semana
        if not recorrencia.dias_semana:
            return []  # Sem dias definidos

        # Garantir que dias_semana é uma lista
        dias_semana = recorrencia.dias_semana if isinstance(recorrencia.dias_semana, list) else []

        while data_atual <= data_limite:
            # Verificar se o dia da semana está na lista (0=segunda, 6=domingo)
            if data_atual.weekday() in dias_semana:
                datas.append(data_atual)
            data_atual += timedelta(days=1)

    elif recorrencia.frequencia == 'mensal':
        # Dia específico do mês
        if not recorrencia.dia_mes:
            return []  # Sem dia definido

        # Começar do primeiro dia do mês atual
        data_atual = data_atual.replace(day=1)

        while data_atual <= data_limite:
            try:
                # Tentar criar data com o dia especificado
                data_mes = data_atual.replace(day=recorrencia.dia_mes)

                # Se a data está dentro do range e não passou ainda
                if data_inicio <= data_mes <= data_limite:
                    datas.append(data_mes)

            except ValueError:
                # Dia inválido para este mês (ex: 31 em fevereiro)
                pass

            # Próximo mês
            if data_atual.month == 12:
                data_atual = data_atual.replace(year=data_atual.year + 1, month=1)
            else:
                data_atual = data_atual.replace(month=data_atual.month + 1)

    return datas


@shared_task
def limpar_recorrencias_expiradas():
    """
    Task opcional para desativar recorrências expiradas
    Roda semanalmente
    """
    from django.utils import timezone

    hoje = timezone.now().date()

    # Desativar recorrências que já expiraram
    expiradas = AgendamentoRecorrente.objects.filter(
        ativo=True,
        data_fim__lt=hoje
    )

    total = expiradas.count()
    expiradas.update(ativo=False)

    return {
        'total_desativadas': total,
        'data_execucao': timezone.now().isoformat()
    }
