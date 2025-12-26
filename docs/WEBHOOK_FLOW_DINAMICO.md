# 🔄 Fluxo de Webhook Dinâmico - Multi-tenant

## ❓ Dúvida: Como o webhook sabe qual instância conectar?

**Pergunta:** Se o workflow é um só para todos os clientes, como ele sabe de qual empresa/instância veio a mensagem e para qual deve responder?

**Resposta:** A Evolution API **envia o nome da instância no payload** do webhook! 🎯

---

## 🎬 Fluxo Passo a Passo

### **Cenário: 3 Empresas usando o sistema**

```
┌─────────────────────────────────────────────────────────┐
│  EMPRESA 1: Barbearia do Pedro                          │
│  Instância Evolution: "empresa_barbearia_pedro"         │
│  WhatsApp: +55 11 98765-4321                            │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│  EMPRESA 2: Salão da Maria                              │
│  Instância Evolution: "empresa_salao_maria"             │
│  WhatsApp: +55 11 91234-5678                            │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│  EMPRESA 3: Clínica Dr. João                            │
│  Instância Evolution: "empresa_clinica_joao"            │
│  WhatsApp: +55 11 99999-8888                            │
└─────────────────────────────────────────────────────────┘
```

---

## 📡 Opção A: Evolution → n8n Direto (Mais Simples)

### **Passo 1: Configurar webhook na Evolution**

Quando você cria a instância da Evolution (via `evolution_api.py`), você define:

```python
# empresas/services/evolution_api.py

webhook_url = f"https://seu-n8n.com/webhook/bot-universal"

data = {
    "instanceName": "empresa_barbearia_pedro",
    "webhook": {
        "url": webhook_url,  # MESMA URL para todos!
        "byEvents": True,
        "events": ["MESSAGES_UPSERT"]
    }
}
```

**⚠️ IMPORTANTE:** A URL do webhook é a MESMA para todas as empresas!

### **Passo 2: Cliente envia mensagem no WhatsApp**

```
Cliente João envia no WhatsApp da Barbearia do Pedro:
"Quero agendar corte amanhã 14h"
```

### **Passo 3: Evolution envia webhook para n8n**

A Evolution API envia um POST para:
```
https://seu-n8n.com/webhook/bot-universal
```

**Payload enviado pela Evolution:**

```json
{
  "instance": "empresa_barbearia_pedro",  ← IDENTIFICA A EMPRESA!
  "data": {
    "key": {
      "remoteJid": "5511999999999@s.whatsapp.net",
      "fromMe": false,
      "id": "msg-id-123"
    },
    "pushName": "João Silva",
    "message": {
      "conversation": "Quero agendar corte amanhã 14h"
    },
    "messageTimestamp": "1703692800"
  },
  "destination": "5511987654321@s.whatsapp.net",
  "date_time": "2025-12-26T14:30:00Z",
  "server_url": "https://evolution.axiodev.cloud",
  "apikey": "sua-evolution-api-key"
}
```

### **Passo 4: n8n extrai a instância**

No node **"⚙️ Configurações + Dados"** (que você editou):

```javascript
{
  "instance_name": "={{ $json.instance || '' }}",  // Extrai "empresa_barbearia_pedro"
  "telefone": "={{ $json.data?.key?.remoteJid?.replace('@s.whatsapp.net', '') }}",
  "mensagem": "={{ $json.data?.message?.conversation }}",
  "nome_cliente": "={{ $json.data?.pushName }}"
}
```

**Resultado:**
```json
{
  "instance_name": "empresa_barbearia_pedro",  ← Agora sabemos quem é!
  "telefone": "5511999999999",
  "mensagem": "Quero agendar corte amanhã 14h",
  "nome_cliente": "João Silva"
}
```

### **Passo 5: n8n busca dados da empresa certa**

Mas espera... como saber o `empresa_id` só com o `instance_name`?

**Solução 1: Evolution envia empresa_id (RECOMENDADO)**

Modifique o Django para adicionar `empresa_id` ao webhook da Evolution:

```python
# empresas/services/evolution_api.py

# Ao criar instância, adicione empresa_id no webhook URL
webhook_url = f"https://seu-n8n.com/webhook/bot-universal?empresa_id={self.config.empresa.id}"
```

Ou use webhook do Django como intermediário (Opção B abaixo).

**Solução 2: Fazer lookup no n8n**

Adicionar um node no n8n que busca empresa_id pelo instance_name:

```javascript
// Node extra: "Buscar Empresa ID"
GET {{ config_django_url }}/api/n8n/empresa-by-instance/?instance={{ $json.instance_name }}

// Retorna:
{
  "empresa_id": 1,
  "nome": "Barbearia do Pedro"
}
```

### **Passo 6: n8n envia resposta para instância correta**

No node **"Enviar Resposta WhatsApp"**:

```javascript
{
  "url": "={{ $json.config_evolution_url }}/message/sendText/{{ $json.instance_name }}",
  //                                                           ↑
  //                                    Usa a instância que veio no webhook!

  "body": {
    "number": "{{ $json.telefone }}",
    "text": "✅ Agendamento confirmado! ..."
  }
}
```

**Expande para:**
```
POST https://evolution.axiodev.cloud/message/sendText/empresa_barbearia_pedro

Body:
{
  "number": "5511999999999",
  "text": "✅ Agendamento confirmado! ..."
}
```

**A mensagem vai para o WhatsApp CERTO!** ✅

---

## 📡 Opção B: Evolution → Django → n8n (Mais Controle)

### **Fluxo:**

```
┌──────────────┐      ┌──────────────┐      ┌──────────────┐
│   Evolution  │─────▶│    Django    │─────▶│     n8n      │
│     API      │      │   Webhook    │      │   Workflow   │
└──────────────┘      └──────────────┘      └──────────────┘
     Envia              Adiciona info        Processa e
   mensagem           empresa_id, valida     responde
```

### **Passo 1: Evolution envia para Django**

Webhook configurado na Evolution:
```
https://axiogestto.com/api/webhooks/whatsapp/1/abc123def/
                                              ↑   ↑
                                         empresa_id  secret
```

### **Passo 2: Django recebe e valida**

```python
# configuracoes/views.py ou similar

@csrf_exempt
def whatsapp_webhook_saas(request, empresa_id, secret):
    """Webhook intermediário - valida e encaminha para n8n"""

    # Validar empresa e secret
    try:
        empresa = Empresa.objects.get(id=empresa_id)
        config = empresa.whatsapp_config

        if config.webhook_secret != secret:
            return JsonResponse({'error': 'Secret inválido'}, status=403)
    except Empresa.DoesNotExist:
        return JsonResponse({'error': 'Empresa não encontrada'}, status=404)

    # Validar assinatura Stripe, limites do plano, etc.
    if not empresa.assinatura_ativa:
        return JsonResponse({'error': 'Assinatura inativa'}, status=402)

    # Montar payload enriquecido para n8n
    payload_n8n = {
        'empresa_id': empresa.id,  # ← Adiciona empresa_id
        'empresa_nome': empresa.nome,
        'instance': config.instance_name,
        'body': json.loads(request.body)  # Payload original da Evolution
    }

    # Encaminhar para n8n
    import requests
    n8n_webhook_url = settings.N8N_WEBHOOK_URL  # Da .env

    response = requests.post(
        n8n_webhook_url,
        json=payload_n8n,
        headers={'Content-Type': 'application/json'}
    )

    return JsonResponse({'success': True, 'forwarded': True})
```

### **Passo 3: n8n recebe payload enriquecido**

```json
{
  "empresa_id": 1,  ← Agora vem do Django!
  "empresa_nome": "Barbearia do Pedro",
  "instance": "empresa_barbearia_pedro",
  "body": {
    "data": {
      "key": { "remoteJid": "..." },
      "message": { "conversation": "..." }
    }
  }
}
```

### **Passo 4: n8n extrai tudo facilmente**

```javascript
// Node "⚙️ Configurações + Dados"
{
  "empresa_id": "={{ $json.empresa_id }}",  ← Já vem pronto!
  "instance_name": "={{ $json.instance }}",
  "telefone": "={{ $json.body.data?.key?.remoteJid?.replace('@s.whatsapp.net', '') }}",
  "mensagem": "={{ $json.body.data?.message?.conversation }}"
}
```

**Vantagens desta abordagem:**
✅ Django valida assinatura, plano, limites
✅ Django adiciona `empresa_id` automaticamente
✅ Django pode fazer rate limiting
✅ Django pode registrar logs/analytics
✅ n8n fica mais simples

---

## 🎯 Qual Opção Usar?

### **Opção A: Evolution → n8n Direto**
👍 **Vantagens:**
- Mais rápido (menos latência)
- Menos complexidade
- n8n gerencia tudo

👎 **Desvantagens:**
- Precisa adicionar `empresa_id` na URL do webhook ou fazer lookup
- Sem validação de assinatura/plano no Django

**Melhor para:** MVPs, sistemas pequenos

---

### **Opção B: Evolution → Django → n8n** ⭐ RECOMENDADO
👍 **Vantagens:**
- Django valida assinatura Stripe
- Django verifica limites do plano
- Django adiciona `empresa_id` automaticamente
- Django pode fazer rate limiting
- Mais controle e segurança

👎 **Desvantagens:**
- Latência adicional (~50-100ms)
- Mais um ponto de falha

**Melhor para:** Produção SaaS, múltiplas empresas

---

## 🔧 Como Implementar (Opção B Recomendada)

### **1. Criar endpoint no Django**

```python
# configuracoes/urls.py

urlpatterns = [
    # ... outras URLs

    path(
        'api/webhooks/whatsapp/<int:empresa_id>/<str:secret>/',
        views.whatsapp_webhook_saas,
        name='whatsapp_webhook_saas'
    ),
]
```

### **2. Implementar view**

```python
# configuracoes/views.py

import requests
import json
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse

@csrf_exempt
def whatsapp_webhook_saas(request, empresa_id, secret):
    """
    Webhook intermediário que:
    1. Valida empresa e secret
    2. Valida assinatura ativa
    3. Adiciona empresa_id ao payload
    4. Encaminha para n8n
    """

    if request.method != 'POST':
        return JsonResponse({'error': 'Apenas POST'}, status=405)

    try:
        # 1. Validar empresa
        empresa = Empresa.objects.select_related('whatsapp_config').get(id=empresa_id)
        config = empresa.whatsapp_config

        # 2. Validar secret
        if config.webhook_secret != secret:
            logger.warning(f"Secret inválido para empresa {empresa_id}")
            return JsonResponse({'error': 'Não autorizado'}, status=403)

        # 3. Validar assinatura ativa
        if not empresa.assinatura_ativa:
            logger.warning(f"Assinatura inativa para empresa {empresa_id}")
            # Enviar mensagem informando assinatura vencida
            # ...
            return JsonResponse({'error': 'Assinatura inativa'}, status=402)

        # 4. Parsear payload da Evolution
        body_raw = request.body.decode('utf-8')
        body = json.loads(body_raw)

        # 5. Montar payload enriquecido
        payload_n8n = {
            'empresa_id': empresa.id,
            'empresa_nome': empresa.nome,
            'instance': config.instance_name,
            'body': body
        }

        # 6. Encaminhar para n8n
        n8n_webhook_url = settings.N8N_WEBHOOK_URL

        response = requests.post(
            n8n_webhook_url,
            json=payload_n8n,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )

        if response.status_code == 200:
            return JsonResponse({
                'success': True,
                'forwarded_to_n8n': True
            })
        else:
            logger.error(f"Erro ao encaminhar para n8n: {response.status_code}")
            return JsonResponse({
                'success': False,
                'error': 'Erro ao processar mensagem'
            }, status=500)

    except Empresa.DoesNotExist:
        logger.error(f"Empresa {empresa_id} não encontrada")
        return JsonResponse({'error': 'Empresa não encontrada'}, status=404)
    except Exception as e:
        logger.error(f"Erro no webhook: {str(e)}")
        return JsonResponse({'error': 'Erro interno'}, status=500)
```

### **3. Adicionar no settings.py**

```python
# config/settings.py

# URL do webhook do n8n
N8N_WEBHOOK_URL = config(
    'N8N_WEBHOOK_URL',
    default='https://seu-n8n.com/webhook/bot-universal'
)
```

### **4. Adicionar no .env**

```bash
N8N_WEBHOOK_URL=https://seu-n8n.com/webhook/bot-universal
```

### **5. Configurar webhook na Evolution**

Quando criar instância, use URL do Django:

```python
# empresas/services/evolution_api.py

def criar_instancia(self):
    # ...

    webhook_url = f"https://axiogestto.com/api/webhooks/whatsapp/{self.config.empresa.id}/{self.config.webhook_secret}/"

    data = {
        "instanceName": instance_name,
        "webhook": {
            "url": webhook_url,  # Aponta para Django!
            "byEvents": True,
            "events": ["MESSAGES_UPSERT"]
        }
    }

    # ...
```

---

## ✅ Resumo Final

### **Como o webhook sabe qual instância conectar?**

1. **Evolution envia `instance` no payload** ✅
2. **Django adiciona `empresa_id` (Opção B)** ✅
3. **n8n extrai `instance_name` do payload** ✅
4. **n8n usa `instance_name` para enviar resposta** ✅

### **Fluxo Recomendado (Opção B):**

```
Cliente WhatsApp
    ↓
Evolution API (empresa_barbearia_pedro)
    ↓
Django /api/webhooks/whatsapp/1/abc123/
    ↓ (valida, adiciona empresa_id)
n8n /webhook/bot-universal
    ↓ (processa, busca dados da empresa_id=1)
Evolution API /message/sendText/empresa_barbearia_pedro
    ↓
Cliente WhatsApp (recebe resposta)
```

### **Diferencial:**
O `instance_name` vem NO PAYLOAD da Evolution!
Por isso funciona dinamicamente para N empresas! 🎯

---

## 🚀 Próximo Passo

Quer que eu:

1. ✅ Implemente o endpoint Django de webhook intermediário?
2. ✅ Atualize o `evolution_api.py` para usar webhook Django?
3. ✅ Crie testes para validar o fluxo completo?

Me avise e implemento! 🚀
