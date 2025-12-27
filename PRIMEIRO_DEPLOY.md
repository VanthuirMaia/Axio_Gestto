# ⚡ Primeiro Deploy - Gestto no Servidor VPS

Guia rápido para colocar o **Gestto no ar** no seu servidor que já tem:
- Traefik, n8n, Evolution, PostgreSQL, Redis, Landing Page

---

## 🎯 Você está aqui (conectado no servidor)

```
root@serveraxio:~#
```

Vamos fazer o deploy em **5 passos simples**!

---

## 1️⃣ Criar diretório e clonar projeto

```bash
# Criar diretório
mkdir -p /var/www/gestto
cd /var/www/gestto

# Clonar repositório (ALTERE a URL para o seu repositório)
git clone https://github.com/SEU_USUARIO/axio_gestto.git .
```

---

## 2️⃣ Criar arquivo .env.production

```bash
nano .env.production
```

**Cole este conteúdo** (já está com suas configurações):

```bash
# Django Core
DEBUG=False
SECRET_KEY=GERE_UMA_SECRET_KEY_SEGURA_AQUI
ALLOWED_HOSTS=app.gestto.app.br,gestto.app.br,SEU_IP_VPS
CSRF_TRUSTED_ORIGINS=https://app.gestto.app.br,https://gestto.app.br

# Database - Supabase
DATABASE_URL=postgresql://USER:PASSWORD@HOST:PORT/DATABASE

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

**Salvar:** `Ctrl+O` → `Enter` → `Ctrl+X`

---

## 3️⃣ Build da imagem Docker

```bash
cd /var/www/gestto

# Build (vai demorar uns 2-3 minutos)
docker build -t gestto-app:latest .
```

---

## 4️⃣ Deploy da stack

```bash
# Carregar variáveis de ambiente
export $(cat .env.production | grep -v '^#' | xargs)

# Deploy no Docker Swarm
docker stack deploy -c gestto-stack.yaml gestto
```

---

## 5️⃣ Verificar se subiu

```bash
# Ver serviços (aguarde aparecer como "1/1")
docker stack services gestto

# Ver logs em tempo real
docker service logs -f gestto_gestto_web
```

**Aguarde até ver:** "Booting worker" ou "Listening at: http://0.0.0.0:8000"

Aperte `Ctrl+C` para sair dos logs.

---

## ✅ Testar!

### 1. Health Check

```bash
curl https://app.gestto.app.br/health/
```

**Esperado:** `{"status": "ok"}`

### 2. Acessar Admin no navegador

```
https://app.gestto.app.br/admin/
```

**Login:**
- Usuário: `admin`
- Senha: `Admin@Gestto2025!Secure`

---

## 🎉 Funcionou?

Se acessou o admin, **parabéns!** Seu Gestto está no ar! 🚀

**Próximos passos:**
1. Testar funcionalidades
2. Configurar CI/CD (GitHub Actions)
3. Personalizar

---

## 🆘 Não funcionou?

### Erro ao fazer build

```bash
# Ver erro completo
docker build -t gestto-app:latest . 2>&1 | tail -50
```

### Serviço não sobe (0/1)

```bash
# Ver logs com erro
docker service logs gestto_gestto_web --tail 100

# Forçar update
docker service update --force gestto_gestto_web
```

### Erro 502 (Bad Gateway)

```bash
# Verificar se o container está rodando
docker ps | grep gestto

# Ver logs do Traefik
docker service logs traefik_traefik --tail 50

# Verificar labels do serviço
docker service inspect gestto_gestto_web | grep -A 10 Labels
```

### Não conecta no banco Supabase

```bash
# Testar conexão manualmente
docker exec $(docker ps -q -f name=gestto_web) python manage.py dbshell

# Se falhar, verificar DATABASE_URL no .env.production
```

### Reset completo

```bash
cd /var/www/gestto

# Remover stack
docker stack rm gestto

# Aguardar 30 segundos
sleep 30

# Rebuild
docker build --no-cache -t gestto-app:latest .

# Deploy novamente
export $(cat .env.production | grep -v '^#' | xargs)
docker stack deploy -c gestto-stack.yaml gestto
```

---

## 📞 Precisa de ajuda?

1. Copie os logs: `docker service logs gestto_gestto_web --tail 100`
2. Cole para análise
3. Consulte `DEPLOY_SWARM.md` (guia completo)

---

**Boa sorte!** 🚀
