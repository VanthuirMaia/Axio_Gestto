# 🖥️ Setup n8n VPS - Sem Sistema de Credenciais

## ⚠️ Problema Resolvido

Você usa n8n self-hosted em VPS e **não quer/pode usar o sistema de credenciais**. Este guia mostra como configurar usando **variáveis de ambiente** ou **valores diretos**.

---

## 🎯 Solução: Variáveis de Ambiente

### **Opção A: Usar Variáveis de Ambiente (RECOMENDADO)**

#### **Passo 1: Configurar no Docker** (se usar Docker)

**1.1. Edite docker-compose.yml:**

```yaml
version: '3.8'

services:
  n8n:
    image: n8nio/n8n:latest
    restart: unless-stopped
    ports:
      - "5678:5678"
    environment:
      # n8n padrão
      - N8N_BASIC_AUTH_ACTIVE=true
      - N8N_BASIC_AUTH_USER=admin
      - N8N_BASIC_AUTH_PASSWORD=sua-senha

      # 🔑 SUAS VARIÁVEIS CUSTOMIZADAS
      - DJANGO_API_URL=https://axiogestto.com
      - DJANGO_API_KEY=sua-api-key-do-django-settings
      - EVOLUTION_API_URL=https://evolution.axiodev.cloud
      - EVOLUTION_API_KEY=sua-evolution-api-key-global
      - OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxxxx

    volumes:
      - n8n_data:/home/node/.n8n

volumes:
  n8n_data:
```

**1.2. Reinicie o n8n:**

```bash
docker-compose down
docker-compose up -d
```

#### **Passo 2: Usar no Workflow**

No n8n, acesse variáveis de ambiente com:

```javascript
{{ $env.DJANGO_API_URL }}
{{ $env.DJANGO_API_KEY }}
{{ $env.EVOLUTION_API_URL }}
{{ $env.EVOLUTION_API_KEY }}
{{ $env.OPENAI_API_KEY }}
```

**Exemplo em HTTP Request node:**

```json
{
  "url": "={{ $env.DJANGO_API_URL }}/api/n8n/profissionais/",
  "headers": {
    "apikey": "={{ $env.DJANGO_API_KEY }}",
    "empresa_id": "={{ $json.empresa_id }}"
  }
}
```

---

### **Opção B: Instalar sem Docker (systemd/pm2)**

Se você roda n8n direto na VPS:

#### **2.1. Criar arquivo .env:**

```bash
cd ~
nano .env.n8n
```

**Conteúdo:**
```bash
# n8n Settings
N8N_BASIC_AUTH_ACTIVE=true
N8N_BASIC_AUTH_USER=admin
N8N_BASIC_AUTH_PASSWORD=sua-senha
N8N_PORT=5678

# Django API
DJANGO_API_URL=https://axiogestto.com
DJANGO_API_KEY=sua-api-key-secreta

# Evolution API
EVOLUTION_API_URL=https://evolution.axiodev.cloud
EVOLUTION_API_KEY=sua-evolution-key

# OpenAI
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxx
```

#### **2.2. Carregar variáveis ao iniciar n8n:**

**Com systemd:**

```bash
sudo nano /etc/systemd/system/n8n.service
```

```ini
[Unit]
Description=n8n
After=network.target

[Service]
Type=simple
User=seu-usuario
EnvironmentFile=/home/seu-usuario/.env.n8n
ExecStart=/usr/bin/n8n start
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl restart n8n
```

**Com PM2:**

```bash
pm2 start n8n --name "n8n" -- start
pm2 save
```

Ou crie um arquivo `ecosystem.config.js`:

```javascript
module.exports = {
  apps: [{
    name: 'n8n',
    script: 'n8n',
    args: 'start',
    env: {
      DJANGO_API_URL: 'https://axiogestto.com',
      DJANGO_API_KEY: 'sua-api-key',
      EVOLUTION_API_URL: 'https://evolution.axiodev.cloud',
      EVOLUTION_API_KEY: 'sua-evolution-key',
      OPENAI_API_KEY: 'sk-proj-xxxxx'
    }
  }]
};
```

```bash
pm2 start ecosystem.config.js
pm2 save
```

---

### **Opção C: Hardcode (Menos Seguro, Mais Rápido)**

Se você quer algo rápido e não se importa com segurança:

#### **Substituir diretamente nos nodes:**

**Antes (com variável):**
```
url: "={{ $env.DJANGO_API_URL }}/api/n8n/profissionais/"
```

**Depois (hardcoded):**
```
url: "https://axiogestto.com/api/n8n/profissionais/"
```

**⚠️ ATENÇÃO:**
- ❌ Menos seguro (chaves ficam visíveis no workflow)
- ❌ Difícil manutenção (mudar URL = editar vários nodes)
- ✅ Mais rápido para testar
- ✅ Funciona imediatamente

---

## 📦 Importar Template VPS

**Arquivo:** `n8n-workflows/TEMPLATE_Bot_Universal_VPS.json`

### **Diferenças do template VPS:**

```json
// ❌ Template antigo (com credenciais)
{
  "authentication": "predefinedCredentialType",
  "nodeCredentialType": "httpHeaderAuth",
  "credentials": {
    "httpHeaderAuth": {
      "id": "django-api"
    }
  }
}

// ✅ Template VPS (sem credenciais)
{
  "authentication": "none",
  "sendHeaders": true,
  "headerParameters": {
    "parameters": [
      {
        "name": "apikey",
        "value": "={{ $env.DJANGO_API_KEY }}"
      }
    ]
  }
}
```

### **Como usar:**

1. **Importe:** n8n → Import from File → `TEMPLATE_Bot_Universal_VPS.json`
2. **Configure variáveis** (docker-compose.yml ou .env)
3. **Reinicie n8n** para carregar variáveis
4. **Ative o workflow**
5. **Teste!**

---

## 🔐 Onde Obter as Chaves?

### **1. DJANGO_API_KEY**

Definida em `config/settings.py`:

```python
# config/settings.py linha 122
N8N_API_KEY = config('N8N_API_KEY', default='desenvolvimento-inseguro-mudar-em-producao')
```

**No .env do Django:**
```bash
N8N_API_KEY=minhaChaveSecretaN8n123456
```

**Use esta mesma chave no n8n!**

### **2. EVOLUTION_API_KEY**

É a **API Key Global** da Evolution API.

**Como obter:**
1. Acesse painel da Evolution
2. Settings → API Key
3. Ou defina no `.env` da Evolution:

```bash
# .env da Evolution API
AUTHENTICATION_API_KEY=SuaChaveSecretaEvolution123
```

### **3. OPENAI_API_KEY**

**Como obter:**
1. Acesse: https://platform.openai.com/api-keys
2. Clique em "Create new secret key"
3. Copie a chave: `sk-proj-xxxxxxxxxxxx`

**⚠️ IMPORTANTE:**
- Adicione créditos na conta OpenAI
- Modelo recomendado: `gpt-4o-mini` (mais barato)

---

## 🧪 Como Testar

### **Teste 1: Verificar se variáveis foram carregadas**

Crie um workflow simples:

**Node 1: Manual Trigger**
**Node 2: Code**

```javascript
return [{
  json: {
    django_url: $env.DJANGO_API_URL,
    django_key_primeiros_5: $env.DJANGO_API_KEY?.substring(0, 5) + '...',
    evolution_url: $env.EVOLUTION_API_URL,
    openai_key_primeiros_5: $env.OPENAI_API_KEY?.substring(0, 5) + '...'
  }
}];
```

**Execute e verifique se mostra os valores.**

### **Teste 2: Testar API Django**

**Node: HTTP Request**

```json
{
  "method": "GET",
  "url": "={{ $env.DJANGO_API_URL }}/api/n8n/servicos/",
  "authentication": "none",
  "sendHeaders": true,
  "headerParameters": {
    "parameters": [
      {
        "name": "apikey",
        "value": "={{ $env.DJANGO_API_KEY }}"
      },
      {
        "name": "empresa_id",
        "value": "1"
      }
    ]
  }
}
```

**Execute e deve retornar lista de serviços.**

### **Teste 3: Testar OpenAI**

**Node: HTTP Request**

```json
{
  "method": "POST",
  "url": "https://api.openai.com/v1/chat/completions",
  "authentication": "none",
  "sendHeaders": true,
  "headerParameters": {
    "parameters": [
      {
        "name": "Authorization",
        "value": "=Bearer {{ $env.OPENAI_API_KEY }}"
      }
    ]
  },
  "sendBody": true,
  "bodyParameters": {
    "model": "gpt-4o-mini",
    "messages": [
      {
        "role": "user",
        "content": "Diga apenas: funcionou!"
      }
    ]
  }
}
```

**Deve retornar: "funcionou!"**

---

## ⚠️ Troubleshooting

### **Variável retorna undefined**

**Problema:** `{{ $env.DJANGO_API_KEY }}` retorna `undefined`

**Soluções:**

1. **Verifique o nome da variável:**
   - Docker: `environment:` no `docker-compose.yml`
   - Systemd: `EnvironmentFile=` correto
   - PM2: `env:` no `ecosystem.config.js`

2. **Reinicie n8n:**
   ```bash
   # Docker
   docker-compose restart n8n

   # Systemd
   sudo systemctl restart n8n

   # PM2
   pm2 restart n8n
   ```

3. **Verifique se carregou:**
   ```bash
   # Docker
   docker exec -it n8n_container env | grep DJANGO

   # Systemd/PM2
   systemctl show n8n | grep Environment
   ```

### **HTTP Request retorna 401/403**

**Problema:** API Django retorna "API Key inválida"

**Soluções:**

1. Confirme que a chave é a mesma:
   ```python
   # Django settings.py
   N8N_API_KEY = 'minhaChave123'
   ```

   ```yaml
   # docker-compose.yml
   DJANGO_API_KEY: 'minhaChave123'  # MESMA chave!
   ```

2. Verifique header:
   ```
   Header name: apikey  (minúsculo!)
   Header value: {{ $env.DJANGO_API_KEY }}
   ```

### **OpenAI retorna erro de quota**

**Problema:** "You exceeded your current quota"

**Solução:**
1. Acesse: https://platform.openai.com/account/billing
2. Adicione créditos ($5 mínimo)
3. Aguarde alguns minutos

---

## 📋 Checklist de Configuração

- [ ] n8n instalado e rodando
- [ ] Variáveis definidas (docker-compose.yml ou .env)
- [ ] n8n reiniciado para carregar variáveis
- [ ] Template VPS importado
- [ ] Teste de variáveis OK
- [ ] Teste de API Django OK
- [ ] Teste de OpenAI OK
- [ ] Workflow ativado
- [ ] Primeiro teste end-to-end OK

---

## 🎯 Resumo

**3 Formas de Configurar:**

| Método | Segurança | Facilidade | Recomendado |
|--------|-----------|------------|-------------|
| Variáveis de Ambiente | ✅ Alta | ⭐⭐⭐ | **SIM** |
| Hardcode direto | ❌ Baixa | ⭐⭐⭐⭐⭐ | Só para teste |
| Sistema de Credenciais | ✅ Alta | ⭐⭐ | Se disponível |

**Melhor opção:** ✅ **Variáveis de Ambiente no Docker/Systemd**

---

## 🚀 Próximo Passo

Com as variáveis configuradas, você pode:
1. Importar `TEMPLATE_Bot_Universal_VPS.json`
2. Ativar o workflow
3. Começar a receber mensagens do WhatsApp! 🎉

Está com algum erro específico? Me avise que te ajudo a resolver!
