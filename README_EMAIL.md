# Configuração de Email - Axio Gestto

## 📧 Emails Automáticos

Este sistema envia emails automaticamente quando:
- ✉️ **Cliente compra assinatura** → Email com senha temporária e instruções
- ✉️ **Nova empresa é cadastrada** → Email de confirmação
- ✉️ **Usuário manual é criado** → Email de boas-vindas (sem senha)
- ✉️ **Recuperação de senha** → Email com link de reset

### 🎯 Dois Tipos de Email de Boas-Vindas

**1. Via Assinatura (COM SENHA):**
- Template HTML profissional
- Senha temporária incluída
- Informações do plano
- Próximos passos

**2. Usuário Manual (SEM SENHA):**
- Template HTML simples
- Sem senha (definida pelo admin)
- Informações básicas

📖 **Documentação completa:** `docs/SISTEMA_EMAIL_INTEGRADO.md`

---

## Opção 1: Brevo (RECOMENDADO) - 300 emails grátis/dia

### Configuração Rápida (5 minutos)

1. **Criar conta:** https://www.brevo.com
2. **Gerar SMTP Key:** Settings → SMTP & API → Generate SMTP Key
3. **Configurar remetente:** Settings → Senders & IP → Add a sender
4. **Configurar .env:**

```env
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp-relay.brevo.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=seu-email@exemplo.com
EMAIL_HOST_PASSWORD=sua-smtp-key-aqui
DEFAULT_FROM_EMAIL=noreply@seudominio.com
```

5. **Testar:**
```bash
python configurar_brevo.py
```

### Documentação Completa
📖 Leia: `docs/CONFIGURACAO_EMAIL_BREVO.md`

---

## Opção 2: Gmail - 500 emails/dia

### Configuração

1. **Criar senha de app:** https://myaccount.google.com/apppasswords
2. **Configurar .env:**

```env
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=seu-email@gmail.com
EMAIL_HOST_PASSWORD=xxxx-xxxx-xxxx-xxxx
DEFAULT_FROM_EMAIL=noreply@seudominio.com
```

---

## Opção 3: Zoho Mail - Grátis até 5 usuários

### Configuração

1. **Criar conta:** https://www.zoho.com/mail/
2. **Configurar .env:**

```env
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.zoho.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=noreply@seudominio.com
EMAIL_HOST_PASSWORD=sua-senha-zoho
DEFAULT_FROM_EMAIL=noreply@seudominio.com
```

---

## Opção 4: Console (Desenvolvimento)

Para desenvolvimento local, os emails aparecem no terminal:

```env
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
EMAIL_HOST=
EMAIL_PORT=
EMAIL_USE_TLS=
EMAIL_HOST_USER=
EMAIL_HOST_PASSWORD=
DEFAULT_FROM_EMAIL=noreply@axiogesto.com
```

---

## Scripts Disponíveis

### 1. Configurar Brevo
```bash
python configurar_brevo.py
```
Valida credenciais e testa conexão SMTP.

### 2. Testar Sistema de Emails Integrado (RECOMENDADO)
```bash
python testar_email_assinatura.py
```
Testa o fluxo completo:
- Email via assinatura COM senha
- Email manual SEM senha
- Prevenção de duplicação

### 3. Testar Todos os Templates
```bash
python testar_emails.py
```
Testa todos os templates e signals básicos.

---

## Templates de Email

Os templates HTML estão em `templates/emails/`:

- `boas_vindas_com_senha.html` - Email de boas-vindas VIA ASSINATURA (com senha)
- `usuario_boas_vindas.html` - Email de boas-vindas MANUAL (sem senha)
- `empresa_criada.html` - Email de confirmação de cadastro de empresa
- `password_reset_email.html` - Email de recuperação de senha

### Personalizar Templates

Você pode editar os templates para:
- Alterar cores (variáveis CSS no `<style>`)
- Adicionar logo da empresa
- Modificar textos
- Adicionar mais informações

---

## Signals (Disparo Automático)

Os emails são enviados automaticamente através de Django Signals:

- `core/signals.py` → Envia email ao criar usuário
- `empresas/signals.py` → Envia email ao criar empresa

### Como funciona:

```python
# Quando você cria um usuário
usuario = Usuario.objects.create(
    username='joao',
    email='joao@exemplo.com',
    ...
)
# ↑ Signal dispara automaticamente e envia email de boas-vindas
```

---

## Comparação de Provedores

| Provedor | Emails Grátis | Configuração | Velocidade | Recomendado |
|----------|---------------|--------------|------------|-------------|
| **Brevo** | 300/dia | ⭐⭐⭐⭐⭐ | Rápido | ✅ Sim |
| Gmail | 500/dia | ⭐⭐⭐⭐ | Médio | Para testes |
| Zoho | Ilimitado* | ⭐⭐⭐ | Lento | Domínio próprio |
| SendGrid | 100/dia | ⭐⭐⭐ | Rápido | Alternativa |

\* *Com domínio próprio*

---

## Troubleshooting

### Emails não estão sendo enviados
1. Verifique o console/logs do Django para erros
2. Execute `python testar_emails.py` para diagnóstico
3. Verifique se as credenciais estão corretas no `.env`

### Emails vão para spam
1. Configure SPF e DKIM no DNS do seu domínio
2. Use um remetente com domínio próprio (não @gmail.com)
3. Verifique reputação do domínio

### Erro de autenticação
1. Para Gmail: Certifique-se de usar "Senha de App", não a senha normal
2. Para Brevo: Gere uma nova SMTP Key
3. Verifique se `EMAIL_HOST_USER` está correto

---

## Suporte

- 📖 Documentação Brevo: https://developers.brevo.com/docs
- 🆘 Issues do projeto: https://github.com/seu-repo/issues
- 💬 Contato: contato@axiogesto.com
