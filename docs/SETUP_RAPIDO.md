# ⚡ Setup Rápido - Gestto Produção

Guia simplificado para colocar o Gestto no ar em **menos de 10 minutos**.

---

## 🎯 Checklist Rápido

### ✅ Pré-requisitos (você já tem)

- [x] VPS Hostinger configurado
- [x] Conta Supabase (PostgreSQL)
- [x] Conta Brevo (SMTP)
- [x] Domínio `app.gestto.app.br` apontado para o VPS
- [x] `.env.production` configurado localmente

---

## 🚀 Deploy em 5 Passos

### 1️⃣ Acessar servidor VPS

```bash
ssh usuario@72.61.56.252
```

### 2️⃣ Instalar Docker (script automático)

```bash
# Download e execução do script de instalação do Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Instalar Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.24.5/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# IMPORTANTE: Fazer logout e login novamente para aplicar permissões do Docker
exit
```

Após fazer logout, conecte novamente:

```bash
ssh usuario@72.61.56.252
```

### 3️⃣ Clonar repositório e configurar

```bash
# Criar diretório e clonar projeto
sudo mkdir -p /var/www/gestto
sudo chown -R $USER:$USER /var/www/gestto
cd /var/www/gestto

# Clonar repositório (ALTERE para sua URL do GitHub)
git clone https://github.com/SEU_USUARIO/axio_gestto.git .

# Criar arquivo .env.production
nano .env.production
```

**Cole o conteúdo do seu `.env.production` local** e salve (`Ctrl+O`, `Enter`, `Ctrl+X`).

### 4️⃣ Subir aplicação

```bash
cd /var/www/gestto

# Build e iniciar containers
docker-compose -f docker-compose.prod.yml build
docker-compose -f docker-compose.prod.yml up -d

# Ver logs em tempo real (Ctrl+C para sair)
docker-compose -f docker-compose.prod.yml logs -f
```

### 5️⃣ Configurar GitHub Actions (CI/CD)

**No GitHub Repository:**

1. Vá em: **Settings → Secrets and variables → Actions**
2. Adicione 3 secrets:

| Nome              | Valor                              |
|-------------------|------------------------------------|
| `DEPLOY_HOST`     | `72.61.56.252`                     |
| `DEPLOY_USER`     | Seu usuário SSH do servidor        |
| `DEPLOY_SSH_KEY`  | Chave privada SSH (ver abaixo ↓)   |

**Gerar chave SSH (no seu PC local):**

```bash
# Gerar chave
ssh-keygen -t ed25519 -C "deploy@gestto" -f ~/.ssh/gestto_deploy

# Copiar chave pública para o servidor
ssh-copy-id -i ~/.ssh/gestto_deploy.pub usuario@72.61.56.252

# Exibir chave privada (copiar TODO o conteúdo)
cat ~/.ssh/gestto_deploy
```

Cole a chave privada inteira no secret `DEPLOY_SSH_KEY` do GitHub.

---

## ✅ Testar Deploy

### 1. Health Check

```bash
curl http://app.gestto.app.br/health/
# Esperado: {"status": "ok"}
```

### 2. Acessar Admin Django

```
http://app.gestto.app.br/admin/
```

**Login:**
- Usuário: `admin`
- Senha: `Admin@Gestto2025!Secure`

### 3. Deploy automático via Git

Agora qualquer commit na branch `main` faz deploy automático! 🎉

```bash
git add .
git commit -m "feat: minha alteração"
git push origin main

# GitHub Actions vai fazer deploy automaticamente!
```

---

## 🔒 Configurar HTTPS (Opcional mas Recomendado)

### Opção mais fácil: **Cloudflare**

1. Adicionar domínio no Cloudflare
2. Configurar DNS:
   - `A` `app.gestto.app.br` → `72.61.56.252`
   - `A` `gestto.app.br` → `72.61.56.252`
3. SSL/TLS → "Flexible" ou "Full"
4. Pronto! Cloudflare gerencia certificados automaticamente.

### Alternativa: **Let's Encrypt** (no servidor)

```bash
# Instalar Certbot
sudo apt install -y certbot

# Gerar certificado
sudo certbot certonly --standalone -d app.gestto.app.br -d gestto.app.br

# Copiar certificados para o Nginx
sudo mkdir -p /var/www/gestto/nginx/ssl
sudo cp /etc/letsencrypt/live/app.gestto.app.br/fullchain.pem /var/www/gestto/nginx/ssl/cert.pem
sudo cp /etc/letsencrypt/live/app.gestto.app.br/privkey.pem /var/www/gestto/nginx/ssl/key.pem

# Reiniciar Nginx
cd /var/www/gestto
docker-compose -f docker-compose.prod.yml restart nginx
```

---

## 📊 Comandos Úteis

```bash
# Ver status dos containers
docker-compose -f docker-compose.prod.yml ps

# Ver logs
docker-compose -f docker-compose.prod.yml logs -f

# Reiniciar aplicação
docker-compose -f docker-compose.prod.yml restart

# Parar tudo
docker-compose -f docker-compose.prod.yml down

# Rebuild completo
docker-compose -f docker-compose.prod.yml build --no-cache
docker-compose -f docker-compose.prod.yml up -d
```

---

## 🎉 Pronto!

Sua aplicação está no ar em: **http://app.gestto.app.br**

**Próximos passos:**
- ✅ Configurar HTTPS (Cloudflare ou Let's Encrypt)
- ✅ Testar todas as funcionalidades
- ✅ Fazer primeiro commit para testar CI/CD

**Documentação completa:** Ver arquivo `DEPLOY.md`

---

## 🆘 Problemas?

### Container não inicia:
```bash
docker-compose -f docker-compose.prod.yml logs web
```

### Erro de conexão com banco:
Verificar `.env.production` → variável `DATABASE_URL` do Supabase

### Erro 502 (Bad Gateway):
```bash
docker-compose -f docker-compose.prod.yml restart web nginx
```

### Reset completo:
```bash
cd /var/www/gestto
docker-compose -f docker-compose.prod.yml down -v
docker-compose -f docker-compose.prod.yml build --no-cache
docker-compose -f docker-compose.prod.yml up -d
```
