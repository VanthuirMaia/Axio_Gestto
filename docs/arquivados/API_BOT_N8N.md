# API Bot WhatsApp - Documentação para n8n

## 🎯 Visão Geral

Esta API centraliza TODA a lógica de negócio do bot WhatsApp.

**n8n faz:** Tradução (WhatsApp ↔ Django) + IA
**Django faz:** TUDO (validações, regras, banco de dados)

---

## 🔑 Autenticação

Todas as requisições precisam dos headers:

```
X-API-Key: desenvolvimento-inseguro-mudar-em-producao
X-Empresa-ID: 1
```

**Em produção:** Gere uma API Key segura e configure no `.env`:
```
N8N_API_KEY=sua-chave-super-secreta-aqui
```

---

## 📡 Endpoint Principal

### **POST** `/api/bot/processar/`

Endpoint único que processa todos os comandos interpretados pela IA.

---

## 📥 Requisição

```json
{
  "telefone": "5511999998888",
  "mensagem_original": "Quero agendar corte amanhã 14h",
  "intencao": "agendar",
  "dados": {
    "servico": "corte de cabelo",
    "data": "2025-12-23",
    "hora": "14:00",
    "profissional": "João"
  }
}
```

### Campos:

| Campo | Tipo | Obrigatório | Descrição |
|-------|------|-------------|-----------|
| `telefone` | string | ✅ | Número do WhatsApp (com ou sem +55) |
| `mensagem_original` | string | ✅ | Mensagem original enviada pelo cliente |
| `intencao` | string | ✅ | `agendar`, `cancelar`, `consultar`, `confirmar` |
| `dados` | object | ✅ | Dados extraídos pela IA (varia por intenção) |

---

## 📤 Resposta

```json
{
  "sucesso": true,
  "mensagem": "✅ Agendamento confirmado!\n\n📅 Serviço: Corte de Cabelo\n👤 Profissional: João\n🕐 Data: 23/12/2025 às 14:00\n💰 Valor: R$ 50,00\n📝 Código: ABC123\n\nPara cancelar: CANCELAR ABC123",
  "dados": {
    "agendamento_id": 123,
    "codigo": "ABC123",
    "data_hora": "23/12/2025 às 14:00",
    "valor": 50.0
  }
}
```

### Campos da Resposta:

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `sucesso` | boolean | `true` se operação foi bem-sucedida |
| `mensagem` | string | Texto formatado para enviar ao cliente no WhatsApp |
| `dados` | object | Dados adicionais (opcional) |

---

## 🎭 Intenções Suportadas

### 1️⃣ **AGENDAR**

Cria novo agendamento.

**Dados necessários:**
```json
{
  "intencao": "agendar",
  "dados": {
    "servico": "corte de cabelo",
    "data": "2025-12-23",      // YYYY-MM-DD
    "hora": "14:00",            // HH:MM
    "profissional": "João"      // Opcional
  }
}
```

**Validações automáticas:**
- ✅ Cliente existe? (se não, cria automaticamente)
- ✅ Serviço existe?
- ✅ Profissional existe?
- ✅ Data/hora não está no passado?
- ✅ Horário está disponível?

**Retorno em caso de conflito:**
```json
{
  "sucesso": false,
  "mensagem": "Este horário já está ocupado! 😔\n\nHorários disponíveis para 23/12/2025:\n🕐 10:00  🕐 10:30  🕐 11:00\n🕐 15:00  🕐 15:30  🕐 16:00",
  "horarios_alternativos": ["10:00", "10:30", "11:00", "15:00", "15:30", "16:00"]
}
```

---

### 2️⃣ **CANCELAR**

Cancela agendamento por código.

**Dados necessários:**
```json
{
  "intencao": "cancelar",
  "dados": {
    "codigo": "ABC123"
  }
}
```

**Validações:**
- ✅ Código existe?
- ✅ Agendamento pertence ao telefone?
- ✅ Agendamento ainda não foi concluído?

---

### 3️⃣ **CONSULTAR**

Consulta horários disponíveis.

**Dados opcionais:**
```json
{
  "intencao": "consultar",
  "dados": {
    "data": "2025-12-23",         // Opcional (default: hoje)
    "profissional": "João"        // Opcional (default: todos)
  }
}
```

**Retorno:**
```json
{
  "sucesso": true,
  "mensagem": "📅 Horários disponíveis em 23/12/2025:\n\n🕐 10:00  🕐 10:30  🕐 11:00\n🕐 14:00  🕐 14:30  🕐 15:00\n🕐 16:00  🕐 16:30  🕐 17:00\n\nPara agendar, diga: 'Quero agendar [serviço] às [hora]'",
  "horarios": ["10:00", "10:30", "11:00", ...]
}
```

---

### 4️⃣ **CONFIRMAR**

Confirma agendamento pendente.

**Dados necessários:**
```json
{
  "intencao": "confirmar",
  "dados": {
    "codigo": "ABC123"
  }
}
```

---

## 🤖 Exemplo de Workflow n8n

### **Workflow Completo: WhatsApp → IA → Django → WhatsApp**

```json
{
  "name": "Bot WhatsApp - Gestto",
  "nodes": [
    {
      "name": "1. Webhook WhatsApp",
      "type": "n8n-nodes-base.webhook",
      "parameters": {
        "path": "whatsapp-incoming",
        "responseMode": "lastNode"
      }
    },
    {
      "name": "2. Extrair dados",
      "type": "n8n-nodes-base.set",
      "parameters": {
        "values": {
          "telefone": "={{ $json.from }}",
          "mensagem": "={{ $json.message }}"
        }
      }
    },
    {
      "name": "3. Processar com IA (OpenAI/Claude)",
      "type": "n8n-nodes-base.openAI",
      "parameters": {
        "model": "gpt-4",
        "messages": {
          "system": "Você é um assistente que extrai informações de agendamentos. Retorne SEMPRE um JSON válido com os campos: {\"intencao\": \"agendar|cancelar|consultar|confirmar\", \"dados\": {...}}",
          "user": "Mensagem do cliente: {{ $json.mensagem }}\n\nExtraia: serviço, data (YYYY-MM-DD), hora (HH:MM), profissional (se mencionado)"
        },
        "temperature": 0.3
      }
    },
    {
      "name": "4. Parse JSON da IA",
      "type": "n8n-nodes-base.code",
      "parameters": {
        "code": "const resposta = JSON.parse($input.first().json.response);\nreturn { json: resposta };"
      }
    },
    {
      "name": "5. Enviar para Django",
      "type": "n8n-nodes-base.httpRequest",
      "parameters": {
        "method": "POST",
        "url": "http://127.0.0.1:8000/api/bot/processar/",
        "authentication": "none",
        "headers": {
          "X-API-Key": "{{ $env.GESTTO_API_KEY }}",
          "X-Empresa-ID": "1",
          "Content-Type": "application/json"
        },
        "body": {
          "telefone": "={{ $node['2. Extrair dados'].json.telefone }}",
          "mensagem_original": "={{ $node['2. Extrair dados'].json.mensagem }}",
          "intencao": "={{ $json.intencao }}",
          "dados": "={{ $json.dados }}"
        }
      }
    },
    {
      "name": "6. Enviar resposta WhatsApp",
      "type": "n8n-nodes-base.whatsapp",
      "parameters": {
        "to": "={{ $node['2. Extrair dados'].json.telefone }}",
        "message": "={{ $json.mensagem }}"
      }
    }
  ]
}
```

---

## 🧪 Testando a API

### **Com cURL:**

```bash
curl -X POST http://127.0.0.1:8000/api/bot/processar/ \
  -H "X-API-Key: desenvolvimento-inseguro-mudar-em-producao" \
  -H "X-Empresa-ID: 1" \
  -H "Content-Type: application/json" \
  -d '{
    "telefone": "5511999998888",
    "mensagem_original": "Quero agendar corte amanhã 14h",
    "intencao": "agendar",
    "dados": {
      "servico": "corte",
      "data": "2025-12-22",
      "hora": "14:00"
    }
  }'
```

### **Com Postman/Insomnia:**

1. **Method:** POST
2. **URL:** `http://127.0.0.1:8000/api/bot/processar/`
3. **Headers:**
   - `X-API-Key`: `desenvolvimento-inseguro-mudar-em-producao`
   - `X-Empresa-ID`: `1`
   - `Content-Type`: `application/json`
4. **Body (JSON):** Ver exemplo acima

---

## 📊 Logs e Auditoria

Toda interação é registrada no modelo `LogMensagemBot`:

**Acessar logs:**
```python
# Django shell
python manage.py shell

from agendamentos.models import LogMensagemBot

# Ver últimos 10 logs
LogMensagemBot.objects.all()[:10]

# Ver logs de um telefone
LogMensagemBot.objects.filter(telefone='5511999998888')

# Ver logs com erro
LogMensagemBot.objects.filter(status='erro')
```

**Ou pelo Django Admin:**
- http://127.0.0.1:8000/admin/agendamentos/logmensagembot/

---

## ⚠️ Tratamento de Erros

### Erro de autenticação:
```json
{
  "detail": "API Key inválida"
}
```

### Erro de validação:
```json
{
  "sucesso": false,
  "mensagem": "Não encontrei o serviço 'massagem'. Serviços disponíveis: Corte de Cabelo, Barba, Sobrancelha",
  "erro": "..."
}
```

### Erro interno:
```json
{
  "sucesso": false,
  "mensagem": "Desculpe, ocorreu um erro ao processar sua solicitação.",
  "erro": "detalhes técnicos..."
}
```

---

## 🚀 Próximos Passos

1. **Configure n8n:**
   - Importe o workflow de exemplo
   - Configure credenciais (WhatsApp, OpenAI, etc)
   - Teste com mensagens reais

2. **Personalize prompts da IA:**
   - Ajuste o prompt do OpenAI/Claude para seu contexto
   - Adicione exemplos específicos do seu negócio

3. **Adicione mais intenções:**
   - Reagendamento
   - Feedback pós-atendimento
   - Pesquisa de satisfação

4. **Monitore logs:**
   - Verifique `LogMensagemBot` diariamente
   - Ajuste IA baseado em erros comuns

---

## 📞 Suporte

Em caso de dúvidas, verifique:
- Logs do Django: `python manage.py runserver`
- Logs do n8n: Console do navegador
- Banco de dados: `LogMensagemBot` table

