"""
Utilitários para gerenciar agendamentos recorrentes
"""
from datetime import datetime, timedelta
from django.utils import timezone
from django.db import transaction
import logging

logger = logging.getLogger(__name__)


def gerar_agendamentos_recorrencia(recorrencia, dias_futuros=60):
    """
    Gera agendamentos a partir de uma recorrência
    
    Args:
        recorrencia: Instância de AgendamentoRecorrente
        dias_futuros: Quantos dias no futuro gerar (padrão: 60)
    
    Returns:
        int: Número de agendamentos criados
    """
    from .models import Agendamento
    
    if not recorrencia.ativo:
        logger.info(f"Recorrência {recorrencia.id} está inativa, pulando geração")
        return 0
    
    # Data de início e fim
    data_inicio = max(recorrencia.data_inicio, timezone.now().date())
    data_limite = timezone.now().date() + timedelta(days=dias_futuros)
    
    if recorrencia.data_fim:
        data_limite = min(data_limite, recorrencia.data_fim)
    
    agendamentos_criados = 0
    data_atual = data_inicio
    
    logger.info(f"Gerando agendamentos para recorrência {recorrencia.id} de {data_inicio} até {data_limite}")
    
    with transaction.atomic():
        while data_atual <= data_limite:
            # Verificar se deve criar agendamento nesta data
            deve_criar = False
            
            if recorrencia.frequencia == 'diaria':
                deve_criar = True
            
            elif recorrencia.frequencia == 'semanal':
                dia_semana = data_atual.weekday()  # 0=segunda, 6=domingo
                deve_criar = dia_semana in recorrencia.dias_semana
            
            elif recorrencia.frequencia == 'mensal':
                deve_criar = data_atual.day == recorrencia.dia_mes
            
            if deve_criar:
                # Criar data/hora de início
                data_hora_inicio = timezone.make_aware(
                    datetime.combine(data_atual, recorrencia.hora_inicio)
                )
                
                # Calcular data/hora de fim
                data_hora_fim = data_hora_inicio + timedelta(minutes=recorrencia.servico.duracao_minutos)
                
                # Verificar se já existe agendamento
                existe = Agendamento.objects.filter(
                    empresa=recorrencia.empresa,
                    cliente=recorrencia.cliente,
                    servico=recorrencia.servico,
                    profissional=recorrencia.profissional,
                    data_hora_inicio=data_hora_inicio,
                    status__in=['pendente', 'confirmado']
                ).exists()
                
                if not existe:
                    # Criar agendamento (status confirmado pois é recorrente)
                    Agendamento.objects.create(
                        empresa=recorrencia.empresa,
                        cliente=recorrencia.cliente,
                        servico=recorrencia.servico,
                        profissional=recorrencia.profissional,
                        data_hora_inicio=data_hora_inicio,
                        data_hora_fim=data_hora_fim,
                        status='confirmado',  # Recorrências já são confirmadas
                        valor_cobrado=recorrencia.servico.preco,
                        origem='manual',
                        notas=f'Gerado automaticamente pela recorrência #{recorrencia.id}'
                    )
                    agendamentos_criados += 1
                    logger.debug(f"Agendamento criado para {data_hora_inicio}")
            
            # Próximo dia
            data_atual += timedelta(days=1)
    
    logger.info(f"Gerados {agendamentos_criados} agendamentos para recorrência {recorrencia.id}")
    return agendamentos_criados


def gerar_todos_agendamentos_recorrentes(dias_futuros=60):
    """
    Gera agendamentos para todas as recorrências ativas
    
    Args:
        dias_futuros: Quantos dias no futuro gerar (padrão: 60)
    
    Returns:
        dict: Estatísticas da geração
    """
    from .models import AgendamentoRecorrente
    
    recorrencias = AgendamentoRecorrente.objects.filter(ativo=True)
    
    total_recorrencias = recorrencias.count()
    total_agendamentos = 0
    
    logger.info(f"Iniciando geração de agendamentos para {total_recorrencias} recorrências")
    
    for recorrencia in recorrencias:
        try:
            criados = gerar_agendamentos_recorrencia(recorrencia, dias_futuros)
            total_agendamentos += criados
        except Exception as e:
            logger.error(f"Erro ao gerar agendamentos para recorrência {recorrencia.id}: {e}")
    
    logger.info(f"Geração concluída: {total_agendamentos} agendamentos criados")
    
    return {
        'total_recorrencias': total_recorrencias,
        'total_agendamentos': total_agendamentos
    }
