@echo off
REM ============================================
REM Script para rodar o projeto em DESENVOLVIMENTO
REM Uso: run_dev.bat
REM ============================================

echo.
echo ╔════════════════════════════════════════════════════════════╗
echo ║                                                            ║
echo ║   🚀 Iniciando Ambiente de DESENVOLVIMENTO                 ║
echo ║                                                            ║
echo ╚════════════════════════════════════════════════════════════╝
echo.

REM Define o ambiente
set DJANGO_ENV=development

REM Copia .env.dev para .env (se existir)
if exist .env.dev (
    echo ✓ Carregando variáveis de .env.dev
    copy /Y .env.dev .env >nul
) else (
    echo ⚠ Arquivo .env.dev não encontrado!
    echo   Criando a partir de .env.example...
    if exist .env.example (
        copy .env.example .env.dev
        copy .env.example .env
    )
)

REM Ativa o ambiente virtual (se existir)
if exist .venv\Scripts\activate.bat (
    echo ✓ Ativando ambiente virtual...
    call .venv\Scripts\activate.bat
) else (
    echo ⚠ Ambiente virtual não encontrado em .venv
)

REM Aplica migrações
echo.
echo ✓ Aplicando migrações...
python manage.py migrate --noinput

REM Coleta arquivos estáticos
echo.
echo ✓ Coletando arquivos estáticos...
python manage.py collectstatic --noinput --clear

REM Inicia o servidor de desenvolvimento
echo.
echo ╔════════════════════════════════════════════════════════════╗
echo ║   Servidor rodando em: http://localhost:8000               ║
echo ║   Ambiente: DEVELOPMENT                                    ║
echo ║   Pressione Ctrl+C para parar                              ║
echo ╚════════════════════════════════════════════════════════════╝
echo.

python manage.py runserver 0.0.0.0:8000
