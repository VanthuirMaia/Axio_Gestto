# Configuração de Email com Brevo (Sendinblue)

## Por que usar Brevo?

- ✅ **300 emails grátis por dia** (9.000/mês)
- ✅ Configuração simples e rápida
- ✅ Alta taxa de entrega (deliverability)
- ✅ Dashboard com estatísticas de envio
- ✅ Suporte a templates HTML
- ✅ Rastreamento de aberturas e cliques (opcional)

---

## Passo 1: Criar Conta na Brevo

1. Acesse: https://www.brevo.com
2. Clique em **Sign up free**
3. Preencha seus dados e confirme o email
4. Complete o cadastro da sua empresa

---

## Passo 2: Obter Credenciais SMTP

1. Faça login na Brevo
2. Vá em **Settings** (Configurações) → **SMTP & API**
3. Na aba **SMTP**, você verá:
   - **Server:** `smtp-relay.brevo.com` (ou `smtp-relay.sendinblue.com`)
   - **Port:** `587`
   - **Login:** Seu email cadastrado na Brevo
   - **SMTP Key:** Clique em **Generate a new SMTP key**

4. **Copie a SMTP Key gerada** (ela aparece apenas uma vez!)

---

## Passo 3: Configurar Remetente Autorizado

**IMPORTANTE:** A Brevo exige que você configure os remetentes permitidos.

1. Na Brevo, vá em **Settings** → **Senders & IP**
2. Clique em **Add a sender**
3. Adicione o email que você usará como remetente:
   - Exemplo: `noreply@axiogesto.com` ou `contato@seudominio.com`
4. **Confirme o email** (a Brevo enviará um link de verificação)

---

## Passo 4: Configurar no Django (.env)

Edite seu arquivo `.env` (ou `.env.production`) e adicione:

```env
# ============================================
# EMAIL SETTINGS - Brevo/Sendinblue
# ============================================
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp-relay.brevo.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=seu-email@exemplo.com
EMAIL_HOST_PASSWORD=sua-smtp-key-aqui
DEFAULT_FROM_EMAIL=noreply@axiogesto.com
```

### Valores a substituir:

- `EMAIL_HOST_USER`: O email que você usou para criar a conta na Brevo
- `EMAIL_HOST_PASSWORD`: A **SMTP Key** que você gerou no Passo 2
- `DEFAULT_FROM_EMAIL`: O email remetente que você configurou no Passo 3

---

## Passo 5: Testar o Envio

Execute o script de teste:

```bash
python testar_emails.py
```

Você deve ver os emails sendo enviados com sucesso!

---

## Exemplo de Configuração Completa

```env
# .env ou .env.production

EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp-relay.brevo.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=contato@axiogesto.com
EMAIL_HOST_PASSWORD=xkeysib-a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6-AbCdEfGhIjKlMnOp
DEFAULT_FROM_EMAIL=noreply@axiogesto.com
```

---

## Troubleshooting (Problemas Comuns)

### 1. Erro: "Authentication failed"
- ❌ **Causa:** SMTP Key inválida ou EMAIL_HOST_USER incorreto
- ✅ **Solução:** Gere uma nova SMTP Key na Brevo e copie corretamente

### 2. Erro: "Sender not authorized"
- ❌ **Causa:** O email `DEFAULT_FROM_EMAIL` não foi configurado como remetente na Brevo
- ✅ **Solução:** Vá em Settings → Senders & IP e adicione o remetente

### 3. Emails não chegam
- Verifique a pasta de **Spam/Lixo eletrônico**
- Confira o dashboard da Brevo para ver os logs de envio
- Verifique se o domínio do remetente está verificado

### 4. Limite de 300 emails/dia excedido
- ❌ **Causa:** Ultrapassou o limite do plano gratuito
- ✅ **Solução:** Aguarde 24h ou faça upgrade para um plano pago

---

## Configuração Avançada (Opcional)

### Verificar Domínio Próprio (Recomendado)

Para melhorar a taxa de entrega, configure SPF e DKIM:

1. Na Brevo, vá em **Settings** → **Senders & IP**
2. Clique em **Authenticate your domain**
3. Siga as instruções para adicionar registros DNS

Exemplo de registros DNS:
```
TXT @ "v=spf1 include:spf.brevo.com ~all"
TXT brevo._domainkey "v=DKIM1; k=rsa; p=..."
```

---

## Monitoramento de Emails

Acesse o dashboard da Brevo para:
- Ver quantos emails foram enviados
- Taxa de abertura
- Taxa de cliques
- Bounces (emails rejeitados)
- Spam complaints

---

## Alternativas ao Brevo

Se precisar de mais emails ou outras funcionalidades:

| Provedor | Emails Grátis | Plano Pago |
|----------|---------------|------------|
| **Brevo** | 300/dia | A partir de €25/mês |
| **SendGrid** | 100/dia | A partir de $19.95/mês |
| **Mailgun** | 100/dia | A partir de $35/mês |
| **Amazon SES** | 62.000/mês* | $0.10/1000 emails |

\* *Apenas se estiver usando EC2*

---

## Suporte

- **Documentação Brevo:** https://developers.brevo.com/docs
- **Suporte Brevo:** https://help.brevo.com/
- **Status Brevo:** https://status.brevo.com/
