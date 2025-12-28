# 🏗️ Arquitetura Separada - Landing Page vs Sistema

## 🎯 Problema de Segurança Identificado

### Atualmente:
```
https://gestto.com/
├── /login/          ← Sistema principal exposto
├── /admin/          ← Admin exposto
├── /dashboard/      ← Protegido mas rotas expostas
└── /api/create-tenant/  ← Público mas sem interface
```

**Riscos:**
- ❌ Sistema principal acessível por qualquer pessoa
- ❌ Tentativas de bruteforce no /login/
- ❌ Exposição de rotas internas
- ❌ Sem separação clara público/privado

---

## ✅ Solução: 2 Domínios/Subdomínios

### Arquitetura Recomendada:

```
1. Landing Page (Público)
   https://gestto.com.br/          ← Site institucional
   ├── Home
   ├── Preços
   ├── Recursos
   ├── Sobre
   └── /cadastro/                  ← Formulário de registro

2. Sistema (Privado - Só clientes)
   https://app.gestto.com.br/      ← Sistema principal
   ├── /login/
   ├── /dashboard/
   ├── /agendamentos/
   └── /api/...

3. API Pública (Isolada)
   https://api.gestto.com.br/
   ├── /create-tenant/
   ├── /webhooks/stripe/
   └── /webhooks/asaas/
```

---

## 📁 Estrutura de Projetos

### Opção 1: Projetos Separados (RECOMENDADO)

```
gestto/
├── landing-page/              ← Site público (Next.js, WordPress, etc)
│   ├── pages/
│   │   ├── index.html        ← Home
│   │   ├── precos.html       ← Página de preços
│   │   └── cadastro.html     ← Formulário de registro
│   └── static/
│
└── sistema-gestto/            ← Sistema Django (atual)
    ├── manage.py
    ├── core/
    ├── agendamentos/
    └── ...
```

**Vantagens:**
- ✅ Completa separação de código
- ✅ Landing page pode ser estática (mais rápida)
- ✅ Sistema Django só para clientes autenticados
- ✅ Pode usar CDN para landing page
- ✅ Fácil atualizar landing sem mexer no sistema

### Opção 2: Mesmo Projeto, Apps Separados

```
gestto/
├── manage.py
├── landing/                   ← App público
│   ├── views.py
│   ├── templates/
│   │   ├── home.html
│   │   ├── precos.html
│   │   └── cadastro.html
│   └── urls.py
│
├── core/                      ← Sistema (privado)
├── agendamentos/
└── config/
    └── urls.py
```

**Vantagens:**
- ✅ Tudo em um único projeto
- ✅ Compartilha models e lógica
- ✅ Mais fácil de deployar

**Desvantagens:**
- ❌ Sistema ainda exposto (precisa configurar bem)
- ❌ Mais difícil de escalar separadamente

---

## 🎨 Implementação Prática

### OPÇÃO A: Landing Page Simples (HTML estático)

Vou criar agora mesmo uma landing page básica que você pode hospedar separado.

### OPÇÃO B: App Django "landing" no mesmo projeto

Adicionar um app público no projeto atual.

---

## 🔒 Configuração de Segurança

### 1. Nginx - Separar Público/Privado

```nginx
# Landing Page (público)
server {
    listen 80;
    server_name gestto.com.br www.gestto.com.br;

    location / {
        root /var/www/landing-page;
        try_files $uri $uri/ /index.html;
    }

    location /cadastro {
        proxy_pass http://api.gestto.com.br/create-tenant/;
    }
}

# API Pública (webhooks, create-tenant)
server {
    listen 80;
    server_name api.gestto.com.br;

    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api_limit:10m rate=10r/m;

    location /create-tenant/ {
        limit_req zone=api_limit burst=5;
        proxy_pass http://django:8000;
    }

    location /webhooks/ {
        proxy_pass http://django:8000;
    }

    # Bloquear acesso a TUDO mais
    location / {
        return 403;
    }
}

# Sistema (só clientes autenticados)
server {
    listen 80;
    server_name app.gestto.com.br;

    # IP whitelist (opcional)
    # allow 1.2.3.4;
    # deny all;

    location / {
        proxy_pass http://django:8000;
    }

    # Bloquear acesso direto ao admin de fora
    location /admin/ {
        allow 192.168.1.0/24;  # Sua rede interna
        deny all;
    }
}
```

### 2. Django settings.py

```python
# Permitir apenas subdomínio app
ALLOWED_HOSTS = ['app.gestto.com.br', 'api.gestto.com.br']

# CSRF trusted origins
CSRF_TRUSTED_ORIGINS = [
    'https://app.gestto.com.br',
    'https://api.gestto.com.br',
    'https://gestto.com.br',  # Para formulário de cadastro
]

# Session cookie domain
SESSION_COOKIE_DOMAIN = '.gestto.com.br'
```

---

## 🎯 Qual Opção Escolher?

### Para Começar (MVP):
**Opção B** - App landing no mesmo projeto Django
- Mais rápido de implementar
- Você já tem tudo configurado
- Depois pode separar

### Para Produção (Escalável):
**Opção A** - Landing page separada
- Melhor performance
- Melhor segurança
- Profissional

---

## 🚀 Implementação Imediata

Vou criar AGORA:

1. **App `landing` no Django** (público)
2. **Formulário de cadastro** estilizado
3. **Página de preços** com os 3 planos
4. **URLs separadas** (`/` = landing, `/app/` = sistema)
5. **Middleware** para bloquear acesso não autorizado

Isso vai funcionar até você criar uma landing separada depois.

---

**Posso criar isso agora?** Ou prefere que eu crie primeiro só o HTML estático da landing page?
