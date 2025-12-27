# 🚀 Deploy Gestto - Docker Swarm (VPS Existente)

Guia específico para deploy do **Gestto** em servidor VPS que já roda:
- Traefik (proxy reverso)
- n8n, Evolution API, PostgreSQL, Redis (via Portainer)

---

## 🎯 Arquitetura

```
Traefik (80/443)
    │
    ├─► app.gestto.app.br → Gestto (Django)
    ├─► axiodev.cloud → Landing Page
    ├─► n8n.axiodev.cloud → n8n
    └─► evolution.axiodev.cloud → Evolution API

Rede: redeaxio (todos conectados)

Redis: redis_redis:6379 (database 2 para Gestto)
PostgreSQL: Opções:
   - Supabase (cloud)
   - OU postgres local (docker)
```

---

## 📋 Pré-requisitos

### 1. No Servidor VPS (já deve estar pronto)
- [x] Docker Swarm ativo
- [x] Traefik rodando
- [x] Rede `redeaxio` criada
- [x] Redis rodando
- [x] Portainer (opcional, para gerenciar)

### 2. DNS Configurado
- [x] `app.gestto.app.br` → `72.61.56.252` (registro A)

### 3. GitHub (para CI/CD)
- [ ] Repositório criado
- [ ] Secrets configurados (vamos fazer)

---

## 🔧 Setup Inicial no Servidor

### 1. Conectar no servidor

```bash
ssh root@72.61.56.252
```

### 2. Criar diretório do projeto

```bash
mkdir -p /var/www/gestto
cd /var/www/gestto
```

### 3. Clonar repositório

```bash
git clone https://github.com/SEU_USUARIO/axio_gestto.git .
```

### 4. Criar `.env.production` no servidor

```bash
nano .env.production
```

Cole este conteúdo (ajuste os valores):

```bash
# Django Core
DEBUG=False
SECRET_KEY=GERE_UMA_SECRET_KEY_SEGURA_AQUI
ALLOWED_HOSTS=app.seudominio.com.br,seudominio.com.br
CSRF_TRUSTED_ORIGINS=https://app.seudominio.com.br,https://seudominio.com.br

# ESCOLHA UMA OPÇÃO ABAIXO:

# OPÇÃO 1: Supabase (Recomendado - cloud gerenciado)
DATABASE_URL=postgresql://USER:PASSWORD@HOST:PORT/DATABASE

# OPÇÃO 2: PostgreSQL local (se preferir usar o que já está rodando)
# DATABASE_URL=
# DB_ENGINE=django.db.backends.postgresql
# DB_NAME=gestto_db
# DB_USER=gestto_user
# DB_PASSWORD=SUA_SENHA_POSTGRES
# DB_HOST=postgres_postgres  # Nome do container Postgres
# DB_PORT=5432

# Email - Brevo
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp-relay.brevo.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=SEU_USUARIO@smtp-brevo.com
EMAIL_HOST_PASSWORD=SUA_SENHA_BREVO_AQUI
DEFAULT_FROM_EMAIL=contato@seudominio.com.br

# Redis (usa o existente, database 2)
REDIS_URL=redis://redis_redis:6379/2
CELERY_BROKER_URL=redis://redis_redis:6379/2
CELERY_RESULT_BACKEND=redis://redis_redis:6379/2

# n8n Integration
N8N_API_KEY=SUA_N8N_API_KEY_AQUI
N8N_WEBHOOK_URL=https://seu-n8n.com/webhook/bot-universal

# Evolution API
EVOLUTION_API_URL=https://sua-evolution.com
EVOLUTION_API_KEY=SUA_EVOLUTION_API_KEY_AQUI

# Site URL
SITE_URL=https://app.seudominio.com.br

# Stripe
STRIPE_PUBLIC_KEY=pk_test_SUA_PUBLIC_KEY_AQUI
STRIPE_SECRET_KEY=sk_test_SUA_SECRET_KEY_AQUI
STRIPE_WEBHOOK_SECRET=whsec_SUA_WEBHOOK_SECRET_AQUI
STRIPE_PRICE_ESSENCIAL=price_SEU_PRICE_ID_AQUI
STRIPE_PRICE_PROFISSIONAL=price_SEU_PRICE_ID_AQUI
STRIPE_PRICE_EMPRESARIAL=price_SEU_PRICE_ID_AQUI

# Superuser
DJANGO_SUPERUSER_USERNAME=admin
DJANGO_SUPERUSER_EMAIL=admin@seudominio.com
DJANGO_SUPERUSER_PASSWORD=SUA_SENHA_FORTE_AQUI
```

Salve: `Ctrl+O` → `Enter` → `Ctrl+X`

---

## 🐳 Deploy com Docker Stack

### 1. Build da imagem Docker

```bash
cd /var/www/gestto

# Build da imagem
docker build -t gestto-app:latest .
```

### 2. Deploy da stack

```bash
# Carregar variáveis de ambiente
export $(cat .env.production | xargs)

# Deploy da stack
docker stack deploy -c gestto-stack.yaml gestto
```

### 3. Verificar deploy

```bash
# Ver serviços da stack
docker stack services gestto

# Ver logs
docker service logs -f gestto_gestto_web
docker service logs -f gestto_gestto_celery

# Ver containers rodando
docker ps | grep gestto
```

---

## ✅ Verificar Funcionamento

### 1. Health Check

```bash
curl https://app.gestto.app.br/health/
# Esperado: {"status": "ok"}
```

### 2. Acessar Admin

```
https://app.gestto.app.br/admin/
```

**Login:**
- Usuário: `admin`
- Senha: `Admin@Gestto2025!Secure`

### 3. Ver logs em tempo real

```bash
# Logs do Django
docker service logs -f gestto_gestto_web

# Logs do Celery
docker service logs -f gestto_gestto_celery
```

---

## 🔄 Atualizar Aplicação (Deploy Manual)

```bash
cd /var/www/gestto

# 1. Puxar atualizações do Git
git pull origin main

# 2. Rebuild da imagem
docker build -t gestto-app:latest .

# 3. Atualizar stack
docker stack deploy -c gestto-stack.yaml gestto

# 4. Esperar alguns segundos e verificar
docker stack services gestto
```

---

## 🤖 CI/CD Automático (GitHub Actions)

### 1. Configurar GitHub Secrets

No GitHub: **Settings → Secrets and variables → Actions**

Adicione:

| Nome              | Valor                              |
|-------------------|------------------------------------|
| `DEPLOY_HOST`     | `72.61.56.252`                     |
| `DEPLOY_USER`     | `root`                             |
| `DEPLOY_SSH_KEY`  | Chave privada SSH completa         |

**Gerar chave SSH (no seu PC):**

```bash
ssh-keygen -t ed25519 -C "deploy-gestto" -f ~/.ssh/gestto_deploy

# Copiar chave pública para o servidor
ssh-copy-id -i ~/.ssh/gestto_deploy.pub root@72.61.56.252

# Exibir chave privada (copiar TODO o conteúdo)
cat ~/.ssh/gestto_deploy
# Cole no GitHub Secret: DEPLOY_SSH_KEY
```

### 2. Workflow já está criado!

O arquivo `.github/workflows/deploy.yml` precisa ser adaptado para usar `docker stack` em vez de `docker-compose`.

---

## 🛠️ Comandos Úteis

### Gerenciar Stack

```bash
# Listar stacks
docker stack ls

# Listar serviços da stack gestto
docker stack services gestto

# Ver detalhes de um serviço
docker service inspect gestto_gestto_web

# Escalar serviço (aumentar réplicas)
docker service scale gestto_gestto_web=2

# Remover stack completa
docker stack rm gestto
```

### Logs e Debug

```bash
# Logs de todos os serviços
docker stack services gestto --format "{{.Name}}"

# Logs de um serviço específico
docker service logs -f gestto_gestto_web

# Ver últimas 100 linhas
docker service logs --tail 100 gestto_gestto_web

# Entrar no container (para debug)
# Primeiro, descubra o ID do container:
docker ps | grep gestto_web
# Depois:
docker exec -it <CONTAINER_ID> /bin/bash
```

### Executar comandos Django

```bash
# Migrations
docker exec $(docker ps -q -f name=gestto_gestto_web) python manage.py migrate

# Collectstatic
docker exec $(docker ps -q -f name=gestto_gestto_web) python manage.py collectstatic --noinput

# Criar superuser
docker exec -it $(docker ps -q -f name=gestto_gestto_web) python manage.py createsuperuser

# Shell Django
docker exec -it $(docker ps -q -f name=gestto_gestto_web) python manage.py shell
```

---

## 🔒 Traefik - SSL Automático

O Traefik já está configurado para:
- ✅ Gerar certificado SSL via Let's Encrypt
- ✅ Renovar automaticamente
- ✅ Redirecionar HTTP → HTTPS

Não precisa fazer nada! Quando acessar `app.gestto.app.br`, o Traefik automaticamente:
1. Gera o certificado SSL
2. Configura HTTPS
3. Redireciona HTTP para HTTPS

---

## 🗄️ Usar PostgreSQL Local (Alternativa ao Supabase)

Se quiser usar o PostgreSQL que já está rodando:

### 1. Descobrir nome do container Postgres

```bash
docker ps | grep postgres
# Anote o nome, exemplo: postgres_postgres.1.yae87yri6ucjrapnpsmclg9f9
```

### 2. Criar database para o Gestto

```bash
# Acessar container Postgres
docker exec -it postgres_postgres.1.yae87yri6ucjrapnpsmclg9f9 psql -U postgres

# Dentro do PostgreSQL:
CREATE DATABASE gestto_db;
CREATE USER gestto_user WITH PASSWORD 'SenhaSegura123!';
GRANT ALL PRIVILEGES ON DATABASE gestto_db TO gestto_user;
\q
```

### 3. Atualizar `.env.production`

```bash
nano /var/www/gestto/.env.production
```

Comentar Supabase e descomentar PostgreSQL local:

```bash
# DATABASE_URL=postgresql://...supabase...

DB_ENGINE=django.db.backends.postgresql
DB_NAME=gestto_db
DB_USER=gestto_user
DB_PASSWORD=SenhaSegura123!
DB_HOST=postgres_postgres  # Nome base do serviço Postgres
DB_PORT=5432
```

### 4. Rebuild e redeploy

```bash
docker build -t gestto-app:latest .
docker stack deploy -c gestto-stack.yaml gestto
```

---

## 🆘 Troubleshooting

### Serviço não inicia

```bash
# Ver logs do serviço
docker service logs gestto_gestto_web

# Ver detalhes do serviço
docker service ps gestto_gestto_web --no-trunc

# Forçar atualização
docker service update --force gestto_gestto_web
```

### Erro "network not found"

```bash
# Verificar se a rede redeaxio existe
docker network ls | grep redeaxio

# Se não existir, criar:
docker network create -d overlay --attachable redeaxio
```

### Traefik não roteia para o Gestto

```bash
# Verificar labels do serviço
docker service inspect gestto_gestto_web | grep -A 20 Labels

# Verificar logs do Traefik
docker service logs traefik_traefik

# Forçar atualização do serviço
docker service update --force gestto_gestto_web
```

### Reset completo

```bash
cd /var/www/gestto

# Remover stack
docker stack rm gestto

# Aguardar remoção completa
sleep 30

# Rebuild
docker build --no-cache -t gestto-app:latest .

# Deploy novamente
export $(cat .env.production | xargs)
docker stack deploy -c gestto-stack.yaml gestto
```

---

## 📊 Monitoramento

### Via Portainer

1. Acesse o Portainer (se configurado)
2. Vá em **Stacks**
3. Clique em **gestto**
4. Veja status dos serviços, logs, etc.

### Via linha de comando

```bash
# Status dos serviços
watch -n 5 'docker stack services gestto'

# Uso de recursos
docker stats $(docker ps -q -f name=gestto)
```

---

## 🎉 Pronto!

Sua aplicação **Gestto** está rodando em:
**https://app.gestto.app.br**

Integrada com:
- ✅ Traefik (SSL automático)
- ✅ Redis existente (database 2)
- ✅ n8n e Evolution API
- ✅ PostgreSQL (Supabase ou local)

**Próximos passos:**
1. Testar todas as funcionalidades
2. Configurar CI/CD (GitHub Actions)
3. Monitorar logs por 24h
4. Ajustar recursos conforme necessário
