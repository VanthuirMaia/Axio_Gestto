# ⚡ Início Rápido - Stripe em 10 Minutos

## ✅ Checklist Ultra-Rápido

### PASSO 1: Rodar migration (adicionar campo stripe_price_id)
```bash
python manage.py makemigrations
python manage.py migrate
```

### PASSO 2: Pegar chaves do Stripe

1. Acesse: https://dashboard.stripe.com/test/apikeys
2. Copie:
   - **Publishable key** (começa com `pk_test_`)
   - **Secret key** (começa com `sk_test_`)

### PASSO 3: Adicionar no .env

Edite o arquivo `.env`:

```env
STRIPE_PUBLIC_KEY=pk_test_COLE_AQUI
STRIPE_SECRET_KEY=sk_test_COLE_AQUI
STRIPE_WEBHOOK_SECRET=
SITE_URL=http://localhost:8000
```

Salve e reinicie o servidor:
```bash
python manage.py runserver
```

### PASSO 4: Criar produtos no Stripe

1. https://dashboard.stripe.com/test/products
2. **Add product**

**Produto 1:**
- Name: `Plano Essencial`
- Price: `R$ 49.00` (ou `USD 10`)
- Billing: `Monthly`
- Copie o `price_id` (ex: `price_1Abc...`)

**Produto 2:**
- Name: `Plano Profissional`
- Price: `R$ 149.00` (ou `USD 30`)
- Billing: `Monthly`
- Copie o `price_id`

**Produto 3:**
- Name: `Plano Empresarial`
- Price: `R$ 299.00` (ou `USD 60`)
- Billing: `Monthly`
- Copie o `price_id`

### PASSO 5: Configurar price_ids no Admin

1. http://localhost:8000/admin/
2. **Assinaturas → Planos**
3. Editar "Essencial":
   - Campo `stripe_price_id`: Colar o price_id do Plano Essencial
   - Salvar
4. Repetir para "Profissional" e "Empresarial"

### PASSO 6: Configurar webhook (para testes locais)

**Baixar Stripe CLI:**
- https://github.com/stripe/stripe-cli/releases/latest
- Extrair para `C:\stripe\`

**Rodar:**
```bash
C:\stripe\stripe.exe login
C:\stripe\stripe.exe listen --forward-to localhost:8000/api/webhooks/stripe/
```

**Copiar o `whsec_...` que aparece.**

**Adicionar no .env:**
```env
STRIPE_WEBHOOK_SECRET=whsec_COLE_AQUI
```

**Reiniciar servidor Django.**

### PASSO 7: TESTAR!

**Via Postman ou curl:**

```bash
curl -X POST http://localhost:8000/api/create-tenant/ ^
  -H "Content-Type: application/json" ^
  -d "{\"nome_empresa\":\"Teste\",\"email_admin\":\"teste@exemplo.com\",\"telefone\":\"11999999999\",\"plano\":\"profissional\",\"gateway\":\"stripe\"}"
```

**Abrir o `checkout_url` que retornar.**

**Pagar com cartão de teste:**
- Número: `4242 4242 4242 4242`
- Validade: `12/25`
- CVC: `123`

**Verificar no Admin:**
- Ir em **Assinaturas → Assinaturas**
- Ver se apareceu com status "ativa"

---

## 🆘 Se der erro

### "No such price: price_..."
→ Price ID errado no Admin

### "Invalid API Key"
→ Secret key errada no .env

### "Webhook signature failed"
→ Webhook secret errado no .env

### "Assinatura não ativou"
→ Stripe CLI não está rodando
→ Ou webhook secret errado

---

## ✅ Pronto!

**Arquivos que você mexeu:**
1. `.env` (chaves)
2. Admin (price_ids)

**Código Python:** ZERO mudanças!

**Próximo passo:** Ler `STRIPE_SETUP_PASSO_A_PASSO.md` para detalhes completos.

---

**Tempo estimado:** 10-15 minutos ⏱️
