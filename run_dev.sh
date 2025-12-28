#!/bin/bash
# ============================================
# Script para rodar o projeto em DESENVOLVIMENTO
# Uso: ./run_dev.sh
# ============================================

echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║                                                            ║"
echo "║   🚀 Iniciando Ambiente de DESENVOLVIMENTO                 ║"
echo "║                                                            ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Define o ambiente
export DJANGO_ENV=development

# Copia .env.dev para .env (se existir)
if [ -f .env.dev ]; then
    echo "✓ Carregando variáveis de .env.dev"
    cp .env.dev .env
else
    echo "⚠ Arquivo .env.dev não encontrado!"
    echo "  Criando a partir de .env.example..."
    if [ -f .env.example ]; then
        cp .env.example .env.dev
        cp .env.example .env
    fi
fi

# Ativa o ambiente virtual (se existir)
if [ -f .venv/bin/activate ]; then
    echo "✓ Ativando ambiente virtual..."
    source .venv/bin/activate
elif [ -f venv/bin/activate ]; then
    echo "✓ Ativando ambiente virtual..."
    source venv/bin/activate
else
    echo "⚠ Ambiente virtual não encontrado"
fi

# Aplica migrações
echo ""
echo "✓ Aplicando migrações..."
python manage.py migrate --noinput

# Coleta arquivos estáticos
echo ""
echo "✓ Coletando arquivos estáticos..."
python manage.py collectstatic --noinput --clear

# Inicia o servidor de desenvolvimento
echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║   Servidor rodando em: http://localhost:8000               ║"
echo "║   Ambiente: DEVELOPMENT                                    ║"
echo "║   Pressione Ctrl+C para parar                              ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

python manage.py runserver 0.0.0.0:8000
