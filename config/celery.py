import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

app = Celery('config')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

# Configurar tarefas agendadas (Celery Beat)
app.conf.beat_schedule = {
    'enviar-lembretes-agendamentos': {
        'task': 'agendamentos.tasks.enviar_lembretes_agendamentos',
        'schedule': crontab(minute='*/10'),  # A cada 10 minutos
    },
    'gerar-agendamentos-recorrentes': {
        'task': 'agendamentos.tasks.gerar_agendamentos_recorrentes',
        'schedule': crontab(hour=0, minute=0),  # Diariamente à meia-noite
    },
    'notificar-trials-expirando': {
        'task': 'assinaturas.tasks.notificar_trials_expirando',
        'schedule': crontab(hour=9, minute=0),  # Diariamente às 9h
    },
}

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
