# Gestto - Gestão de Agendamentos SaaS

Aplicação Django multi-tenant para salões, barbearias e pequenos negócios que dependem de agenda. Inclui painel interno, agendamento público, PWA e integrações com WhatsApp/n8n, mais controles de assinatura e limites por plano.

## Principais recursos
- Calendário FullCalendar com prevenção de conflitos, cores por profissional e timezone America/Recife
- Agendamentos recorrentes gerados via Celery (60 dias adiante) com logs e checagens de conflito
- Gestão de clientes, serviços, profissionais e comissões
- Multi-tenant por empresa (FK), com limites de uso e status de assinatura em middlewares
- Webhooks/integrações: WhatsApp (Evolution), n8n, APIs públicas para booking online
- PWA: manifest, service worker, página offline e static via WhiteNoise

## Stack
- Python/Django 5.2, Django REST Framework, Celery + Redis
- Postgres (prod) ou SQLite (dev)
- Nginx + Gunicorn para servir app; Docker Compose com db/redis/web/celery/nginx

## Como rodar (local)
1. Criar venv e instalar deps: `python -m venv .venv && .venv\Scripts\Activate && pip install -r requirements.txt`
2. Configurar `.env` (copie do template) e gerar `SECRET_KEY` segura.
3. Rodar migrações e criar superuser: `python manage.py migrate && python manage.py createsuperuser`.
4. Subir servidor: `python manage.py runserver` e acessar http://localhost:8000.

## Como rodar (Docker Compose)
- `docker-compose up -d` sobe Postgres, Redis, web (migrate+collectstatic+gunicorn), Celery worker e Nginx.
- Variáveis chave: `SECRET_KEY`, `DB_*`, `ALLOWED_HOSTS`, `CORS_ALLOWED_ORIGINS`, `REDIS_URL`, `STRIPE_*`, `ASAAS_*`, `EMAIL_*`.

## Variáveis de ambiente essenciais
- Core: `SECRET_KEY`, `DEBUG`, `ALLOWED_HOSTS`, `SITE_URL`, `CORS_ALLOWED_ORIGINS`
- Banco: `DATABASE_URL` ou `DB_ENGINE/DB_NAME/DB_USER/DB_PASSWORD/DB_HOST/DB_PORT`
- Cache/Celery: `REDIS_URL`, `CELERY_BROKER_URL`, `CELERY_RESULT_BACKEND`
- Emails: `EMAIL_BACKEND`, `EMAIL_HOST`, `EMAIL_PORT`, `EMAIL_USE_TLS`, `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`, `DEFAULT_FROM_EMAIL`
- Pagamentos: `STRIPE_PUBLIC_KEY`, `STRIPE_SECRET_KEY`, `STRIPE_WEBHOOK_SECRET`, `ASAAS_API_KEY`, `ASAAS_SANDBOX`
- Bots/API: `N8N_API_KEY`, `N8N_WEBHOOK_URL`, `EVOLUTION_API_URL`, `EVOLUTION_API_KEY`

## Estrutura resumida
- `core/`: auth custom (`Usuario`), onboarding, middlewares de assinatura/limites, health check
- `empresas/`, `clientes/`, `agendamentos/`, `financeiro/`: domínios principais (agenda, recorrência, logs do bot)
- `assinaturas/`: planos, assinatura e webhooks de criação de tenant/API
- `configuracoes/`: preferências da empresa, integrações e webhooks WhatsApp -> n8n
- `landing/`, `dashboard/`, `templates/`, `static/`: UI, PWA e assets
- `config/settings/`: base/dev/prod com split por ambiente

## Segurança e operações
- Produção usa Postgres + Redis, HTTPS forçado, HSTS, cookies seguros e ADMIN_URL customizável
- Multi-tenant depende de filtrar por `empresa` nas views/queries; revise antes de expor APIs públicas
- Evite commitar `.env` (há um na raiz; revise e limpe segredos)

## Roadmap curto
- Melhorias de UX no calendário (drag & drop, criação direta no clique)
- Bloqueio de folgas/ausências
- Dashboard financeiro avançado e API pública completa
- Automação de cobrança/renovação com Stripe/Asaas
