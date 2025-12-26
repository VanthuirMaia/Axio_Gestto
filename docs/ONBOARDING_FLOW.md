# 🔄 Fluxo de Onboarding - Cliente Conecta WhatsApp

## Sua Dúvida Respondida

**Pergunta:** Como o cliente vai scanear o QR code e conectar ao n8n? Será um fluxo único para todos ou cada um terá o seu?

**Resposta Curta:** ✅ **Cada cliente terá sua própria instância** no Evolution API, mas todos usam o **mesmo n8n** (centralizado) que roteia as mensagens corretamente para cada empresa.

---

## 🎯 Arquitetura Multi-Tenant

### Opção Implementada no Seu Sistema: **Instâncias Separadas + n8n Centralizado**

```
┌─────────────────────────────────────────────────────────────┐
│                    EVOLUTION API (UMA)                       │
│  https://evolution.axiodev.cloud                            │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Instância 1: "empresa_barbearia_pedro"                     │
│  ├─ WhatsApp: +55 11 99999-8888                             │
│  ├─ Webhook: /api/webhooks/whatsapp/1/secret123/            │
│  └─ Events: MESSAGES_UPSERT, CONNECTION_UPDATE              │
│                                                              │
│  Instância 2: "empresa_salao_maria"                         │
│  ├─ WhatsApp: +55 11 98888-7777                             │
│  ├─ Webhook: /api/webhooks/whatsapp/2/secret456/            │
│  └─ Events: MESSAGES_UPSERT, CONNECTION_UPDATE              │
│                                                              │
│  Instância 3: "empresa_clinica_joao"                        │
│  ├─ WhatsApp: +55 11 97777-6666                             │
│  ├─ Webhook: /api/webhooks/whatsapp/3/secret789/            │
│  └─ Events: MESSAGES_UPSERT, CONNECTION_UPDATE              │
│                                                              │
└─────────────────────────────────────────────────────────────┘
                            │
                            │ Webhook
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    DJANGO (SEU SISTEMA)                      │
│  https://axiogestto.com                                     │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  /api/webhooks/whatsapp/1/secret123/                        │
│  → Identifica: Empresa ID = 1                               │
│  → Valida: secret123                                        │
│  → Processa ou encaminha para n8n                           │
│                                                              │
│  /api/webhooks/whatsapp/2/secret456/                        │
│  → Identifica: Empresa ID = 2                               │
│  → Valida: secret456                                        │
│  → Processa ou encaminha para n8n                           │
│                                                              │
└─────────────────────────────────────────────────────────────┘
                            │
                            │ HTTP Request (opcional)
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    n8n (UM CENTRALIZADO)                     │
│  https://seu-n8n.com                                        │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Workflow: "Bot Atendimento Universal"                      │
│  ├─ Webhook Trigger                                         │
│  ├─ Switch (roteia por empresa_id)                          │
│  ├─ OpenAI Agent (processa mensagem)                        │
│  ├─ HTTP Request → Django API                               │
│  │   - GET /api/n8n/servicos/?empresa_id=1                  │
│  │   - POST /api/bot/processar/                             │
│  └─ Evolution API (envia resposta)                          │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## 📱 Fluxo de Onboarding Completo (Passo a Passo)

### **Cenário:** Pedro é dono da "Barbearia do Pedro" e quer usar o sistema

### **Etapa 1: Cadastro Inicial** (Landing Page)

```
1. Pedro acessa: https://axiogestto.com
2. Clica em "Começar Agora"
3. Preenche formulário:
   - Nome da empresa: "Barbearia do Pedro"
   - CNPJ: 12.345.678/0001-90
   - Email: pedro@barbearia.com
   - Telefone: (11) 99999-8888
   - Senha: ********
4. Escolhe plano: "Básico - R$ 49/mês"
5. Sistema cria:
   ✅ Empresa ID: 1
   ✅ Usuário: pedro@barbearia.com
   ✅ Assinatura: Trial 14 dias
   ✅ Slug: "barbearia-do-pedro"
```

### **Etapa 2: Onboarding Wizard**

```
Pedro faz login → Sistema redireciona para /app/onboarding/

Tela 1: "Bem-vindo! Vamos configurar sua empresa"
Tela 2: "Configure seus serviços" (Corte, Barba, etc)
Tela 3: "Adicione seus profissionais" (Pedro, João)
Tela 4: "Configure horários de funcionamento"
Tela 5: ⭐ "Conecte seu WhatsApp" ← AQUI!
```

### **Etapa 3: Conexão do WhatsApp**

#### **3.1. Pedro clica em "Conectar WhatsApp"**

```python
# Frontend chama via AJAX:
POST /configuracoes/whatsapp/criar-instancia/

# Django (configuracoes/views.py):
def whatsapp_criar_instancia(request):
    empresa = request.user.empresa  # Empresa ID: 1
    config = ConfiguracaoWhatsApp.objects.get(empresa=empresa)

    # 1. Gerar nome único da instância
    instance_name = "empresa_barbearia_pedro"  # ou config.gerar_instance_name()

    # 2. Gerar secret para webhook
    webhook_secret = "abc123def456"  # gerado aleatoriamente

    # 3. Montar webhook URL
    webhook_url = "https://axiogestto.com/api/webhooks/whatsapp/1/abc123def456/"

    # 4. Chamar Evolution API
    service = EvolutionAPIService(config)
    result = service.criar_instancia()
    # ↓
    # POST https://evolution.axiodev.cloud/instance/create
    # {
    #   "instanceName": "empresa_barbearia_pedro",
    #   "qrcode": true,
    #   "webhook": {
    #     "url": "https://axiogestto.com/api/webhooks/whatsapp/1/abc123def456/",
    #     "byEvents": true,
    #     "base64": true,
    #     "events": ["MESSAGES_UPSERT", "CONNECTION_UPDATE", ...]
    #   }
    # }

    # 5. Retornar QR Code
    return JsonResponse({
        'success': True,
        'qrcode': result['qrcode'],  # base64
        'instance_name': instance_name
    })
```

#### **3.2. Frontend mostra QR Code**

```javascript
// Frontend recebe resposta e mostra QR Code
<div id="qr-code-container">
  <img src="data:image/png;base64,{{ qrcode }}" />
  <p>Abra o WhatsApp no celular e escaneie este QR Code</p>
</div>

// Inicia polling para verificar conexão
setInterval(() => {
  fetch('/configuracoes/whatsapp/verificar-status/')
    .then(res => res.json())
    .then(data => {
      if (data.conectado) {
        // ✅ Conectou! Redirecionar para dashboard
        window.location.href = '/app/dashboard/';
      }
    });
}, 3000); // A cada 3 segundos
```

#### **3.3. Pedro escaneia com celular**

```
1. Pedro pega o celular
2. Abre WhatsApp
3. Vai em Aparelhos Conectados → Conectar Aparelho
4. Escaneia o QR Code da tela
5. WhatsApp conecta à Evolution API
```

#### **3.4. Evolution API notifica via webhook**

```
Evolution API detecta conexão →
POST https://axiogestto.com/api/webhooks/whatsapp/1/abc123def456/
{
  "event": "CONNECTION_UPDATE",
  "instance": "empresa_barbearia_pedro",
  "data": {
    "state": "open",
    "profilePictureUrl": "https://...",
    "displayName": "Barbearia do Pedro"
  }
}

# Django processa webhook (empresas/api_views.py):
def whatsapp_webhook(request, empresa_id, secret):
    # 1. Valida secret
    if secret != config.webhook_secret:
        return 403

    # 2. Atualiza status
    config.status = 'conectado'
    config.numero_conectado = '+55 11 99999-8888'
    config.nome_perfil = 'Barbearia do Pedro'
    config.save()

    # ✅ Pronto! WhatsApp conectado!
```

---

## 🔀 Como n8n se Conecta? (2 Opções)

### **Opção A: Django Processa + n8n para IA (RECOMENDADO)**

```
Cliente WhatsApp envia: "Quero agendar corte amanhã 14h"
    │
    ▼
Evolution API
    │ webhook
    ▼
Django /api/webhooks/whatsapp/1/abc123def456/
    │
    ├─ Identifica: Empresa ID = 1
    ├─ Salva mensagem no banco
    │
    ├─ É mensagem simples? (ex: "oi", "horários")
    │   └─ SIM → Responde direto do Django
    │
    └─ É mensagem complexa? (ex: "quero agendar...")
        └─ NÃO → Chama n8n
            │
            ▼
n8n Workflow "Bot Universal"
    │
    ├─ Recebe: empresa_id=1, mensagem="Quero agendar..."
    ├─ OpenAI processa
    ├─ Extrai: { intencao: "agendar", servico: "corte", data: "amanhã", hora: "14h" }
    │
    ├─ HTTP Request → Django
    │   POST /api/bot/processar/
    │   Headers: apikey, empresa_id=1
    │   Body: { intencao, dados... }
    │
    ├─ Django responde: { sucesso: true, mensagem: "✅ Agendado!" }
    │
    └─ n8n envia resposta
        │
        ▼
Evolution API /message/sendText/empresa_barbearia_pedro
    │
    ▼
WhatsApp do Cliente
```

### **Opção B: n8n Processa Tudo (Mais Flexível)**

```
Cliente WhatsApp envia: "Quero agendar corte amanhã 14h"
    │
    ▼
Evolution API
    │ webhook DIRETO para n8n
    ▼
n8n Workflow "Bot - Barbearia do Pedro"
    │
    ├─ Webhook Trigger (específico para empresa_id=1)
    ├─ OpenAI processa
    ├─ HTTP Requests para Django:
    │   - GET /api/n8n/servicos/?empresa_id=1
    │   - GET /api/n8n/profissionais/?empresa_id=1
    │   - POST /api/n8n/horarios-disponiveis/
    │   - POST /api/bot/processar/
    │
    └─ Evolution API envia resposta
```

---

## 🏢 Multi-Tenant: 1 n8n ou Vários?

### **Opção 1: UM n8n Centralizado (RECOMENDADO)**

✅ **Vantagens:**
- Gerenciamento único
- Custos reduzidos
- Atualizações centralizadas
- Fácil manutenção

❌ **Desvantagens:**
- Todos os clientes compartilham recursos
- Se cair, todos ficam sem bot

**Como funciona:**

```
n8n
│
├─ Workflow: "Bot Universal"
│  ├─ Webhook: /webhook/bot-universal
│  ├─ Switch (por empresa_id)
│  │  ├─ Empresa 1 → Config específica
│  │  ├─ Empresa 2 → Config específica
│  │  └─ Empresa 3 → Config específica
│  │
│  └─ HTTP Requests parametrizados
│     - Headers: { "empresa_id": "{{ $json.empresa_id }}" }
```

### **Opção 2: UM n8n por Cliente (Isolamento Total)**

✅ **Vantagens:**
- Isolamento completo
- Customização total por cliente
- Falha de um não afeta outros

❌ **Desvantagens:**
- Muito caro (N instâncias n8n)
- Gerenciamento complexo
- Difícil manutenção

**Só vale se:**
- Cliente pagar muito (plano enterprise)
- Exigir SLA 99.99%
- Precisar de customizações extremas

---

## 🎯 Configuração Atual do Seu Sistema

### O que já está implementado:

```python
# Cada empresa tem:
empresa = Empresa.objects.get(id=1)
config = ConfiguracaoWhatsApp.objects.get(empresa=empresa)

# Dados únicos:
config.instance_name = "empresa_barbearia_pedro"
config.webhook_url = "https://axiogestto.com/api/webhooks/whatsapp/1/abc123/"
config.webhook_secret = "abc123"
config.numero_conectado = "+55 11 99999-8888"

# Evolution API:
# - Uma Evolution centralizada
# - Múltiplas instâncias (uma por empresa)
# - Cada instância = 1 WhatsApp Business

# Django recebe webhooks:
/api/webhooks/whatsapp/<empresa_id>/<secret>/
→ Identifica empresa automaticamente
→ Processa ou encaminha para n8n
```

---

## 📊 Resumo Visual

### **Estrutura Atual:**

```
┌──────────────────────────────────────────────────────┐
│              1 EVOLUTION API CENTRAL                  │
│  (evolution.axiodev.cloud)                           │
│                                                       │
│  ┌─────────────────┐  ┌─────────────────┐           │
│  │ Instância 1     │  │ Instância 2     │  ...      │
│  │ Empresa ID: 1   │  │ Empresa ID: 2   │           │
│  │ WhatsApp: 9999  │  │ WhatsApp: 8888  │           │
│  └─────────────────┘  └─────────────────┘           │
└──────────────────────────────────────────────────────┘
                      │ webhooks
                      ▼
┌──────────────────────────────────────────────────────┐
│              1 DJANGO CENTRAL                         │
│  (axiogestto.com)                                    │
│                                                       │
│  Webhook Router:                                     │
│  /api/webhooks/whatsapp/1/secret1/ → Empresa 1      │
│  /api/webhooks/whatsapp/2/secret2/ → Empresa 2      │
│                                                       │
│  APIs n8n:                                           │
│  /api/n8n/servicos/?empresa_id=1                    │
│  /api/bot/processar/ + header empresa_id=1          │
└──────────────────────────────────────────────────────┘
                      │ (opcional)
                      ▼
┌──────────────────────────────────────────────────────┐
│              1 n8n CENTRAL (Opcional)                 │
│  (seu-n8n.com)                                       │
│                                                       │
│  Workflow Universal com Switch por empresa_id        │
└──────────────────────────────────────────────────────┘
```

### **Fluxo do Cliente:**

```
1. Pedro se cadastra → Empresa ID: 1
2. Pedro conecta WhatsApp → Instância: "empresa_barbearia_pedro"
3. Cliente envia mensagem → Evolution → Django (identifica empresa_id=1)
4. Django processa OU chama n8n
5. Resposta volta para WhatsApp do cliente
```

---

## ✅ Conclusão

**Resposta final:**

✅ **Cada cliente TEM SUA PRÓPRIA instância** na Evolution API
✅ **Mas todos usam o MESMO Django** (multi-tenant)
✅ **E podem usar o MESMO n8n** (roteamento por empresa_id)

**Benefícios:**
- Isolamento de WhatsApp (cada empresa tem seu número)
- Compartilhamento de infraestrutura (economia)
- Fácil gerenciamento
- Escalável

**Já está implementado:** ✅ Sim! Tudo pronto no código.

Ficou claro? Quer que eu mostre como configurar o n8n universal ou prefere outro approach?
