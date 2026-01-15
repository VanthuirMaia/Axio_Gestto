# Troubleshooting: Emails Não Sendo Enviados

## Guia Rápido de Diagnóstico

### 1. Execute o Script de Diagnóstico

No servidor de produção, execute:

```bash
cd /caminho/do/projeto
python diagnostico_email_producao.py
```

Este script irá:
- ✅ Verificar todas as variáveis de ambiente
- ✅ Testar conexão SMTP com Brevo
- ✅ Enviar email de teste
- ✅ Analisar logs de erro

### 2. Problemas Comuns e Soluções

#### Problema: "EMAIL_HOST não configurado"

**Causa**: Variável `EMAIL_HOST` faltando no `.env.prod`

**Solução**:
```bash
# Adicione ao .env.prod
EMAIL_HOST=smtp-relay.brevo.com
```

#### Problema: "DEFAULT_FROM_EMAIL não configurado"

**Causa**: Variável `DEFAULT_FROM_EMAIL` faltando no `.env.prod`

**Solução**:
```bash
# Adicione ao .env.prod
DEFAULT_FROM_EMAIL=Gestto <noreply@seudominio.com>
```

> **Nota**: O formato `Nome <email@dominio.com>` faz com que "Nome" apareça como remetente.

#### Problema: "Falha na autenticação SMTP"

**Causa**: Credenciais do Brevo incorretas

**Solução**:
1. Acesse [https://app.brevo.com](https://app.brevo.com)
2. Vá em **Settings** → **SMTP & API**
3. Copie as credenciais corretas:
   - **SMTP Server**: `smtp-relay.brevo.com`
   - **Port**: `587`
   - **Login**: Seu email cadastrado no Brevo
   - **SMTP Key**: Gere uma nova chave se necessário

```bash
# Atualize no .env.prod
EMAIL_HOST_USER=seu-email@dominio.com
EMAIL_HOST_PASSWORD=sua-smtp-key-do-brevo
```

#### Problema: "Timeout ao conectar ao servidor SMTP"

**Causa**: Firewall bloqueando porta 587

**Solução**:
```bash
# Teste se a porta está acessível
telnet smtp-relay.brevo.com 587

# Se não funcionar, verifique firewall
sudo ufw allow 587/tcp
```

#### Problema: Emails não chegam (sem erro)

**Possíveis causas**:
1. **Limite do Brevo atingido** (300 emails/dia no plano gratuito)
2. **Email indo para spam**
3. **Domínio não verificado no Brevo**

**Soluções**:

**1. Verificar limite do Brevo:**
- Acesse dashboard do Brevo
- Veja quantos emails foram enviados hoje
- Upgrade de plano se necessário

**2. Evitar spam:**
```bash
# Configure SPF e DKIM no seu domínio
# No painel do seu provedor de DNS, adicione:

# SPF Record (TXT)
v=spf1 include:spf.brevo.com ~all

# DKIM - Copie do Brevo em Settings → Senders & IP
```

**3. Verificar domínio:**
- No Brevo, vá em **Senders & IP** → **Domains**
- Adicione e verifique seu domínio

### 3. Verificar Logs em Produção

```bash
# Ver logs em tempo real
tail -f logs/django.log

# Filtrar apenas emails
tail -f logs/django.log | grep -i email

# Ver últimos erros
tail -100 logs/django.log | grep ERROR
```

### 4. Testar Envio Manual via Django Shell

```bash
python manage.py shell
```

```python
from django.core.mail import send_mail
from django.conf import settings

# Teste simples
send_mail(
    subject='Teste Manual',
    message='Corpo do email',
    from_email=settings.DEFAULT_FROM_EMAIL,
    recipient_list=['seu-email@gmail.com'],
    fail_silently=False,
)

# Se funcionar, você verá: 1
# Se falhar, verá a mensagem de erro
```

### 5. Checklist de Configuração Completa

Verifique se todas estas variáveis estão no `.env.prod`:

```bash
# Email Configuration
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp-relay.brevo.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=seu-email@dominio.com
EMAIL_HOST_PASSWORD=sua-smtp-key-brevo
DEFAULT_FROM_EMAIL=Gestto <noreply@seudominio.com>

# Site URL (importante para links de ativação)
SITE_URL=https://seudominio.com
```

### 6. Reiniciar Aplicação Após Mudanças

Após alterar o `.env.prod`, sempre reinicie:

```bash
# Se usando Docker
docker-compose restart

# Se usando Gunicorn diretamente
sudo systemctl restart gestto

# Ou
pkill -HUP gunicorn
```

### 7. Monitoramento Contínuo

Configure alertas para falhas de email:

```python
# Em settings/prod.py
ADMINS = [('Admin', 'admin@seudominio.com')]

# Django enviará emails de erro para os admins
```

## Comandos Úteis

```bash
# Verificar configuração atual
python manage.py shell -c "from django.conf import settings; print(f'Host: {settings.EMAIL_HOST}'); print(f'Port: {settings.EMAIL_PORT}'); print(f'From: {settings.DEFAULT_FROM_EMAIL}')"

# Testar envio rápido
python diagnostico_email_producao.py

# Ver logs de email
grep -i "email" logs/django.log | tail -20

# Verificar se processo está rodando
ps aux | grep gunicorn

# Verificar portas abertas
netstat -tuln | grep 587
```

## Suporte

Se o problema persistir após seguir este guia:

1. Execute `python diagnostico_email_producao.py` e salve a saída
2. Colete os últimos 100 linhas do log: `tail -100 logs/django.log > debug.log`
3. Entre em contato com o suporte com estes arquivos
