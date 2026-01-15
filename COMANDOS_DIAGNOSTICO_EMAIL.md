# Comandos de Diagnóstico de Email (Executar no Servidor via SSH)

## 1. Verificar Variáveis de Ambiente

```bash
cd /caminho/do/projeto
cat .env.prod | grep -E "EMAIL|DEFAULT_FROM|SITE_URL"
```

**O que verificar:**
- `EMAIL_BACKEND` deve ser `django.core.mail.backends.smtp.EmailBackend`
- `EMAIL_HOST` deve ser `smtp-relay.brevo.com`
- `EMAIL_PORT` deve ser `587`
- `EMAIL_USE_TLS` deve ser `True`
- `EMAIL_HOST_USER` deve ter um email válido
- `EMAIL_HOST_PASSWORD` deve ter a chave SMTP do Brevo
- `DEFAULT_FROM_EMAIL` deve estar configurado (ex: `Gestto <noreply@seudominio.com>`)

---

## 2. Testar Conexão SMTP (One-liner)

```bash
python -c "
import smtplib
import os
from decouple import config

host = config('EMAIL_HOST')
port = int(config('EMAIL_PORT'))
user = config('EMAIL_HOST_USER')
password = config('EMAIL_HOST_PASSWORD')

print(f'Testando conexão com {host}:{port}...')
try:
    smtp = smtplib.SMTP(host, port, timeout=10)
    smtp.starttls()
    smtp.login(user, password)
    print('✓ Conexão SMTP OK!')
    print('✓ Autenticação bem-sucedida!')
    smtp.quit()
except Exception as e:
    print(f'✗ Erro: {e}')
"
```

---

## 3. Testar Envio de Email via Django Shell (One-liner)

**IMPORTANTE:** Substitua `SEU_EMAIL@gmail.com` pelo seu email real!

```bash
python manage.py shell -c "
from django.core.mail import send_mail
from django.conf import settings
import traceback

try:
    print(f'Configuração atual:')
    print(f'  EMAIL_HOST: {settings.EMAIL_HOST}')
    print(f'  EMAIL_PORT: {settings.EMAIL_PORT}')
    print(f'  EMAIL_USE_TLS: {settings.EMAIL_USE_TLS}')
    print(f'  DEFAULT_FROM_EMAIL: {settings.DEFAULT_FROM_EMAIL}')
    print()
    print('Enviando email de teste...')
    
    result = send_mail(
        subject='[TESTE] Email do Gestto',
        message='Este é um email de teste. Se você recebeu, está funcionando!',
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=['SEU_EMAIL@gmail.com'],
        fail_silently=False,
    )
    
    print(f'✓ Email enviado com sucesso! (result={result})')
    print('Verifique sua caixa de entrada (e spam)')
except Exception as e:
    print(f'✗ Erro ao enviar email:')
    print(f'  Tipo: {type(e).__name__}')
    print(f'  Mensagem: {str(e)}')
    traceback.print_exc()
"
```

---

## 4. Verificar Logs de Erro Recentes

```bash
# Ver últimas 50 linhas do log
tail -50 logs/django.log

# Filtrar apenas erros de email
tail -100 logs/django.log | grep -i -E "email|smtp"

# Ver erros em tempo real
tail -f logs/django.log | grep -i error
```

---

## 5. Testar Cadastro Completo (Simular Cliente)

```bash
python manage.py shell -c "
from assinaturas.views import create_tenant
from rest_framework.test import APIRequestFactory
from rest_framework.request import Request
import json

factory = APIRequestFactory()

# Dados de teste - USE UM EMAIL REAL SEU!
data = {
    'company_name': 'Teste Email Debug',
    'email': 'SEU_EMAIL@gmail.com',
    'telefone': '11999999999',
    'cnpj': '12345678000199',
    'plano': 'essencial'
}

# Cria request
request = factory.post('/api/create-tenant/', data, format='json')
request = Request(request)

print('Criando tenant de teste...')
print(f'Email: {data[\"email\"]}')
print()

try:
    response = create_tenant(request)
    print(f'Status: {response.status_code}')
    print(f'Resposta: {json.dumps(response.data, indent=2, ensure_ascii=False)}')
    
    if response.status_code == 201:
        print()
        print('✓ Tenant criado com sucesso!')
        print('✓ Verifique se o email foi recebido')
    else:
        print()
        print('✗ Erro ao criar tenant')
except Exception as e:
    print(f'✗ Exceção: {type(e).__name__}: {str(e)}')
    import traceback
    traceback.print_exc()
"
```

---

## 6. Verificar se DEFAULT_FROM_EMAIL tem Nome

```bash
python manage.py shell -c "
from django.conf import settings
from email.utils import parseaddr

from_email = settings.DEFAULT_FROM_EMAIL
name, email = parseaddr(from_email)

print(f'DEFAULT_FROM_EMAIL: {from_email}')
print(f'  Nome do remetente: {name or \"(vazio)\"}')
print(f'  Email: {email}')
print()

if not name:
    print('⚠ AVISO: Nome do remetente não configurado!')
    print('  Para aparecer \"Gestto\" como remetente, configure:')
    print('  DEFAULT_FROM_EMAIL=Gestto <noreply@seudominio.com>')
else:
    print(f'✓ Nome do remetente configurado: {name}')
"
```

---

## 7. Comando Completo de Diagnóstico (Tudo de Uma Vez)

```bash
python manage.py shell -c "
from django.conf import settings
from django.core.mail import send_mail
import smtplib
import traceback

print('='*70)
print('DIAGNÓSTICO DE EMAIL - GESTTO')
print('='*70)
print()

# 1. Verificar configurações
print('1. CONFIGURAÇÕES:')
print(f'  EMAIL_BACKEND: {settings.EMAIL_BACKEND}')
print(f'  EMAIL_HOST: {settings.EMAIL_HOST}')
print(f'  EMAIL_PORT: {settings.EMAIL_PORT}')
print(f'  EMAIL_USE_TLS: {settings.EMAIL_USE_TLS}')
print(f'  EMAIL_HOST_USER: {settings.EMAIL_HOST_USER}')
print(f'  DEFAULT_FROM_EMAIL: {settings.DEFAULT_FROM_EMAIL}')
print()

# 2. Testar conexão SMTP
print('2. TESTE DE CONEXÃO SMTP:')
try:
    smtp = smtplib.SMTP(settings.EMAIL_HOST, settings.EMAIL_PORT, timeout=10)
    smtp.starttls()
    smtp.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)
    print('  ✓ Conexão SMTP OK!')
    print('  ✓ Autenticação bem-sucedida!')
    smtp.quit()
except Exception as e:
    print(f'  ✗ Erro: {type(e).__name__}: {str(e)}')

print()
print('3. TESTE DE ENVIO:')
print('  Digite um email para teste (ou deixe vazio para pular):')
"
```

---

## Interpretação dos Resultados

### ✅ Tudo OK
Se todos os testes passarem, o problema pode ser:
1. **Limite do Brevo atingido** - Verifique em https://app.brevo.com
2. **Email indo para spam** - Configure SPF/DKIM
3. **Erro no código** - Verifique logs durante cadastro real

### ❌ Erro de Autenticação
- Credenciais do Brevo incorretas
- Gere nova SMTP Key em https://app.brevo.com

### ❌ Erro de Conexão
- Firewall bloqueando porta 587
- Execute: `sudo ufw allow 587/tcp`

### ❌ Variável Não Configurada
- Adicione a variável faltando no `.env.prod`
- Reinicie a aplicação: `docker-compose restart` ou `systemctl restart gestto`

---

## Após Fazer Mudanças no .env.prod

**SEMPRE reinicie a aplicação:**

```bash
# Se usando Docker
docker-compose restart

# Se usando systemd
sudo systemctl restart gestto

# Ou kill do gunicorn
pkill -HUP gunicorn
```

---

## Comandos Rápidos de Verificação

```bash
# Ver se processo está rodando
ps aux | grep gunicorn

# Ver portas abertas
netstat -tuln | grep 587

# Testar DNS
nslookup smtp-relay.brevo.com

# Testar conectividade
telnet smtp-relay.brevo.com 587
```
