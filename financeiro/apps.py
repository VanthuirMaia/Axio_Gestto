from django.apps import AppConfig
import logging

logger = logging.getLogger(__name__)


class FinanceiroConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'financeiro'
    verbose_name = 'Financeiro'

    def ready(self):
        import financeiro.signals  # Signals
        
        # Inicia o agendador apenas em desenvolvimento
        from django.conf import settings
        if settings.DEBUG:
            try:
                from financeiro.scheduler import start_scheduler
                start_scheduler()
            except Exception as e:
                logger.error(f"Erro ao iniciar agendador: {str(e)}")