# 🔧 Guia de Instalação do Stripe CLI - Windows

## ✅ Passo 1: Instalar Stripe CLI

### Opção A - Via Scoop (Recomendado)
```bash
# Se não tiver o Scoop instalado:
Set-ExecutionPolicy RemoteSigned -Scope CurrentUser
irm get.scoop.sh | iex

# Instalar Stripe CLI:
scoop bucket add stripe https://github.com/stripe/scoop-stripe-cli.git
scoop install stripe
```

### Opção B - Download Direto
1. Baixar: https://github.com/stripe/stripe-cli/releases/latest
2. Procurar por `stripe_X.X.X_windows_x86_64.zip`
3. Descompactar e adicionar ao PATH

### Verificar Instalação
```bash
stripe --version
```

---

## 🔑 Passo 2: Fazer Login no Stripe

```bash
stripe login
```

Vai abrir o navegador pedindo autorização. Clique em **"Allow access"**.

Você verá:
```
✔ Done! The Stripe CLI is configured with account ID acct_xxxxx
```

---

## 🎧 Passo 3: Escutar Webhooks Localmente

### Terminal 1 - Servidor Django (deixe rodando)
```bash
# No terminal do VSCode
python manage.py runserver
```

### Terminal 2 - Stripe CLI (deixe rodando)
```bash
# Em OUTRO terminal
stripe listen --forward-to http://localhost:8000/api/webhooks/stripe/
```

Você verá algo assim:
```
> Ready! You are using Stripe API Version [2024-XX-XX].
> Your webhook signing secret is whsec_1234567890abcdefghijklmnopqrstuvwxyz
```

**🔴 IMPORTANTE: Copie o `whsec_...` e atualize no .env:**
```env
STRIPE_WEBHOOK_SECRET=whsec_1234567890abcdefghijklmnopqrstuvwxyz
```

Depois reinicie o servidor Django (Ctrl+C e `python manage.py runserver` novamente).

---

## 🧪 Passo 4: Atualizar Planos no Banco

```bash
# No terminal do Django
python atualizar_planos_stripe.py
```

Deve mostrar:
```
✅ Plano 'Essencial' atualizado:
   - Preço: R$ 49.00
   - Price ID: price_1XXXXXXXXXXXXXXXXXXXXX

✅ Plano 'Profissional' atualizado:
   - Preço: R$ 179.00
   - Price ID: price_1YYYYYYYYYYYYYYYYYYYYYY

✅ Plano 'Empresarial' atualizado:
   - Preço: R$ 399.00
   - Price ID: price_1ZZZZZZZZZZZZZZZZZZZZZ
```

---

## 🎯 Passo 5: Testar Webhook

### Terminal 3 - Enviar Evento de Teste
```bash
stripe trigger checkout.session.completed
```

No **Terminal 2** (stripe listen), você verá:
```
✔️ webhook_id: evt_xxxxx checkout.session.completed [200]
```

No **Terminal 1** (Django), você verá logs do processamento.

---

## 📋 Checklist Final

- [ ] Stripe CLI instalado (`stripe --version` funciona)
- [ ] Login feito (`stripe login` concluído)
- [ ] Webhook secret copiado para `.env`
- [ ] Planos atualizados (`python atualizar_planos_stripe.py`)
- [ ] Servidor Django rodando (Terminal 1)
- [ ] Stripe CLI escutando (Terminal 2)
- [ ] Teste de webhook OK (`stripe trigger checkout.session.completed`)

---

## 🐛 Troubleshooting

### Erro: "stripe: command not found"
- Reinicie o terminal após instalar
- Verifique se adicionou ao PATH

### Erro: "Invalid API Key"
- Rode `stripe login` novamente
- Verifique se está logado na conta correta

### Webhook retorna 404
- Verifique se URL está correta: `http://localhost:8000/api/webhooks/stripe/`
- Verifique se servidor Django está rodando na porta 8000

### Webhook retorna 400/500
- Verifique logs do Django
- Confira se `STRIPE_WEBHOOK_SECRET` está no `.env`
- Reinicie o servidor Django após mudar `.env`

---

## 🎓 Comandos Úteis

```bash
# Listar produtos
stripe products list

# Listar preços
stripe prices list

# Testar eventos específicos
stripe trigger checkout.session.completed
stripe trigger invoice.payment_succeeded
stripe trigger invoice.payment_failed

# Ver logs de webhooks
stripe logs tail
```

---

## ⚡ Próximos Passos

Depois de tudo configurado:
1. Testar cadastro de nova empresa
2. Verificar redirecionamento ao Stripe
3. Pagar com cartão de teste
4. Verificar assinatura ativada

**Cartões de teste do Stripe:**
- Sucesso: `4242 4242 4242 4242`
- Recusado: `4000 0000 0000 0002`
- CVV: qualquer 3 dígitos
- Data: qualquer data futura
