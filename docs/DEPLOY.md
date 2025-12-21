# 🚀 Guia de Deploy - Axio Gestto

## 📋 Pré-requisitos

- Servidor com Ubuntu 22.04+ / Debian 11+
- Docker e Docker Compose instalados
- Domínio configurado apontando para o servidor
- Portas 80, 443, 22 abertas no firewall
- Mínimo 2GB RAM, 2 vCPUs, 20GB storage

---

## 🔧 Instalação do Docker

```bash
# Atualizar sistema
sudo apt update && sudo apt upgrade -y

# Instalar Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Instalar Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Adicionar usuário ao grupo docker
sudo usermod -aG docker $USER
newgrp docker

# Verificar instalação
docker --version
docker-compose --version
```

---

## 📦 Deploy Passo a Passo

### 1. Clonar Repositório

```bash
# SSH (recomendado)
git clone git@github.com:seu-usuario/axio_gestto.git
cd axio_gestto

# OU HTTPS
git clone https://github.com/seu-usuario/axio_gestto.git
cd axio_gestto
```

### 2. Configurar Variáveis de Ambiente

```bash
# Copiar exemplo
cp .env.example .env

# Editar com suas configurações
nano .env
```

**Configurações OBRIGATÓRIAS no `.env`:**

```env
# Django
SECRET_KEY=<gerar com: python -c "import secrets; print(''.join(secrets.choice('abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)') for i in range(50)))">
DEBUG=False
ALLOWED_HOSTS=seu-dominio.com,www.seu-dominio.com

# Database
DB_PASSWORD=<gerar com: python -c "import secrets; print(secrets.token_urlsafe(24))">

# API
N8N_API_KEY=<gerar com: python -c "import secrets; print(secrets.token_urlsafe(32))">

# CORS
CORS_ALLOWED_ORIGINS=https://seu-dominio.com,https://www.seu-dominio.com

# Email (opcional, mas recomendado)
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST_USER=seu-email@gmail.com
EMAIL_HOST_PASSWORD=sua-senha-app-gmail
DEFAULT_FROM_EMAIL=noreply@seu-dominio.com

# Superuser inicial
DJANGO_SUPERUSER_USERNAME=admin
DJANGO_SUPERUSER_EMAIL=admin@seu-dominio.com
DJANGO_SUPERUSER_PASSWORD=SenhaForte@2025!
```

### 3. Configurar SSL (Let's Encrypt)

**Opção A: Certificado Let's Encrypt (Produção)**

```bash
# Criar diretório para certificados
mkdir -p certbot/conf certbot/www

# Obter certificado
docker run -it --rm \
  -v $(pwd)/certbot/conf:/etc/letsencrypt \
  -v $(pwd)/certbot/www:/var/www/certbot \
  -p 80:80 \
  certbot/certbot certonly --standalone \
  --email seu-email@gmail.com \
  --agree-tos \
  --no-eff-email \
  -d seu-dominio.com \
  -d www.seu-dominio.com

# Copiar certificados para nginx
sudo cp certbot/conf/live/seu-dominio.com/fullchain.pem nginx/certs/cert.pem
sudo cp certbot/conf/live/seu-dominio.com/privkey.pem nginx/certs/key.pem

# Editar docker-compose.yml (linha 120)
# Descomentar:
# - ./certbot/conf:/etc/nginx/certs:ro
```

**Opção B: Certificado Auto-Assinado (Desenvolvimento)**

O Nginx já gera automaticamente no build. Apenas para testes locais!

### 4. Build e Start dos Containers

```bash
# Build das imagens
docker-compose build

# Subir todos os serviços
docker-compose up -d

# Verificar logs
docker-compose logs -f

# Verificar status
docker-compose ps
```

**Saída esperada:**
```
NAME                IMAGE                COMMAND              STATUS
gestao_db           postgres:15          "docker-entrypoint"  Up (healthy)
gestao_redis        redis:7-alpine       "docker-entrypoint"  Up (healthy)
gestao_web          axio_gestto-web      "sh -c python..."    Up (healthy)
gestao_celery       axio_gestto-celery   "celery -A config"   Up
gestao_nginx        axio_gestto-nginx    "nginx -g 'daemon"   Up
```

### 5. Verificar Deploy

```bash
# Health check
curl http://localhost/health/

# Deve retornar:
# {"status":"healthy","checks":{"database":"ok","redis":"ok"}}

# Verificar SSL
curl -I https://seu-dominio.com/

# Acessar admin
# https://seu-dominio.com/admin/
# User: admin
# Pass: <DJANGO_SUPERUSER_PASSWORD do .env>
```

### 6. Configurar Renovação Automática SSL

```bash
# Criar cron job
crontab -e

# Adicionar linha (renova a cada 12h):
0 */12 * * * docker run --rm -v $(pwd)/certbot/conf:/etc/letsencrypt -v $(pwd)/certbot/www:/var/www/certbot certbot/certbot renew && docker-compose restart nginx
```

---

## 🔄 Atualizações e Manutenção

### Deploy de Atualizações

```bash
# 1. Pull do código mais recente
git pull origin main

# 2. Rebuild e restart
docker-compose down
docker-compose build
docker-compose up -d

# 3. Verificar logs
docker-compose logs -f web
```

### Backup do Banco de Dados

```bash
# Backup manual
docker exec gestao_db pg_dump -U postgres gestao_negocios > backup_$(date +%Y%m%d_%H%M%S).sql

# Restaurar backup
cat backup_20251221_120000.sql | docker exec -i gestao_db psql -U postgres gestao_negocios
```

### Backup Automático (Cron)

```bash
# Criar script de backup
cat > backup.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/var/backups/axio_gestto"
mkdir -p $BACKUP_DIR
docker exec gestao_db pg_dump -U postgres gestao_negocios | gzip > $BACKUP_DIR/backup_$(date +%Y%m%d_%H%M%S).sql.gz

# Manter apenas últimos 30 dias
find $BACKUP_DIR -name "backup_*.sql.gz" -mtime +30 -delete
EOF

chmod +x backup.sh

# Adicionar ao cron (diariamente às 2h)
crontab -e
0 2 * * * /caminho/para/backup.sh
```

### Logs

```bash
# Ver logs de todos os serviços
docker-compose logs -f

# Ver logs de um serviço específico
docker-compose logs -f web
docker-compose logs -f nginx
docker-compose logs -f celery

# Últimas 100 linhas
docker-compose logs --tail=100 web
```

### Reiniciar Serviços

```bash
# Reiniciar todos
docker-compose restart

# Reiniciar um serviço
docker-compose restart web
docker-compose restart nginx
docker-compose restart celery
```

---

## 🐛 Troubleshooting

### Erro: "Connection refused" no banco de dados

```bash
# Verificar se PostgreSQL está rodando
docker-compose ps db

# Verificar logs do PostgreSQL
docker-compose logs db

# Restart do banco
docker-compose restart db

# Aguardar healthcheck
docker-compose ps
```

### Erro: "Bad Gateway 502" no Nginx

```bash
# Verificar se web está rodando
docker-compose ps web

# Verificar logs do Django
docker-compose logs web

# Verificar se gunicorn está ouvindo
docker exec gestao_web netstat -tuln | grep 8000
```

### Erro: Migrações pendentes

```bash
# Aplicar migrações manualmente
docker exec -it gestao_web python manage.py migrate

# Verificar status das migrações
docker exec -it gestao_web python manage.py showmigrations
```

### Erro: Static files não aparecem

```bash
# Coletar static files
docker exec -it gestao_web python manage.py collectstatic --noinput

# Verificar permissões
docker exec -it gestao_web ls -la /app/staticfiles/
```

### Performance lenta

```bash
# Verificar uso de recursos
docker stats

# Aumentar workers do Gunicorn (editar docker-compose.yml)
# linha 41: --workers 5 (ao invés de 3)

# Restart
docker-compose restart web
```

---

## 🔒 Hardening de Segurança Pós-Deploy

### 1. Firewall UFW

```bash
# Instalar UFW
sudo apt install ufw

# Configurar regras
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow 22/tcp      # SSH
sudo ufw allow 80/tcp      # HTTP
sudo ufw allow 443/tcp     # HTTPS

# Ativar
sudo ufw enable

# Verificar status
sudo ufw status
```

### 2. Fail2Ban (proteção SSH)

```bash
# Instalar
sudo apt install fail2ban

# Configurar
sudo cp /etc/fail2ban/jail.conf /etc/fail2ban/jail.local
sudo nano /etc/fail2ban/jail.local

# Ativar
sudo systemctl enable fail2ban
sudo systemctl start fail2ban
```

### 3. Whitelist de IPs para Admin

Edite `nginx/nginx.conf`, adicione dentro de `location /admin/`:

```nginx
location /admin/ {
    # Permitir apenas IPs específicos
    allow 203.0.113.0/24;  # Seu IP de escritório
    allow 198.51.100.50;    # Seu IP VPN
    deny all;

    # ... resto da configuração
}
```

Depois: `docker-compose restart nginx`

---

## 📊 Monitoramento

### Health Check

```bash
# Criar script de monitoramento
cat > monitor.sh << 'EOF'
#!/bin/bash
HEALTH_URL="https://seu-dominio.com/health/"
STATUS=$(curl -s -o /dev/null -w "%{http_code}" $HEALTH_URL)

if [ $STATUS -ne 200 ]; then
  echo "ALERT: Health check failed with status $STATUS"
  # Enviar email/Slack/etc
fi
EOF

chmod +x monitor.sh

# Executar a cada 5 minutos
crontab -e
*/5 * * * * /caminho/para/monitor.sh
```

### Integração com Sentry (opcional)

```bash
# Adicionar ao requirements.txt
echo "sentry-sdk[django]==1.40.0" >> requirements.txt

# Adicionar ao settings.py
# import sentry_sdk
# sentry_sdk.init(
#     dsn="https://seu-dsn@sentry.io/projeto",
#     environment="production",
# )
```

---

## 🎯 Checklist Final

Antes de considerar o deploy completo:

- [ ] `.env` configurado com valores de produção
- [ ] Certificado SSL válido instalado
- [ ] HTTPS funcionando (redirect HTTP→HTTPS)
- [ ] Health check retornando 200 OK
- [ ] Admin acessível via HTTPS
- [ ] Login funcionando
- [ ] API bot testada
- [ ] Backup automático configurado
- [ ] Firewall configurado
- [ ] Domínio resolvendo corretamente
- [ ] Logs sendo gerados
- [ ] Monitoramento configurado

---

## 📞 Suporte

- Email: suporte@axiogesto.com
- Documentação: https://docs.axiogesto.com
- Issues: https://github.com/seu-usuario/axio_gestto/issues

---

**Boa sorte com seu deploy! 🚀**
