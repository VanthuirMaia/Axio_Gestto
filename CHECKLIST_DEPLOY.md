# ✅ Checklist de Deploy - Gestto

Use este checklist para garantir que tudo está configurado corretamente antes e depois do deploy.

---

## 📋 Pré-Deploy (Preparação)

### 1. Configurações Locais

- [ ] ✅ `.env` configurado para desenvolvimento (SQLite)
- [ ] ✅ `.env.production` criado com dados reais
- [ ] ✅ `.env.production` NÃO está no Git (.gitignore)
- [ ] ✅ Arquivo `.env.production` testado localmente
- [ ] ✅ `requirements.txt` atualizado com todas as dependências
- [ ] ✅ Código testado em desenvolvimento

### 2. Credenciais e Serviços Externos

- [ ] ✅ Conta Supabase criada
  - [ ] Connection String obtida
  - [ ] Connection Pooler habilitado (porta 6543)
  - [ ] IP do VPS adicionado às regras do firewall (se necessário)

- [ ] ✅ Conta Brevo criada
  - [ ] SMTP configurado
  - [ ] Credenciais obtidas
  - [ ] Email de origem verificado

- [ ] ✅ Evolution API configurada
  - [ ] URL da API obtida
  - [ ] API Key obtida

- [ ] ✅ n8n configurado (opcional)
  - [ ] Webhook URL obtida
  - [ ] API Key gerada

- [ ] ✅ Stripe configurado (se usar pagamentos)
  - [ ] Public Key obtida
  - [ ] Secret Key obtida
  - [ ] Webhook Secret configurado

### 3. Domínio e DNS

- [ ] ✅ Domínio registrado (`app.gestto.app.br`)
- [ ] ✅ DNS apontado para IP do VPS (`72.61.56.252`)
- [ ] ✅ Registro A configurado
- [ ] ✅ TTL baixo (para mudanças rápidas, opcional)

### 4. VPS/Servidor

- [ ] ✅ VPS Hostinger contratado
- [ ] ✅ Ubuntu 20.04+ instalado
- [ ] ✅ Acesso SSH funcionando
- [ ] ✅ IP estático configurado
- [ ] ✅ Firewall configurado (portas 22, 80, 443)

### 5. GitHub

- [ ] ✅ Repositório criado/atualizado
- [ ] ✅ Branch `main` definida como principal
- [ ] ✅ Secrets configurados no GitHub Actions:
  - [ ] `DEPLOY_HOST`
  - [ ] `DEPLOY_USER`
  - [ ] `DEPLOY_SSH_KEY`

---

## 🚀 Durante o Deploy

### 1. Setup do Servidor

- [ ] ✅ SSH funcionando: `ssh usuario@72.61.56.252`
- [ ] ✅ Docker instalado: `docker --version`
- [ ] ✅ Docker Compose instalado: `docker-compose --version`
- [ ] ✅ Usuário adicionado ao grupo docker
- [ ] ✅ Diretório `/var/www/gestto` criado
- [ ] ✅ Repositório clonado

### 2. Configuração de Ambiente

- [ ] ✅ Arquivo `.env.production` criado no servidor
- [ ] ✅ Todas as variáveis preenchidas (sem valores de exemplo)
- [ ] ✅ Permissões corretas: `chmod 600 .env.production`

### 3. Build e Deploy

- [ ] ✅ Build executado sem erros
- [ ] ✅ Containers iniciados: `docker-compose -f docker-compose.prod.yml up -d`
- [ ] ✅ Todos os 5 containers rodando (nginx, web, redis, celery, celery-beat)
- [ ] ✅ Logs sem erros críticos

### 4. Migrations e Dados

- [ ] ✅ Migrations executadas: `python manage.py migrate`
- [ ] ✅ Arquivos estáticos coletados: `collectstatic`
- [ ] ✅ Superuser criado
- [ ] ✅ Dados iniciais carregados (se houver)

---

## ✅ Pós-Deploy (Verificação)

### 1. Testes Básicos

- [ ] ✅ Health check funcionando:
  ```bash
  curl http://app.gestto.app.br/health/
  # Esperado: {"status": "ok"}
  ```

- [ ] ✅ Nginx respondendo (HTTP):
  ```bash
  curl -I http://app.gestto.app.br
  # Esperado: HTTP/1.1 301 (redirect para HTTPS)
  ```

- [ ] ✅ Aplicação acessível via navegador

### 2. Funcionalidades Django

- [ ] ✅ Admin Django acessível: `/admin/`
- [ ] ✅ Login no admin funcionando
- [ ] ✅ Dashboard carregando sem erros
- [ ] ✅ Arquivos estáticos carregando (CSS/JS)
- [ ] ✅ Upload de imagens funcionando

### 3. Banco de Dados

- [ ] ✅ Conexão com Supabase estabelecida
- [ ] ✅ Queries funcionando corretamente
- [ ] ✅ Dados sendo salvos e recuperados
- [ ] ✅ Sem erros de conexão nos logs

### 4. Email

- [ ] ✅ Teste de envio de email:
  ```python
  from django.core.mail import send_mail
  send_mail('Test', 'Teste Gestto', 'contato@gestto.app.br', ['seu@email.com'])
  ```
- [ ] ✅ Email recebido corretamente
- [ ] ✅ Recuperação de senha funcionando

### 5. Integrações Externas

- [ ] ✅ Evolution API respondendo
- [ ] ✅ Webhooks configurados e funcionando
- [ ] ✅ n8n recebendo requisições (se configurado)
- [ ] ✅ Stripe webhooks ativos (se configurado)

### 6. Celery e Tarefas Assíncronas

- [ ] ✅ Celery worker rodando
- [ ] ✅ Celery beat rodando (tarefas agendadas)
- [ ] ✅ Tarefas sendo processadas
- [ ] ✅ Logs do Celery sem erros

### 7. Segurança

- [ ] ✅ HTTPS funcionando (certificado válido)
- [ ] ✅ Redirect HTTP → HTTPS funcionando
- [ ] ✅ Headers de segurança presentes:
  ```bash
  curl -I https://app.gestto.app.br | grep -i "strict-transport"
  ```
- [ ] ✅ Rate limiting funcionando (testar múltiplas requisições)
- [ ] ✅ Admin protegido contra brute force

### 8. Performance

- [ ] ✅ Arquivos estáticos servidos pelo Nginx (não Django)
- [ ] ✅ Cache de arquivos estáticos funcionando
- [ ] ✅ Tempo de resposta aceitável (< 2s)
- [ ] ✅ Sem memory leaks (monitorar por 1 hora)

### 9. Logs e Monitoramento

- [ ] ✅ Logs acessíveis:
  ```bash
  docker-compose -f docker-compose.prod.yml logs -f
  ```
- [ ] ✅ Sem erros 500 nos logs
- [ ] ✅ Sem avisos críticos
- [ ] ✅ Logs estruturados e legíveis

### 10. CI/CD

- [ ] ✅ GitHub Actions executando com sucesso
- [ ] ✅ Deploy automático funcionando ao push na `main`
- [ ] ✅ Testes automatizados passando
- [ ] ✅ Rollback possível (se necessário)

---

## 🔒 Segurança Adicional (Recomendado)

- [ ] ⚠️ Alterar senha do superuser padrão
- [ ] ⚠️ Configurar 2FA no admin (se disponível)
- [ ] ⚠️ Configurar firewall UFW:
  ```bash
  sudo ufw enable
  sudo ufw allow 22/tcp
  sudo ufw allow 80/tcp
  sudo ufw allow 443/tcp
  ```
- [ ] ⚠️ Configurar fail2ban (proteção SSH)
- [ ] ⚠️ Desabilitar login SSH como root
- [ ] ⚠️ Configurar backups automáticos
- [ ] ⚠️ Adicionar monitoramento (Sentry, UptimeRobot)

---

## 🎯 Otimizações Pós-Deploy (Opcional)

- [ ] 🔧 Configurar CDN (Cloudflare)
- [ ] 🔧 Ativar Cloudflare cache
- [ ] 🔧 Configurar object storage (S3/Cloudflare R2) para media
- [ ] 🔧 Adicionar Redis Sentinel (alta disponibilidade)
- [ ] 🔧 Configurar backup automático do Supabase
- [ ] 🔧 Adicionar monitoramento de uptime
- [ ] 🔧 Configurar alertas (email/Slack) para erros
- [ ] 🔧 Otimizar queries do banco (indexação)
- [ ] 🔧 Adicionar caching de views Django
- [ ] 🔧 Configurar load balancer (se necessário)

---

## 🆘 Troubleshooting

### Container não inicia
```bash
docker-compose -f docker-compose.prod.yml logs web
docker-compose -f docker-compose.prod.yml build --no-cache web
docker-compose -f docker-compose.prod.yml up -d
```

### Erro 502 Bad Gateway
```bash
docker-compose -f docker-compose.prod.yml restart web nginx
docker-compose -f docker-compose.prod.yml logs -f nginx
```

### Banco não conecta
```bash
# Verificar variáveis
docker-compose -f docker-compose.prod.yml exec web env | grep DB_

# Testar conexão
docker-compose -f docker-compose.prod.yml exec web python manage.py dbshell
```

### Migrations não rodam
```bash
docker-compose -f docker-compose.prod.yml exec web python manage.py migrate --fake-initial
```

### Arquivos estáticos não carregam
```bash
docker-compose -f docker-compose.prod.yml exec web python manage.py collectstatic --noinput
docker-compose -f docker-compose.prod.yml restart nginx
```

---

## 📊 Métricas de Sucesso

Após deploy completo, você deve ter:

- ✅ Uptime > 99%
- ✅ Tempo de resposta < 2s
- ✅ 0 erros 500
- ✅ HTTPS com A+ no SSL Labs
- ✅ Backups automáticos configurados
- ✅ Monitoramento ativo
- ✅ Deploy automático via Git
- ✅ Documentação completa

---

## 🎉 Deploy Finalizado!

**Parabéns!** Se todos os itens acima estão marcados, seu deploy foi um sucesso! 🚀

**Próximos passos:**
1. Monitorar aplicação por 24-48h
2. Ajustar recursos conforme necessário
3. Implementar melhorias contínuas
4. Adicionar testes automatizados
5. Configurar alertas de monitoramento

**Mantenha sempre atualizado:**
- Dependências Python (`pip list --outdated`)
- Imagens Docker (`docker images`)
- Sistema operacional (`apt update && apt upgrade`)
- Certificados SSL (renovação automática)
