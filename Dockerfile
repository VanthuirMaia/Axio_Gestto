FROM python:3.11-slim

WORKDIR /app

# Variáveis de ambiente Python
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PIP_NO_CACHE_DIR=1
ENV PIP_DISABLE_PIP_VERSION_CHECK=1

# Django Environment (pode ser sobrescrito por .env)
ENV DJANGO_ENV=production

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y \
    postgresql-client \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copiar e instalar dependências Python
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copiar código da aplicação
COPY . .

# Criar diretórios para static e media
RUN mkdir -p /app/staticfiles /app/media

# Coletar arquivos estáticos (será refeito no entrypoint, mas garante que funcione)
RUN python manage.py collectstatic --noinput || true

# Expor porta
EXPOSE 8000

# Healthcheck para Docker
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health/ || exit 1

# Comando padrão (será sobrescrito no docker-compose)
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3", "--timeout", "120"]
