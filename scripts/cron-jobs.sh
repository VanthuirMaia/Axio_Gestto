#!/bin/bash

# Script que será executado pelo cron dentro do container

cd /app

# Roda o comando Django
python manage.py processar_agendamentos_concluidos >> /var/log/cron.log 2>&1

# Adicione aqui outros comandos periódicos no futuro
# python manage.py enviar_lembretes >> /var/log/cron.log 2>&1