# Tarefa Celery para limpar logs antigos automaticamente
from celery import shared_task
from django.core.management import call_command
import logging

logger = logging.getLogger(__name__)


@shared_task
def limpar_logs_analytics_antigos():
    """
    Limpa logs de analytics com mais de 30 dias
    Executado automaticamente via Celery Beat
    """
    try:
        logger.info("Iniciando limpeza de logs de analytics...")
        call_command('limpar_logs_analytics', days=30)
        logger.info("Limpeza de logs concluída com sucesso")
    except Exception as e:
        logger.error(f"Erro ao limpar logs de analytics: {str(e)}")
