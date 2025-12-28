# 💳 Integração Stripe - Passo a Passo COMPLETO

## ✅ Checklist Rápido

- [ ] Conta Stripe criada
- [ ] Modo Test ativado
- [ ] Chaves API copiadas
- [ ] Variáveis no .env configuradas
- [ ] Webhook configurado no Stripe Dashboard
- [ ] Teste de pagamento realizado

---

## PASSO 1: Pegar as chaves no Stripe Dashboard

### 1.1 Acessar o Dashboard
- URL: https://dashboard.stripe.com/
- Login com sua conta

### 1.2 Ativar Modo Test
- No canto superior direito, verifica se está escrito **"Test mode"**
- Se não estiver, clique no toggle para ativar
- **IMPORTANTE:** Sempre use Test mode enquanto desenvolve!

### 1.3 Pegar as Chaves da API
- Ir em: **Developers → API Keys**
- Você verá 2 chaves:

**Publishable key (começa com `pk_test_`):**
```
pk_test_51QZd8sP8qY...  (exemplo)
```

**Secret key (começa com `sk_test_`):** (clique em "Reveal test key")
```
sk_test_51QZd8sP8qY...  (exemplo)
```

### 1.4 Copiar as chaves
- ⚠️ **NÃO compartilhe a Secret Key com ninguém!**
- Vamos usar ela no próximo passo

---

## PASSO 2: Configurar as variáveis de ambiente

### 2.1 Abrir o arquivo .env

**Caminho:** `D:\Axio\axio_gestto\.env`

Se não existir, crie copiando do `.env.example`:
```bash
copy .env.example .env
```

### 2.2 Adicionar/Editar estas linhas no .env

```env
# ==========================================
# STRIPE (PAGAMENTOS INTERNACIONAIS)
# ==========================================
STRIPE_PUBLIC_KEY=pk_test_COLE_SUA_CHAVE_AQUI
STRIPE_SECRET_KEY=sk_test_COLE_SUA_CHAVE_AQUI
STRIPE_WEBHOOK_SECRET=whsec_VAMOS_PEGAR_ISSO_DEPOIS

# URL do site (importante para o Stripe)
SITE_URL=http://localhost:8000
```

**Substitua:**
- `pk_test_COLE_SUA_CHAVE_AQUI` → Sua Publishable key
- `sk_test_COLE_SUA_CHAVE_AQUI` → Sua Secret key

**Exemplo real:**
```env
STRIPE_PUBLIC_KEY=pk_test_51QZd8sP8qYJKLMNOPQRSTUVWXYZ
STRIPE_SECRET_KEY=sk_test_51QZd8sP8qYabcdefghijklmnopqrstuvwxyz
STRIPE_WEBHOOK_SECRET=
SITE_URL=http://localhost:8000
```

### 2.3 Salvar o arquivo

**IMPORTANTE:** Após salvar, reinicie o servidor Django:
```bash
# Parar o servidor (Ctrl+C se estiver rodando)
# Iniciar novamente
python manage.py runserver
```

---

## PASSO 3: Instalar biblioteca Stripe

### 3.1 Verificar se já está instalada

```bash
pip list | findstr stripe
```

Se aparecer `stripe` na lista, já está instalado. Pule para o Passo 4.

### 3.2 Se não estiver instalado:

```bash
pip install stripe
```

### 3.3 Adicionar ao requirements.txt

**Arquivo:** `requirements.txt`

Adicione esta linha:
```
stripe==10.12.0
```

---

## PASSO 4: Criar produtos e preços no Stripe

### 4.1 Criar Produto "Plano Essencial"

1. No Stripe Dashboard: **Products → Add product**
2. Preencher:
   - **Name:** Plano Essencial
   - **Description:** 500 agendamentos/mês, 1 profissional
   - **Pricing model:** Standard pricing
   - **Price:** R$ 49.00 (ou USD 10.00 se quiser testar em dólar)
   - **Billing period:** Monthly
   - **Currency:** BRL (ou USD)
3. Clicar em **Add product**

4. **COPIAR O PRICE ID:**
   - Depois de criar, você verá algo como: `price_1Abc...`
   - Copie esse ID!

### 4.2 Criar Produto "Plano Profissional"

Repetir processo:
- **Name:** Plano Profissional
- **Price:** R$ 149.00
- **Billing period:** Monthly
- Copiar o `price_id`

### 4.3 Criar Produto "Plano Empresarial"

- **Name:** Plano Empresarial
- **Price:** R$ 299.00
- **Billing period:** Monthly
- Copiar o `price_id`

### 4.4 Atualizar os Price IDs no banco de dados

**OPÇÃO A - Via Admin Django (recomendado):**

1. Acessar: `http://localhost:8000/admin/`
2. Login com superuser
3. Ir em: **Assinaturas → Planos**
4. Editar "Essencial":
   - Campo `stripe_price_id`: Colar o price_id do produto Essencial
   - Salvar
5. Repetir para "Profissional" e "Empresarial"

**OPÇÃO B - Via Django Shell:**

```python
python manage.py shell

from assinaturas.models import Plano

# Essencial
essencial = Plano.objects.get(nome='essencial')
essencial.stripe_price_id = 'price_ABC123'  # ← SEU PRICE ID
essencial.save()

# Profissional
profissional = Plano.objects.get(nome='profissional')
profissional.stripe_price_id = 'price_DEF456'  # ← SEU PRICE ID
profissional.save()

# Empresarial
empresarial = Plano.objects.get(nome='empresarial')
empresarial.stripe_price_id = 'price_GHI789'  # ← SEU PRICE ID
empresarial.save()

exit()
```

---

## PASSO 5: Configurar Webhook no Stripe

### 5.1 Por que precisa de webhook?

O webhook avisa seu sistema quando:
- Cliente completou o pagamento ✅
- Pagamento mensal foi processado 💰
- Cliente cancelou assinatura ❌

### 5.2 Instalar Stripe CLI (para testar localmente)

**Download:** https://github.com/stripe/stripe-cli/releases/latest

1. Baixar `stripe_1.x.x_windows_x86_64.zip`
2. Extrair para `C:\stripe\`
3. Adicionar ao PATH do Windows (ou usar caminho completo)

### 5.3 Login no Stripe CLI

```bash
C:\stripe\stripe.exe login
```

- Abrirá o navegador
- Clicar em "Allow access"

### 5.4 Iniciar o webhook local

**IMPORTANTE:** Deixe este terminal aberto enquanto testa!

```bash
C:\stripe\stripe.exe listen --forward-to localhost:8000/api/webhooks/stripe/
```

Você verá algo como:
```
> Ready! Your webhook signing secret is whsec_abc123xyz... (^C to quit)
```

### 5.5 Copiar o Webhook Secret

Copie o código que começa com `whsec_`

Exemplo:
```
whsec_1a2b3c4d5e6f7g8h9i0j
```

### 5.6 Adicionar no .env

**Arquivo:** `.env`

```env
STRIPE_WEBHOOK_SECRET=whsec_COLE_AQUI_O_CODIGO
```

**Exemplo:**
```env
STRIPE_WEBHOOK_SECRET=whsec_1a2b3c4d5e6f7g8h9i0j
```

### 5.7 Reiniciar Django

```bash
# Ctrl+C no servidor Django
python manage.py runserver
```

---

## PASSO 6: TESTAR! 🎉

### 6.1 Criar um tenant de teste

**Via API (Postman ou curl):**

```bash
curl -X POST http://localhost:8000/api/create-tenant/ \
  -H "Content-Type: application/json" \
  -d "{
    \"nome_empresa\": \"Barbearia Teste\",
    \"email_admin\": \"teste@exemplo.com\",
    \"telefone\": \"(11) 99999-9999\",
    \"plano\": \"profissional\",
    \"gateway\": \"stripe\"
  }"
```

**Resposta esperada:**
```json
{
  "sucesso": true,
  "mensagem": "Tenant criado com sucesso! Realize o pagamento.",
  "checkout_url": "https://checkout.stripe.com/c/pay/cs_test_abc123...",
  "credentials": {
    "username": "admin_barbearia-teste",
    "temp_password": "xyz789"
  }
}
```

### 6.2 Abrir o link de pagamento

Copie o `checkout_url` e abra no navegador.

### 6.3 Pagar com cartão de teste

Na página do Stripe Checkout, use estes dados:

**Cartão de teste (APROVADO):**
- **Número:** `4242 4242 4242 4242`
- **Validade:** Qualquer data futura (ex: `12/25`)
- **CVC:** Qualquer 3 dígitos (ex: `123`)
- **Nome:** Qualquer nome
- **Email:** Qualquer email

**Clicar em "Subscribe"**

### 6.4 Verificar no terminal do Stripe CLI

No terminal onde você rodou `stripe listen`, você verá:

```
checkout.session.completed [evt_abc123]
customer.subscription.created [evt_def456]
```

### 6.5 Verificar no Django Admin

1. Acessar: `http://localhost:8000/admin/`
2. Ir em: **Assinaturas → Assinaturas**
3. Verificar se apareceu uma nova assinatura:
   - Empresa: Barbearia Teste
   - Status: **ativa** ✅
   - Plano: Profissional

### 6.6 Fazer login com o novo cliente

1. Acessar: `http://localhost:8000/login/`
2. Login: `admin_barbearia-teste`
3. Senha: (a senha temporária que veio na resposta)
4. Deve redirecionar para o onboarding!

---

## PASSO 7: Configurar webhook em PRODUÇÃO (depois do deploy)

### 7.1 Quando subir para produção

No Stripe Dashboard:
1. Ir em: **Developers → Webhooks**
2. Clicar em **Add endpoint**
3. **Endpoint URL:** `https://seu-dominio.com/api/webhooks/stripe/`
4. **Events to send:**
   - `checkout.session.completed`
   - `invoice.payment_succeeded`
   - `invoice.payment_failed`
   - `customer.subscription.deleted`
5. Clicar em **Add endpoint**

### 7.2 Copiar o Webhook Signing Secret

Depois de criar o endpoint:
1. Clicar no endpoint criado
2. Seção **Signing secret**
3. Clicar em **Reveal**
4. Copiar o código `whsec_...`

### 7.3 Atualizar .env de produção

No servidor de produção, editar `.env`:
```env
STRIPE_WEBHOOK_SECRET=whsec_NOVO_CODIGO_DE_PRODUCAO
SITE_URL=https://seu-dominio.com
```

Reiniciar servidor.

---

## 🔥 Arquivos que você MEXEU (resumo)

### 1. `.env` (ÚNICO arquivo que você editou!)
```env
STRIPE_PUBLIC_KEY=pk_test_...
STRIPE_SECRET_KEY=sk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...
SITE_URL=http://localhost:8000
```

### 2. Admin Django
- Atualizou `stripe_price_id` nos 3 planos

**Pronto! Integração completa. NÃO precisou mexer em código Python!**

---

## 🆘 Como corrigir se quebrar

### Erro: "No such price: price_..."

**Causa:** O `stripe_price_id` no banco está errado

**Solução:**
1. Acesse Admin Django
2. Vá em Assinaturas → Planos
3. Edite o plano com erro
4. Copie o price_id correto do Stripe Dashboard
5. Cole no campo `stripe_price_id`
6. Salve

---

### Erro: "Invalid API Key provided"

**Causa:** A secret key no `.env` está errada

**Solução:**
1. Vá no Stripe Dashboard → Developers → API Keys
2. Copie novamente a **Secret key**
3. Edite `.env`
4. Cole a chave correta em `STRIPE_SECRET_KEY`
5. Reinicie o servidor Django

---

### Erro: "Webhook signature verification failed"

**Causa:** O `STRIPE_WEBHOOK_SECRET` está errado ou faltando

**Solução LOCAL:**
1. Parar o `stripe listen`
2. Rodar novamente: `stripe listen --forward-to localhost:8000/api/webhooks/stripe/`
3. Copiar o novo `whsec_...`
4. Atualizar no `.env`
5. Reiniciar Django

**Solução PRODUÇÃO:**
1. Ir em Stripe Dashboard → Webhooks
2. Clicar no endpoint
3. Revelar o Signing secret
4. Copiar
5. Atualizar `.env` no servidor
6. Reiniciar servidor

---

### Erro: "Assinatura não ativou após pagamento"

**Causa:** Webhook não chegou ou falhou

**Verificar logs:**
```python
# Django shell
from assinaturas.models import HistoricoPagamento
logs = HistoricoPagamento.objects.order_by('-criado_em')[:10]
for log in logs:
    print(f"{log.gateway} - {log.status} - {log.dados_evento}")
```

**Ativar manualmente:**
```python
from assinaturas.models import Assinatura
from django.utils.timezone import now
from datetime import timedelta

assinatura = Assinatura.objects.get(empresa__slug='cliente')
assinatura.status = 'ativa'
assinatura.data_expiracao = now() + timedelta(days=30)
assinatura.save()
```

---

## ✅ Checklist de Sucesso

Após seguir todos os passos:

- [ ] Consegui criar um checkout do Stripe
- [ ] Consegui pagar com cartão de teste
- [ ] Webhook chegou (vi no terminal do stripe listen)
- [ ] Assinatura apareceu como "ativa" no Admin
- [ ] Consegui fazer login com as credenciais geradas
- [ ] Onboarding apareceu após login

**Se todos os ✅ estão marcados: PARABÉNS! Integração funcionando! 🎉**

---

## 📞 Próximos Passos

1. **Testar com todos os 3 planos** (Essencial, Profissional, Empresarial)
2. **Testar cartão que falha:** `4000 0000 0000 0002`
3. **Testar cancelamento de assinatura**
4. **Quando for para produção:**
   - Mudar para modo Live no Stripe
   - Pegar chaves Live (pk_live_ e sk_live_)
   - Configurar webhook de produção
   - Atualizar .env

---

**Dúvidas?** Todos os arquivos estão em `assinaturas/stripe_integration.py` (mas você NÃO precisa mexer lá!)
