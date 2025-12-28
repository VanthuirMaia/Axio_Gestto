# Sistema de Email Integrado - Axio Gestto

## 📧 Como Funciona

O sistema possui **dois fluxos de email** diferentes dependendo de como o usuário foi criado:

---

## 🎯 Fluxo 1: Usuário via Assinatura (COM SENHA)

**Quando acontece:** Cliente compra o sistema ou cria conta via checkout

**O que é enviado:**
- ✅ Email HTML bonito e profissional
- ✅ **Senha temporária incluída**
- ✅ Informações do plano contratado
- ✅ Trial days e data de expiração
- ✅ Próximos passos para configurar o sistema

**Template usado:** `templates/emails/boas_vindas_com_senha.html`

**Código responsável:** `assinaturas/views.py` → função `_enviar_email_boas_vindas()`

### Exemplo de email:

```
🎉 Bem-vindo ao Gestto!

Olá, Salão Bela Vida!

🔐 Suas Credenciais de Acesso
  Email: contato@belavida.com
  Senha: Abc123XyZ!@#

⚠️ IMPORTANTE: Altere sua senha no primeiro acesso!

🎁 Período de Teste Grátis
  Plano Essencial: 7 dias grátis

📋 Próximos Passos (5 minutos)
  1️⃣ Faça login com suas credenciais
  2️⃣ Configure seus serviços
  3️⃣ Cadastre seus profissionais
  4️⃣ Conecte seu WhatsApp
  5️⃣ Pronto! Comece a receber agendamentos 🚀
```

---

## 👤 Fluxo 2: Usuário Manual (SEM SENHA)

**Quando acontece:** Admin cria usuário manualmente no sistema (sem empresa associada)

**O que é enviado:**
- ✅ Email HTML simples
- ❌ **Senha NÃO incluída** (o admin define a senha manualmente)
- ✅ Informações básicas de acesso

**Template usado:** `templates/emails/usuario_boas_vindas.html`

**Código responsável:** `core/signals.py` → signal `enviar_email_boas_vindas()`

### Exemplo de email:

```
Bem-vindo ao Axio Gestto!

Olá, João Silva!

Sua conta foi criada com sucesso!

Suas credenciais de acesso:
  Usuário: joao.silva
  Email: joao@exemplo.com

[Acessar o Sistema]
```

---

## 🚫 Prevenção de Duplicação

O sistema **previne emails duplicados** da seguinte forma:

### Signal Inteligente (`core/signals.py`)

```python
@receiver(post_save, sender=Usuario)
def enviar_email_boas_vindas(sender, instance, created, **kwargs):
    if created:
        # ⚠️ Se o usuário tem empresa, significa que foi criado via assinatura
        # Nesse caso, o email já foi enviado pela função de assinatura
        if instance.empresa:
            return  # 🚫 Não envia email duplicado!

        # ✅ Usuário manual (sem empresa) - envia email padrão
        # ...
```

---

## 📁 Estrutura de Templates

```
templates/emails/
├── boas_vindas_com_senha.html     # Email de assinatura COM senha
├── usuario_boas_vindas.html       # Email manual SEM senha
├── empresa_criada.html            # Email de confirmação de empresa
└── password_reset_email.html      # Email de recuperação de senha
```

---

## 🔄 Fluxo Completo de Assinatura

### Quando um cliente compra o sistema:

1. **POST** `/api/create-tenant/`
   ```json
   {
     "company_name": "Salão Bela Vida",
     "email": "contato@belavida.com",
     "telefone": "11999999999",
     "cnpj": "12345678000199"
   }
   ```

2. **Sistema cria:**
   - ✅ Empresa
   - ✅ Assinatura (trial)
   - ✅ Usuário admin com senha temporária

3. **Emails enviados:**
   - 📧 Email 1: Empresa criada (signal `empresas/signals.py`)
   - 📧 Email 2: Boas-vindas COM SENHA (função `_enviar_email_boas_vindas()`)

4. **Cliente recebe:**
   - Email com as credenciais completas
   - Senha temporária para primeiro acesso
   - Instruções de configuração

---

## 🧪 Como Testar

### Teste Completo
```bash
python testar_email_assinatura.py
```

**O script testa:**
1. ✅ Email via assinatura (COM senha)
2. ✅ Email manual (SEM senha)
3. ✅ Prevenção de duplicação
4. ✅ Verificação de templates

### Teste Rápido
```bash
python testar_emails.py
```

---

## ⚙️ Configuração

### Desenvolvimento (Console)
```env
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
```
Emails aparecem no terminal

### Produção (Brevo/SMTP)
```env
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp-relay.brevo.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=seu-email@exemplo.com
EMAIL_HOST_PASSWORD=sua-smtp-key
DEFAULT_FROM_EMAIL=noreply@seudominio.com
```

---

## 📊 Comparação de Fluxos

| Característica | Via Assinatura | Manual |
|----------------|----------------|--------|
| **Template** | `boas_vindas_com_senha.html` | `usuario_boas_vindas.html` |
| **Senha incluída** | ✅ Sim | ❌ Não |
| **Plano incluído** | ✅ Sim | ❌ Não |
| **Trial info** | ✅ Sim | ❌ Não |
| **Empresa** | ✅ Obrigatório | ❌ Opcional |
| **Próximos passos** | ✅ Sim | ❌ Não |
| **Acionado por** | Função manual | Signal automático |

---

## 🔧 Manutenção

### Adicionar novo campo ao email de assinatura

1. Editar `templates/emails/boas_vindas_com_senha.html`
2. Adicionar variável no contexto em `assinaturas/views.py`:

```python
context = {
    'usuario': usuario,
    'empresa': empresa,
    'senha_temporaria': senha,
    'plano': plano,
    'novo_campo': 'valor',  # ← Adicionar aqui
}
```

### Personalizar textos

Edite os templates HTML em `templates/emails/`

### Mudar remetente

Configure `DEFAULT_FROM_EMAIL` no `.env`

---

## 🐛 Troubleshooting

### Email duplicado sendo enviado

**Causa:** Signal não está verificando `instance.empresa`

**Solução:** Verifique `core/signals.py` linha 22:
```python
if instance.empresa:
    return  # Deve estar presente!
```

### Senha não aparece no email

**Causa:** Template errado ou contexto faltando

**Solução:** Verifique se está usando `boas_vindas_com_senha.html` e se `senha_temporaria` está no contexto

### Email não está sendo enviado

**Causa:** Signal ou função não está sendo executada

**Solução:**
1. Verifique logs do Django
2. Execute `python testar_email_assinatura.py`
3. Verifique se `apps.py` tem `ready()` method

---

## 📝 Checklist de Implementação

- [x] Template HTML de boas-vindas com senha
- [x] Template HTML de boas-vindas sem senha
- [x] Signal para usuários manuais
- [x] Função para usuários de assinatura
- [x] Prevenção de duplicação
- [x] Script de testes
- [x] Documentação
- [x] Integração com Brevo/SMTP
- [x] Suporte a fallback (texto puro)

---

## 🎓 Conceitos Técnicos

### Django Signals
Eventos que disparam automaticamente quando algo acontece no Django (ex: criar usuário)

### Template Context
Variáveis passadas para o template HTML (ex: `{{ usuario.email }}`)

### HTML Email
Email com formatação rica (cores, botões, etc.) vs texto puro

### Fallback
Versão texto puro para clientes de email que não suportam HTML

---

## 📚 Referências

- Django Email: https://docs.djangoproject.com/en/5.0/topics/email/
- Django Signals: https://docs.djangoproject.com/en/5.0/topics/signals/
- Brevo SMTP: https://developers.brevo.com/docs/send-email-via-smtp
- Template Rendering: https://docs.djangoproject.com/en/5.0/topics/templates/
