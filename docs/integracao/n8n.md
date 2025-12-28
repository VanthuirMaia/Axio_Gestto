# Integração n8n com Axio Gestto - Guia Completo

## Visão Geral

O n8n se comunica com o Django via APIs REST para automatizar agendamentos via WhatsApp. A integração funciona em dois fluxos:

1. **n8n → Django**: Envia comandos processados (agendar, cancelar, consultar)
2. **Django → n8n**: Fornece dados (serviços, profissionais, horários disponíveis)

---

## Arquitetura da Integração

```
┌─────────────────────────────────────────────────────────────┐
│                         FLUXO COMPLETO                       │
└─────────────────────────────────────────────────────────────┘

Cliente WhatsApp
     │
     │ "Quero agendar corte amanhã às 14h"
     │
     ▼
┌─────────────────────┐
│  WhatsApp Business  │
│  API / Evolution    │
└──────────┬──────────┘
           │
           │ Webhook
           │
           ▼
┌─────────────────────────────────────────────────────────────┐
│                      n8n Workflow                            │
│                                                               │
│  1. Webhook Trigger (recebe mensagem)                        │
│  2. Extrai contexto (nome cliente, telefone)                 │
│  3. Consulta dados da empresa (GET APIs)                     │
│       └─► GET /api/n8n/servicos/                             │
│       └─► GET /api/n8n/profissionais/                        │
│  4. Envia mensagem + contexto para Claude AI                 │
│  5. IA retorna intent + dados estruturados                   │
│       {                                                      │
│         "intencao": "agendar",                               │
│         "servico": "corte",                                  │
│         "data": "2025-12-26",                                │
│         "hora": "14:00"                                      │
│       }                                                      │
│  6. Valida horários disponíveis                              │
│       └─► POST /api/n8n/horarios-disponiveis/               │
│  7. Envia comando para Django                                │
│       └─► POST /api/bot/processar/                           │
│  8. Recebe confirmação do Django                             │
│  9. Envia resposta ao cliente via WhatsApp                   │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
                ┌──────────────────────┐
                │   Django (Gestto)    │
                │                      │
                │  • Valida dados      │
                │  • Verifica conflitos│
                │  • Cria agendamento  │
                │  • Retorna código    │
                └──────────────────────┘
```

---

## Configuração do n8n

### Opção 1: n8n Cloud (n8n.io)

1. Criar conta em https://n8n.io
2. Criar novo workflow
3. Importar workflows da pasta `/n8n-workflows/`
4. Configurar credenciais e variáveis

**Vantagens:**
- Sem gerenciamento de servidor
- Backups automáticos
- SSL incluído

### Opção 2: n8n Self-Hosted (Docker)

```bash
# No servidor (mesma VPS do Gestto)
mkdir -p /home/n8n_data

docker run -d \
  --name n8n \
  --restart unless-stopped \
  -p 5678:5678 \
  -e N8N_HOST=seu-dominio-n8n.com \
  -e N8N_PORT=5678 \
  -e N8N_PROTOCOL=https \
  -e N8N_BASIC_AUTH_ACTIVE=true \
  -e N8N_BASIC_AUTH_USER=admin \
  -e N8N_BASIC_AUTH_PASSWORD=SUA_SENHA_FORTE \
  -e WEBHOOK_URL=https://seu-dominio-n8n.com \
  -v /home/n8n_data:/home/node/.n8n \
  n8nio/n8n

# Acessar em: https://seu-dominio-n8n.com:5678
```

**Vantagens:**
- Controle total
- Sem limitações de execuções
- Dados locais

---

## APIs Disponíveis

### 1. POST /api/bot/processar/ (Endpoint Principal)

**Autenticação:** API Key via Header

**Request:**
```bash
POST https://seu-dominio.com/api/bot/processar/
Content-Type: application/json
X-API-Key: SEU_TOKEN_N8N_API_KEY
X-Empresa-ID: 1

{
  "telefone": "5587999887766",
  "mensagem_original": "Quero agendar corte amanhã às 14h com João",
  "intencao": "agendar",
  "dados": {
    "servico": "corte",
    "profissional": "João",
    "data": "2025-12-26",
    "hora": "14:00"
  }
}
```

**Response (Sucesso):**
```json
{
  "sucesso": true,
  "mensagem": "✅ Agendamento confirmado!\n\nProfissional: João Silva\nServiço: Corte Masculino\nData: 26/12/2025 às 14:00\nValor: R$ 45,00\n\nCódigo de confirmação: ABC123\n\nPara cancelar, envie: CANCELAR ABC123",
  "dados": {
    "agendamento_id": 42,
    "codigo": "ABC123",
    "cliente": "Pedro Santos",
    "servico": "Corte Masculino",
    "profissional": "João Silva",
    "data_hora": "2025-12-26T14:00:00-03:00",
    "valor": "45.00"
  }
}
```

**Response (Erro):**
```json
{
  "sucesso": false,
  "mensagem": "❌ Horário indisponível. Tente outro horário.",
  "erro": "Profissional já possui agendamento neste horário"
}
```

**Intenções Suportadas:**
- `agendar` - Criar novo agendamento
- `cancelar` - Cancelar agendamento existente
- `consultar` - Buscar agendamentos do cliente
- `confirmar` - Confirmar agendamento pendente
- `reagendar` - Alterar data/hora de agendamento

---

### 2. GET /api/n8n/servicos/ (Listar Serviços)

**Request:**
```bash
GET https://seu-dominio.com/api/n8n/servicos/
X-API-Key: SEU_TOKEN_N8N_API_KEY
```

**Response:**
```json
{
  "servicos": [
    {
      "id": 1,
      "nome": "Corte Masculino",
      "descricao": "Corte tradicional",
      "preco": "45.00",
      "duracao_minutos": 30,
      "ativo": true
    },
    {
      "id": 2,
      "nome": "Barba",
      "descricao": "Aparar e modelar barba",
      "preco": "30.00",
      "duracao_minutos": 20,
      "ativo": true
    }
  ]
}
```

**Uso no n8n:**
- Para IA entender quais serviços estão disponíveis
- Para validar se serviço mencionado pelo cliente existe

---

### 3. GET /api/n8n/profissionais/ (Listar Profissionais)

**Request:**
```bash
GET https://seu-dominio.com/api/n8n/profissionais/
X-API-Key: SEU_TOKEN_N8N_API_KEY
```

**Response:**
```json
{
  "profissionais": [
    {
      "id": 1,
      "nome": "João Silva",
      "especialidades": ["Corte Masculino", "Barba"],
      "cor_hex": "#FF5733",
      "ativo": true
    },
    {
      "id": 2,
      "nome": "Maria Santos",
      "especialidades": ["Corte Feminino", "Coloração"],
      "cor_hex": "#3498DB",
      "ativo": true
    }
  ]
}
```

**Uso no n8n:**
- Para IA sugerir profissional baseado no serviço
- Para validar se profissional mencionado existe

---

### 4. GET /api/n8n/horarios-funcionamento/ (Horários da Empresa)

**Request:**
```bash
GET https://seu-dominio.com/api/n8n/horarios-funcionamento/?dia_semana=1
X-API-Key: SEU_TOKEN_N8N_API_KEY
```

**Parâmetros:**
- `dia_semana` (opcional): 0=Domingo, 1=Segunda, ..., 6=Sábado

**Response:**
```json
{
  "horarios": [
    {
      "dia_semana": 1,
      "dia_semana_nome": "Segunda",
      "hora_abertura": "09:00",
      "hora_fechamento": "19:00",
      "fechado": false
    }
  ]
}
```

**Uso no n8n:**
- Para IA validar se horário solicitado está dentro do expediente
- Para sugerir horários alternativos

---

### 5. GET /api/n8n/datas-especiais/ (Feriados/Horários Especiais)

**Request:**
```bash
GET https://seu-dominio.com/api/n8n/datas-especiais/?data_inicio=2025-12-01&tipo=feriado
X-API-Key: SEU_TOKEN_N8N_API_KEY
```

**Parâmetros:**
- `data_inicio` (opcional): YYYY-MM-DD
- `data_fim` (opcional): YYYY-MM-DD
- `tipo` (opcional): feriado, fechado, horario_especial

**Response:**
```json
{
  "datas_especiais": [
    {
      "data": "2025-12-25",
      "descricao": "Natal",
      "tipo": "feriado",
      "fechado_dia_todo": true
    },
    {
      "data": "2025-12-31",
      "descricao": "Véspera de Ano Novo",
      "tipo": "horario_especial",
      "fechado_dia_todo": false,
      "hora_abertura": "09:00",
      "hora_fechamento": "13:00"
    }
  ]
}
```

**Uso no n8n:**
- Para IA avisar cliente que dia está fechado
- Para sugerir próximo dia útil

---

### 6. POST /api/n8n/horarios-disponiveis/ (Consultar Disponibilidade)

**Request:**
```bash
POST https://seu-dominio.com/api/n8n/horarios-disponiveis/
Content-Type: application/json
X-API-Key: SEU_TOKEN_N8N_API_KEY

{
  "data": "2025-12-26",
  "profissional_id": 1,
  "servico_id": 1
}
```

**Response:**
```json
{
  "data": "2025-12-26",
  "profissional": "João Silva",
  "servico": "Corte Masculino",
  "horarios_disponiveis": [
    "09:00",
    "09:30",
    "10:00",
    "14:00",
    "14:30",
    "15:00",
    "18:00"
  ],
  "horarios_ocupados": [
    "11:00",
    "16:00"
  ]
}
```

**Uso no n8n:**
- Antes de tentar agendar, verificar se horário está livre
- Sugerir horários alternativos se horário solicitado estiver ocupado

---

## Exemplo de Workflow n8n (Passo a Passo)

### Workflow: "Agendamento via WhatsApp"

```
1. [Webhook Trigger]
   ├─ Method: POST
   ├─ Path: /webhook/whatsapp
   └─ Auth: None (WhatsApp envia webhook)

2. [Extract Data]
   ├─ Telefone: {{ $json.from }}
   ├─ Mensagem: {{ $json.body }}
   └─ Nome Cliente: {{ $json.notifyName }}

3. [HTTP Request - Buscar Serviços]
   ├─ Method: GET
   ├─ URL: https://seu-dominio.com/api/n8n/servicos/
   ├─ Headers:
   │   └─ X-API-Key: {{ $env.N8N_API_KEY }}
   └─ Output: servicos_disponiveis

4. [HTTP Request - Buscar Profissionais]
   ├─ Method: GET
   ├─ URL: https://seu-dominio.com/api/n8n/profissionais/
   ├─ Headers:
   │   └─ X-API-Key: {{ $env.N8N_API_KEY }}
   └─ Output: profissionais_disponiveis

5. [OpenAI / Claude AI]
   ├─ Prompt: |
   │   Você é assistente de agendamento.
   │
   │   Serviços disponíveis: {{ $node["HTTP Request - Buscar Serviços"].json.servicos }}
   │   Profissionais: {{ $node["HTTP Request - Buscar Profissionais"].json.profissionais }}
   │
   │   Mensagem do cliente: "{{ $node["Extract Data"].json.mensagem }}"
   │
   │   Extraia:
   │   - intencao: agendar/cancelar/consultar
   │   - servico: nome do serviço
   │   - profissional: nome (opcional)
   │   - data: YYYY-MM-DD
   │   - hora: HH:MM
   │
   │   Retorne JSON válido.
   │
   └─ Output Format: JSON

6. [Switch - Detectar Intenção]
   ├─ Case "agendar" → próximo nó
   ├─ Case "cancelar" → fluxo cancelamento
   ├─ Case "consultar" → fluxo consulta
   └─ Default → "Não entendi, pode repetir?"

7. [HTTP Request - Verificar Disponibilidade]
   ├─ Method: POST
   ├─ URL: https://seu-dominio.com/api/n8n/horarios-disponiveis/
   ├─ Headers:
   │   └─ X-API-Key: {{ $env.N8N_API_KEY }}
   ├─ Body:
   │   {
   │     "data": "{{ $node["OpenAI"].json.data }}",
   │     "profissional_id": {{ $node["OpenAI"].json.profissional_id }},
   │     "servico_id": {{ $node["OpenAI"].json.servico_id }}
   │   }
   └─ Output: horarios_disponiveis

8. [IF - Horário Disponível?]
   ├─ Condição: {{ $node["OpenAI"].json.hora }} IN {{ $node["Verificar Disponibilidade"].json.horarios_disponiveis }}
   │
   ├─ TRUE → Próximo nó (criar agendamento)
   │
   └─ FALSE → Responder:
       "Horário indisponível. Disponíveis: {{ $node["Verificar Disponibilidade"].json.horarios_disponiveis }}"

9. [HTTP Request - Criar Agendamento]
   ├─ Method: POST
   ├─ URL: https://seu-dominio.com/api/bot/processar/
   ├─ Headers:
   │   ├─ X-API-Key: {{ $env.N8N_API_KEY }}
   │   └─ Content-Type: application/json
   ├─ Body:
   │   {
   │     "telefone": "{{ $node["Extract Data"].json.telefone }}",
   │     "mensagem_original": "{{ $node["Extract Data"].json.mensagem }}",
   │     "intencao": "agendar",
   │     "dados": {
   │       "servico": "{{ $node["OpenAI"].json.servico }}",
   │       "profissional": "{{ $node["OpenAI"].json.profissional }}",
   │       "data": "{{ $node["OpenAI"].json.data }}",
   │       "hora": "{{ $node["OpenAI"].json.hora }}"
   │     }
   │   }
   └─ Output: resultado_agendamento

10. [IF - Agendamento Sucesso?]
    ├─ Condição: {{ $node["Criar Agendamento"].json.sucesso }} == true
    │
    ├─ TRUE → Responder WhatsApp:
    │   "{{ $node["Criar Agendamento"].json.mensagem }}"
    │
    └─ FALSE → Responder WhatsApp:
        "{{ $node["Criar Agendamento"].json.mensagem }}"

11. [WhatsApp - Enviar Resposta]
    ├─ Method: POST
    ├─ URL: API do WhatsApp Business/Evolution
    └─ Body:
        {
          "to": "{{ $node["Extract Data"].json.telefone }}",
          "message": "{{ $node["IF"].json.resposta }}"
        }
```

---

## Configuração de Credenciais no n8n

### 1. Criar Credential "Gestto API"

1. No n8n, ir em **Credentials** → **New**
2. Tipo: **Header Auth**
3. Configurar:
   - **Name**: Gestto API
   - **Header Name**: X-API-Key
   - **Header Value**: [copiar N8N_API_KEY do .env do servidor]

### 2. Usar em HTTP Request Nodes

Em todos os nós **HTTP Request** que chamam APIs do Gestto:
- **Authentication**: Header Auth
- **Credential for Header Auth**: Gestto API

---

## Variáveis de Ambiente no n8n

Se usar n8n self-hosted, configurar:

```bash
# .env do n8n
N8N_API_KEY=mesmo_valor_do_env_django
GESTTO_API_URL=https://seu-dominio.com
EMPRESA_ID=1
```

No workflow, usar:
```javascript
{{ $env.GESTTO_API_URL }}/api/bot/processar/
{{ $env.N8N_API_KEY }}
```

---

## Importar Workflows Existentes

Os workflows prontos estão em `/n8n-workflows/`:

1. No n8n, ir em **Workflows** → **Import from File**
2. Selecionar arquivo `.json`
3. Após importar, editar:
   - URLs (trocar `localhost` por `seu-dominio.com`)
   - Credenciais (selecionar "Gestto API")
   - Webhooks (atualizar URLs)

**Arquivos disponíveis:**
- `1- Secretaria _ Brandão Barbearia.json` - Workflow principal
- `2- Agente de Agendamento _ Brandão Barbearia.json` - Agente com IA
- `3 - Agendamento Fixo.json` - Agendamentos recorrentes
- `4 - Brandão - FolowUp_CRM.json` - Follow-up pós-atendimento

---

## Exemplos de Mensagens de Teste

### Agendar
```
Cliente: "Quero agendar corte amanhã às 14h"
Cliente: "Pode marcar barba para dia 26/12 às 10h com João?"
Cliente: "Preciso fazer corte e barba na terça que vem"
```

### Cancelar
```
Cliente: "Cancelar agendamento ABC123"
Cliente: "Quero cancelar meu horário de amanhã"
```

### Consultar
```
Cliente: "Quais meus agendamentos?"
Cliente: "Tenho algum horário marcado?"
```

### Confirmar
```
Cliente: "Confirmar agendamento ABC123"
Cliente: "Confirmo o horário de amanhã"
```

---

## Rate Limiting e Throttling

O Django implementa rate limiting para proteger as APIs:

| Endpoint | Limite | Por |
|----------|--------|-----|
| `/api/bot/processar/` | 500 requisições | hora |
| `/api/n8n/*` (GETs) | 1000 requisições | hora |
| Usuário anônimo | 100 requisições | hora |

Se exceder, retorna:
```json
{
  "detail": "Request was throttled. Expected available in 3600 seconds."
}
```

**Solução:** Implementar retry no n8n com delay exponencial.

---

## Logs e Auditoria

Todas as interações são registradas em `LogMensagemBot`:

**Ver logs via Django Admin:**
```
https://seu-dominio.com/admin/agendamentos/logmensagembot/
```

**Campos registrados:**
- Telefone do cliente
- Mensagem original
- Intenção detectada (agendar/cancelar/etc)
- Dados extraídos (JSON)
- Status (sucesso/erro/parcial)
- Timestamp

**Via API (futuro):**
```bash
GET /api/n8n/logs/?telefone=5587999887766&data_inicio=2025-12-01
```

---

## Troubleshooting

### Erro: "Unauthorized" (401)
**Causa:** API Key incorreta ou ausente

**Solução:**
```bash
# Verificar .env no servidor
cat .env | grep N8N_API_KEY

# Comparar com credential no n8n
# Devem ser EXATAMENTE iguais
```

### Erro: "Too Many Requests" (429)
**Causa:** Rate limit excedido

**Solução:** Adicionar delay entre requisições no n8n ou aumentar limite em `/agendamentos/throttling.py`

### Erro: "Bad Request" (400)
**Causa:** Dados inválidos no JSON

**Solução:** Verificar formato dos dados:
```json
{
  "intencao": "agendar",  // string
  "dados": {
    "data": "2025-12-26",  // YYYY-MM-DD
    "hora": "14:00",       // HH:MM
    "servico": "corte"     // string (nome ou ID)
  }
}
```

### Workflow não executa
**Causa:** Webhook URL incorreta

**Solução:**
1. No n8n, copiar Webhook URL
2. Configurar no WhatsApp Business API
3. Testar com `curl`:
```bash
curl -X POST https://seu-n8n.com/webhook/whatsapp \
  -H "Content-Type: application/json" \
  -d '{"from":"5587999887766","body":"teste"}'
```

---

## Próximos Passos

1. Importar workflows do `/n8n-workflows/`
2. Configurar credenciais "Gestto API"
3. Atualizar URLs em todos os HTTP Request nodes
4. Conectar com WhatsApp Business API / Evolution API
5. Testar fluxo completo end-to-end
6. Monitorar logs em tempo real

---

## Recursos Adicionais

- **Docs n8n**: https://docs.n8n.io/
- **WhatsApp Business API**: https://developers.facebook.com/docs/whatsapp
- **Evolution API** (alternativa): https://github.com/EvolutionAPI/evolution-api
- **Django REST Framework**: https://www.django-rest-framework.org/

---

**Desenvolvido por:** Axio Gestto Team
**Última atualização:** 2025-12-25
