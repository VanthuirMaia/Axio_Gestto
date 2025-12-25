# 🔗 Webhook WhatsApp Multi-Tenant (SaaS)

## Visão Geral

O endpoint `/api/whatsapp-webhook/` é o **webhook público multi-tenant** que detecta automaticamente qual empresa (tenant) deve processar cada mensagem baseado no `instance_id` do WhatsApp.

**Diferenças entre endpoints:**

| Característica | `/api/bot/processar/` (Antigo) | `/api/whatsapp-webhook/` (SaaS) |
|----------------|--------------------------------|----------------------------------|
| **Autenticação** | API Key + empresa_id manual | Auto-detect pelo instance_id |
| **Uso** | Single-tenant (1 empresa) | Multi-tenant (N empresas) |
| **Verificação** | Nenhuma | Assinatura ativa + limites |
| **Segurança** | Headers customizados | Instance ID único por empresa |

---

## 🎯 Endpoint

```
POST /api/whatsapp-webhook/
```

**Características:**
- ✅ Público (sem autenticação via header)
- ✅ Detecta tenant automaticamente
- ✅ Valida status da assinatura
- ✅ Verifica limites do plano
- ✅ Compatível com Evolution API e Z-API

---

## 📡 Configuração no Evolution API

### 1. Criar Instância

Na Evolution API, crie uma nova instância com nome único:

```bash
curl -X POST https://sua-evolution-api.com/instance/create \
  -H "apikey: SUA_API_KEY" \
  -d '{
    "instanceName": "empresa123",
    "qrcode": true,
    "webhook": {
      "url": "https://seu-dominio.com/api/whatsapp-webhook/",
      "events": ["messages.upsert"],
      "enabled": true
    }
  }'
```

### 2. Configurar no Onboarding

No **Passo 3 do Onboarding**, o cliente deve informar:

- **Instance ID**: `empresa123` (mesmo nome da instância)
- **Número WhatsApp**: `(11) 99999-9999`
- **Token (opcional)**: Token da Evolution API (se precisar autenticar retornos)

### 3. Testar Webhook

Envie uma mensagem de teste no WhatsApp conectado e verifique os logs.

---

## 📨 Fluxo de Processamento

```
1. WhatsApp recebe mensagem do cliente
2. Evolution API envia webhook para /api/whatsapp-webhook/
3. Django extrai "instance" do payload
4. Busca empresa onde whatsapp_instance_id = instance
5. Valida assinatura está ativa ou em trial
6. Verifica se não excedeu limite de agendamentos do plano
7. Roteia para n8n processar mensagem com IA
8. n8n retorna intent processada
9. Django executa ação (agendar, cancelar, consultar)
10. Retorna resposta para Evolution API
11. Evolution API envia resposta ao cliente no WhatsApp
```

---

## 🔒 Validações de Segurança

### 1. Instance ID Único

O campo `empresa.whatsapp_instance_id` deve ser **único** no banco:

```python
# Validação automática no onboarding
if Empresa.objects.filter(whatsapp_instance_id=instance_id).exclude(id=empresa.id).exists():
    raise ValidationError('Instance ID já em uso')
```

### 2. Verificação de Assinatura

```python
# Bloqueia se assinatura não está ativa
if assinatura.status not in ['ativa', 'trial']:
    return Response({
        'erro': 'Assinatura suspensa/cancelada'
    }, status=402)
```

### 3. Limites do Plano

```python
# Verifica limite de agendamentos do mês
if agendamentos_mes >= plano.max_agendamentos_mes:
    return Response({
        'erro': 'Limite de agendamentos atingido'
    }, status=429)
```

---

## 📦 Payloads

### Webhook Bruto (Evolution API → Django)

```json
{
  "instance": "empresa123",
  "event": "messages.upsert",
  "data": {
    "key": {
      "remoteJid": "5511999998888@s.whatsapp.net",
      "fromMe": false,
      "id": "3EB0C6A8D9F6E2C4C8A1"
    },
    "message": {
      "conversation": "Quero agendar corte amanhã 14h"
    },
    "pushName": "João Silva",
    "messageTimestamp": 1672531200
  }
}
```

**Resposta Django (validação OK):**

```json
{
  "sucesso": true,
  "mensagem": "Webhook recebido. Empresa validada.",
  "empresa_id": 1,
  "empresa_nome": "Barbearia Example",
  "assinatura_status": "ativa",
  "plano": "profissional"
}
```

### Webhook Processado (n8n → Django)

Depois que n8n processa a mensagem com IA:

```json
{
  "instance": "empresa123",
  "telefone": "5511999998888",
  "mensagem_original": "Quero agendar corte amanhã 14h",
  "intencao": "agendar",
  "dados": {
    "servico": "corte de cabelo",
    "data": "2025-12-26",
    "hora": "14:00",
    "profissional": null
  }
}
```

**Resposta Django (agendamento criado):**

```json
{
  "sucesso": true,
  "mensagem": "✅ Agendamento confirmado!\n\n📅 Serviço: Corte de Cabelo\n👤 Profissional: João Silva\n🕐 Data: 26/12/2025 às 14:00\n💰 Valor: R$ 45.00\n📝 Código: AB12CD\n\nPara cancelar: CANCELAR AB12CD",
  "dados": {
    "agendamento_id": 123,
    "codigo": "AB12CD",
    "data_hora": "26/12/2025 às 14:00",
    "valor": 45.0
  }
}
```

---

## ⚠️ Erros Comuns

### 400 - Instance ID não fornecido

```json
{
  "sucesso": false,
  "erro": "Instance ID não fornecido. Envie campo 'instance' no payload."
}
```

**Solução:** Verifique se o webhook está enviando o campo `instance`.

### 404 - Empresa não encontrada

```json
{
  "sucesso": false,
  "erro": "Nenhuma empresa encontrada para instance 'xyz123'"
}
```

**Solução:**
1. Verifique se a empresa configurou o WhatsApp no onboarding
2. Confirme que `whatsapp_instance_id` está salvo no banco
3. Verifique se `empresa.ativa = True` e `whatsapp_conectado = True`

### 402 - Assinatura inativa

```json
{
  "sucesso": false,
  "erro": "Assinatura suspensa. Regularize o pagamento para continuar.",
  "status_assinatura": "suspensa",
  "plano": "essencial"
}
```

**Solução:** Cliente deve regularizar pagamento na área de assinaturas.

### 402 - Assinatura expirada

```json
{
  "sucesso": false,
  "erro": "Assinatura expirada. Renove para continuar usando o bot.",
  "data_expiracao": "25/12/2025"
}
```

**Solução:** Sistema suspende automaticamente. Cliente deve renovar.

### 429 - Limite de agendamentos atingido

```json
{
  "sucesso": false,
  "erro": "Limite de 500 agendamentos/mês atingido. Faça upgrade do plano.",
  "agendamentos_usados": 500,
  "limite": 500,
  "plano_atual": "essencial"
}
```

**Solução:** Cliente deve fazer upgrade para plano superior.

---

## 🔧 Configuração n8n

### Workflow Sugerido

```
1. Webhook Node (recebe do Evolution API)
   ↓
2. Function Node (extrai dados da mensagem)
   ↓
3. HTTP Request (POST para /api/whatsapp-webhook/)
   ↓
4. IF Node (verifica se precisa processar com IA)
   ↓
5. OpenAI Node (extrai intent + dados)
   ↓
6. HTTP Request (POST novamente com dados processados)
   ↓
7. Evolution API Send Message (envia resposta)
```

### Exemplo de Function Node

```javascript
// Extrair dados básicos da mensagem
const instance = $input.item.json.instance;
const remoteJid = $input.item.json.data.key.remoteJid;
const telefone = remoteJid.replace('@s.whatsapp.net', '');
const mensagem = $input.item.json.data.message.conversation ||
                 $input.item.json.data.message.extendedTextMessage?.text || '';

return {
  json: {
    instance: instance,
    telefone: telefone,
    mensagem_original: mensagem,
    raw: $input.item.json
  }
};
```

---

## 📊 Monitoramento

### Ver logs de mensagens

```python
from agendamentos.models import LogMensagemBot

# Últimas 100 mensagens processadas
logs = LogMensagemBot.objects.filter(
    empresa_id=1
).order_by('-criado_em')[:100]

for log in logs:
    print(f"{log.telefone}: {log.intencao_detectada} - {log.status}")
```

### Verificar assinaturas expiradas

```python
from django.utils.timezone import now
from assinaturas.models import Assinatura

# Assinaturas que expiram em 7 dias
expirando = Assinatura.objects.filter(
    status='ativa',
    data_expiracao__lte=now() + timedelta(days=7)
)

for assinatura in expirando:
    print(f"{assinatura.empresa.nome} expira em {assinatura.data_expiracao}")
```

---

## 🚀 Deploy

### Nginx Rate Limiting

Para proteger o webhook de abuse, configure rate limit:

```nginx
# /etc/nginx/sites-available/gestto

http {
    limit_req_zone $binary_remote_addr zone=webhook_limit:10m rate=10r/s;

    server {
        location /api/whatsapp-webhook/ {
            limit_req zone=webhook_limit burst=20;
            proxy_pass http://django;
        }
    }
}
```

### Variáveis de Ambiente

Não são necessárias variáveis adicionais. O webhook funciona com a configuração padrão do Django.

---

## ✅ Checklist de Implementação

- [x] Criar endpoint `/api/whatsapp-webhook/`
- [x] Adicionar validação de assinatura
- [x] Verificar limites do plano
- [x] Atualizar onboarding step 3 para coletar instance_id
- [x] Adicionar validação de instance_id único
- [x] Documentar fluxo completo
- [ ] Testar com Evolution API real
- [ ] Configurar rate limiting no nginx
- [ ] Implementar retry logic para webhooks falhados
- [ ] Dashboard de monitoramento de webhooks

---

## 📚 Recursos

- **Evolution API Docs**: https://doc.evolution-api.com/
- **Z-API Docs**: https://developer.z-api.io/
- **n8n Webhook Node**: https://docs.n8n.io/integrations/builtin/core-nodes/n8n-nodes-base.webhook/

---

**Atualizado em:** 25/12/2025
**Status:** ✅ Implementado (aguardando testes)
