#!/bin/bash
# ============================================
# Script para rodar o projeto em PRODUÇÃO
# Uso: ./run_prod.sh
# ATENÇÃO: Use apenas em servidor de produção!
# ============================================

echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║                                                            ║"
echo "║   🔒 Iniciando Ambiente de PRODUÇÃO                        ║"
echo "║                                                            ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Define o ambiente
export DJANGO_ENV=production

# Verifica se .env.prod existe
if [ ! -f .env.prod ]; then
    echo "❌ ERRO: Arquivo .env.prod não encontrado!"
    echo "   Crie o arquivo .env.prod baseado em .env.prod.example"
    echo "   e configure as variáveis de produção."
    exit 1
fi

# Copia .env.prod para .env
echo "✓ Carregando variáveis de .env.prod"
cp .env.prod .env

# Ativa o ambiente virtual
if [ -f .venv/bin/activate ]; then
    source .venv/bin/activate
elif [ -f venv/bin/activate ]; then
    source venv/bin/activate
else
    echo "❌ ERRO: Ambiente virtual não encontrado!"
    exit 1
fi

# Verifica se todas as variáveis críticas estão definidas
echo ""
echo "✓ Verificando configurações de segurança..."

# Cria diretório de logs se não existir
mkdir -p logs

# Aplica migrações
echo ""
echo "✓ Aplicando migrações..."
python manage.py migrate --noinput

# Coleta arquivos estáticos
echo ""
echo "✓ Coletando arquivos estáticos..."
python manage.py collectstatic --noinput --clear

# Verifica se SECRET_KEY foi alterada
python -c "
from decouple import config
secret = config('SECRET_KEY')
if 'MUDE-ISTO' in secret or 'dev-secret' in secret or len(secret) < 40:
    print('❌ ERRO: SECRET_KEY não foi configurada corretamente!')
    print('   Gere uma nova chave segura e configure em .env.prod')
    exit(1)
print('✓ SECRET_KEY configurada corretamente')
"

if [ $? -ne 0 ]; then
    exit 1
fi

# Verifica se DEBUG está False
python -c "
from decouple import config
if config('DEBUG', cast=bool):
    print('❌ ERRO: DEBUG está True em produção!')
    print('   Configure DEBUG=False no .env.prod')
    exit(1)
print('✓ DEBUG desativado')
"

if [ $? -ne 0 ]; then
    exit 1
fi

echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║                                                            ║"
echo "║   ✓ Ambiente de PRODUÇÃO configurado corretamente         ║"
echo "║                                                            ║"
echo "║   Recomendações:                                           ║"
echo "║   • Use Gunicorn ou uWSGI ao invés de runserver            ║"
echo "║   • Configure Nginx como proxy reverso                     ║"
echo "║   • Use supervisor ou systemd para process management      ║"
echo "║                                                            ║"
echo "║   Exemplo com Gunicorn:                                    ║"
echo "║   gunicorn config.wsgi:application --bind 0.0.0.0:8000     ║"
echo "║                                                            ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Inicia Gunicorn se estiver instalado
if command -v gunicorn &> /dev/null; then
    echo "✓ Iniciando com Gunicorn..."
    gunicorn config.wsgi:application \
        --bind 0.0.0.0:8000 \
        --workers 4 \
        --timeout 120 \
        --access-logfile logs/access.log \
        --error-logfile logs/error.log \
        --log-level info
else
    echo "⚠️ Gunicorn não encontrado. Instalando..."
    pip install gunicorn

    echo "✓ Iniciando com Gunicorn..."
    gunicorn config.wsgi:application \
        --bind 0.0.0.0:8000 \
        --workers 4 \
        --timeout 120 \
        --access-logfile logs/access.log \
        --error-logfile logs/error.log \
        --log-level info
fi
