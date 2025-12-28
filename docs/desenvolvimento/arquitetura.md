# 🏗️ Arquitetura Separada - Implementada

## ✅ Separação Completa

### Estrutura de URLs:

```
┌─────────────────────────────────────────┐
│  PÚBLICO (sem autenticação)             │
├─────────────────────────────────────────┤
│  /                  → Landing home      │
│  /precos/           → Preços            │
│  /cadastro/         → Formulário        │
│  /sobre/            → Sobre             │
│  /contato/          → Contato           │
│                                         │
│  /api/create-tenant/    → Criar cliente │
│  /api/webhooks/stripe/  → Webhooks      │
│  /api/webhooks/asaas/   → Webhooks      │
│  /api/whatsapp-webhook/ → WhatsApp      │
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│  PRIVADO (só autenticados)              │
├─────────────────────────────────────────┤
│  /app/login/           → Login          │
│  /app/dashboard/       → Dashboard      │
│  /app/agendamentos/    → Agendamentos   │
│  /app/clientes/        → Clientes       │
│  /app/financeiro/      → Financeiro     │
│  /app/configuracoes/   → Config         │
│  /app/admin/           → Admin Django   │
└─────────────────────────────────────────┘
```

---

## 🔒 Segurança Implementada

### 1. Separação Física de URLs
- ✅ Landing em `/` (público)
- ✅ Sistema em `/app/` (privado)
- ✅ APIs em `/api/` (públicas mas protegidas)

### 2. Benefícios
- ✅ Sistema não aparece para visitantes
- ✅ URLs internas não expostas
- ✅ Admin protegido em `/app/admin/`
- ✅ Fácil aplicar rate limiting por rota
- ✅ Fácil migrar landing para domínio separado

---

## 📁 Arquivos Criados

```
landing/
├── __init__.py
├── apps.py
├── views.py             ← Home, preços, cadastro, sobre, contato
├── urls.py              ← Rotas públicas
└── templates/
    └── landing/
        ├── base.html
        ├── home.html
        ├── precos.html
        ├── cadastro.html
        ├── sobre.html
        └── contato.html
```

---

## 🚀 Como Testar

### 1. Acessar Landing (público)
```
http://localhost:8000/           → Home
http://localhost:8000/precos/    → Preços
http://localhost:8000/cadastro/  → Cadastro
```

### 2. Acessar Sistema (privado)
```
http://localhost:8000/app/login/     → Login
http://localhost:8000/app/dashboard/ → Dashboard (precisa login)
```

### 3. Testar Cadastro
1. Acesse `/cadastro/`
2. Preencha formulário
3. Clique "Continuar para Pagamento"
4. Será redirecionado para Stripe/Asaas checkout
5. Após pagar, recebe credenciais por email
6. Faz login em `/app/login/`

---

## 🌐 Deploy com Domínios Separados

### Opção 1: Subdomínios

**Nginx config:**
```nginx
# Landing (público)
server {
    listen 80;
    server_name gestto.com.br www.gestto.com.br;

    location / {
        proxy_pass http://django:8000;  # Vai para landing/
    }

    location /app/ {
        return 301 https://app.gestto.com.br$request_uri;
    }
}

# Sistema (privado)
server {
    listen 80;
    server_name app.gestto.com.br;

    location / {
        proxy_pass http://django:8000/app/;
    }
}

# API (públic)
server {
    listen 80;
    server_name api.gestto.com.br;

    limit_req_zone $binary_remote_addr zone=api_limit:10m rate=10r/m;

    location / {
        limit_req zone=api_limit burst=5;
        proxy_pass http://django:8000/api/;
    }
}
```

**Django settings.py:**
```python
ALLOWED_HOSTS = [
    'gestto.com.br',
    'www.gestto.com.br',
    'app.gestto.com.br',
    'api.gestto.com.br',
]

CSRF_TRUSTED_ORIGINS = [
    'https://gestto.com.br',
    'https://app.gestto.com.br',
    'https://api.gestto.com.br',
]
```

### Opção 2: Mesmo Domínio (atual)

```
gestto.com.br/             → Landing
gestto.com.br/app/         → Sistema
gestto.com.br/api/         → APIs
```

**Vantagens:**
- ✅ Mais simples de configurar
- ✅ 1 só SSL
- ✅ Funciona como está agora

**Desvantagens:**
- ⚠️ URLs mais longas (/app/dashboard/)
- ⚠️ Landing e sistema no mesmo servidor

---

## 🔧 Migração Futura (se quiser)

### Para separar landing completamente:

1. **Criar site estático (HTML/Next.js/WordPress)**
2. **Hospedar em:**
   - Vercel (gratuito)
   - Netlify (gratuito)
   - GitHub Pages
3. **Apontar domínio principal:**
   - `gestto.com.br` → Vercel/Netlify
4. **Manter Django apenas para sistema:**
   - `app.gestto.com.br` → Seu VPS

**Formulário de cadastro na landing estática:**
```html
<form action="https://api.gestto.com.br/create-tenant/" method="POST">
  <!-- campos -->
</form>
```

---

## ✅ Checklist de Segurança

- [x] Landing separada do sistema
- [x] URLs /app/* protegidas por login
- [x] Admin em /app/admin/ (não na raiz)
- [x] APIs públicas isoladas em /api/*
- [ ] Rate limiting (configurar no nginx)
- [ ] Firewall no servidor (só portas 80, 443, 22)
- [ ] SSL configurado (Let's Encrypt)
- [ ] Backup automático do banco
- [ ] Monitoramento (Sentry, etc)

---

## 📊 Fluxo Completo

```
1. Cliente acessa gestto.com.br/
   ↓
2. Navega pela landing (preços, recursos)
   ↓
3. Clica em "Cadastrar" → /cadastro/
   ↓
4. Preenche formulário e escolhe plano
   ↓
5. Sistema chama /api/create-tenant/
   ↓
6. Django cria empresa + assinatura + admin
   ↓
7. Redireciona para Stripe/Asaas checkout
   ↓
8. Cliente paga
   ↓
9. Webhook /api/webhooks/stripe/ ativa assinatura
   ↓
10. Email enviado com credenciais
   ↓
11. Cliente acessa app.gestto.com.br/login/
   ↓
12. Faz login → Onboarding
   ↓
13. Configura serviços, profissionais, WhatsApp
   ↓
14. Pronto! Sistema funcionando
```

---

**Data:** 25/12/2025
**Status:** ✅ Implementado e testável
**Próximo passo:** Testar fluxo completo
