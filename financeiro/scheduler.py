from apscheduler.schedulers.background import BackgroundScheduler
from django.core.management import call_command
import logging

logger = logging.getLogger(__name__)


def processar_agendamentos():
    """Executa o comando de processamento de agendamentos"""
    try:
        logger.info("🔄 Iniciando processamento de agendamentos...")
        call_command('processar_agendamentos_concluidos')
        logger.info("✅ Processamento concluído")
    except Exception as e:
        logger.error(f"❌ Erro no processamento: {str(e)}")


def start_scheduler():
    """Inicia o agendador de tarefas"""
    scheduler = BackgroundScheduler()
    
    # Executa a cada 15 minutos
    scheduler.add_job(
        processar_agendamentos,
        'interval',
        minutes=15,
        id='processar_agendamentos',
        replace_existing=True
    )
    
    scheduler.start()
    logger.info("📅 Agendador iniciado - processamento a cada 15 minutos")