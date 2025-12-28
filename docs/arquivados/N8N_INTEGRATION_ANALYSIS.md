# Análise de Integração com n8n

## Resumo Executivo

A pasta `n8n-workflows/` contém **7 workflows** do n8n originalmente criados para a **Brandão Barbearia**. Estes workflows são **templates/exemplos** de como implementar automações de agendamento via WhatsApp usando n8n.

## Arquivos Encontrados

| Arquivo | Tamanho | Descrição |
|---------|---------|-----------|
| `1- Secretaria _ Brandão Barbearia.json` | 224KB | Workflow principal - recebe webhooks do WhatsApp |
| `2- Agente de Agendamento _ Brandão Barbearia.json` | 22KB | Agente IA para processar agendamentos |
| `3 - Agendamento Fixo.json` | 7.8KB | Roteamento para agendamentos de datas fixas |
| `4 - Brandão - FolowUp_CRM.json` | 15KB | Follow-up e CRM automatizado |
| `Pedro _ Brandão Barbearia.json` | 21KB | Workflow específico do profissional Pedro |
| `Fixo _ Pedro Brandão.json` | 28KB | Agendamentos fixos do Pedro |
| `Agendamento _ Pedro _ Brandão Barbearia.json` | 41KB | Sistema completo de agendamento do Pedro |

## Arquitetura Atual dos Workflows

### 1. Fluxo Principal (Workflow #1 - Secretaria)

```
Webhook Evolution API (MESSAGES_UPSERT)
    ↓
Normalização de dados
    ↓
Verificação de tipo de mensagem (texto/audio/imagem)
    ↓
Processamento de áudio (se aplicável)
    ↓
Roteamento para agentes especializados
    ↓
Resposta ao cliente via Evolution API
```

### 2. Integrações Utilizadas

#### Google Sheets
- **Planilha principal:** `1afoO870jEQTkBfsgQ_YvRaCHbcDKq9bniJNdMWc2NMs`
- **Abas utilizadas:**
  - `gid=0` - Dados principais
  - `gid=168094712` - Horários disponíveis
  - `gid=217584611` - Datas especiais

**Função:** Armazenar agendamentos, horários, serviços e disponibilidade dos profissionais.

#### Evolution API
- **URL Base:** `https://evolution.axiodev.cloud`
- **Instâncias:**
  - `BrandaoBarbearia`
  - `Axio_Test`
- **Endpoints usados:**
  - `/message/sendText/{instance}` - Enviar mensagens de texto
  - `/chat/getBase64FromMediaMessage/{instance}` - Obter mídia em base64

#### OpenAI (LangChain)
- **Modelo:** `gpt-4.1-mini`
- **Função:** Agentes inteligentes para:
  - Processar linguagem natural
  - Gerenciar agendamentos
  - Responder dúvidas
  - Validar disponibilidade

### 3. Fluxo de Dados

```json
{
  "webhook_entrada": {
    "instance": "BrandaoBarbearia",
    "data": {
      "key": {
        "fromMe": false,
        "id": "message_id"
      },
      "message": {
        "conversation": "texto da mensagem",
        "extendedTextMessage": {},
        "audioMessage": {},
        "imageMessage": {}
      },
      "messageTimestamp": 1234567890
    }
  }
}
```

## O Que Temos x O Que Precisamos

### ✅ O Que JÁ TEMOS no Sistema Django

1. **Evolution API integrada** ✓
   - Webhook configurado corretamente
   - Envio de mensagens implementado
   - Recebimento de eventos (MESSAGES_UPSERT, etc)

2. **Modelos de dados** ✓
   - Agendamento
   - Cliente
   - Profissional
   - Servico
   - Empresa

3. **API interna** ✓
   - Endpoints REST (se houver DRF configurado)
   - Lógica de negócio para agendamentos

### ❌ O Que PRECISAMOS para integrar com n8n

#### 1. Endpoints de API para n8n consumir

**Endpoints necessários:**

```
GET  /api/agendamentos/disponibilidade/
     ?profissional_id=1&data=2025-01-15&servico_id=2

POST /api/agendamentos/criar/
     {
       "cliente_nome": "Nome",
       "cliente_telefone": "5511999999999",
       "profissional_id": 1,
       "servico_id": 2,
       "data_hora": "2025-01-15T14:00:00"
     }

GET  /api/profissionais/
     Retorna lista de profissionais ativos

GET  /api/servicos/
     Retorna lista de serviços com duração e preço

POST /api/agendamentos/{id}/cancelar/
     Cancela um agendamento

PATCH /api/agendamentos/{id}/remarcar/
      {
        "nova_data_hora": "2025-01-16T15:00:00"
      }

GET  /api/agendamentos/buscar/
     ?cliente_telefone=5511999999999
     Busca agendamentos de um cliente
```

#### 2. Autenticação para n8n

**Opções:**
- API Key específica para n8n (recomendado)
- Token JWT
- Basic Auth

#### 3. Webhook handler para Evolution

**Já existe parcialmente, mas precisa:**
- Processar todos os tipos de mensagem (texto, áudio, imagem)
- Integrar com n8n via HTTP request
- Ou processar diretamente no Django

#### 4. Configurações de Empresa

**Necessário adicionar ao modelo `Empresa`:**
- `n8n_webhook_url` - URL do webhook do n8n para essa empresa
- `n8n_api_key` - API key do n8n (se aplicável)
- `openai_api_key` - Para agentes IA (opcional)

## Estratégias de Integração

### Opção 1: Django como Backend, n8n como Orquestrador (RECOMENDADO)

```
WhatsApp → Evolution API → Django Webhook
                                ↓
                          n8n (via HTTP Request)
                                ↓
                    Agente IA (OpenAI) no n8n
                                ↓
                    Django API (criar/consultar agendamentos)
                                ↓
                    n8n envia resposta → Evolution API → WhatsApp
```

**Vantagens:**
- n8n cuida da orquestração e lógica de IA
- Django cuida dos dados e regras de negócio
- Separação clara de responsabilidades
- Fácil manutenção dos workflows

**Desvantagens:**
- Mais uma ferramenta para gerenciar (n8n)
- Custo adicional se usar n8n cloud

### Opção 2: Django Full Stack (sem n8n)

```
WhatsApp → Evolution API → Django Webhook
                                ↓
                    Processamento no Django
                    (OpenAI API diretamente)
                                ↓
                    Lógica de agendamento
                                ↓
                    Evolution API → WhatsApp
```

**Vantagens:**
- Tudo em uma única stack
- Menos dependências externas
- Mais controle

**Desvantagens:**
- Precisa reimplementar toda lógica dos workflows
- Manutenção de código de IA no Django
- Menos flexível para mudanças rápidas

### Opção 3: Híbrido (MEIO TERMO)

```
WhatsApp → Evolution API → Django Webhook
                                ↓
                    IF (mensagem simples):
                        Processa no Django
                    ELSE:
                        Chama n8n para IA
                                ↓
                    Evolution API → WhatsApp
```

## Próximos Passos

### Fase 1: Preparar Django API ✅ (2-3 dias)

- [ ] Criar endpoints REST com DRF
- [ ] Implementar autenticação via API Key
- [ ] Adicionar serializers para Agendamento, Profissional, Servico
- [ ] Implementar lógica de disponibilidade
- [ ] Documentar API com Swagger/OpenAPI

### Fase 2: Configurar n8n (1 dia)

- [ ] Instalar n8n (local ou cloud)
- [ ] Importar workflows existentes
- [ ] Adaptar para usar API do Django em vez de Google Sheets
- [ ] Configurar credenciais (Evolution, OpenAI, Django API)
- [ ] Testar fluxo básico

### Fase 3: Integração Evolution + n8n (1-2 dias)

- [ ] Configurar webhook do Evolution apontar para n8n
- [ ] OU configurar Django webhook chamar n8n
- [ ] Testar recebimento de mensagens
- [ ] Testar envio de respostas

### Fase 4: Customização por Empresa (2-3 dias)

- [ ] Sistema de templates de workflow por empresa
- [ ] Configuração de horários por empresa/profissional
- [ ] Personalização de mensagens
- [ ] Multi-tenant no n8n

### Fase 5: Testes e Deploy (2-3 dias)

- [ ] Testes end-to-end
- [ ] Ajustes finos
- [ ] Documentação
- [ ] Deploy

## Estimativa Total

**Com n8n:** 8-12 dias
**Sem n8n (tudo no Django):** 15-20 dias

## Recomendação

✅ **Usar n8n** como orquestrador porque:

1. Os workflows já estão prontos e testados
2. Facilita iteração rápida em regras de negócio
3. OpenAI/LangChain já está integrado
4. Interface visual para ajustes
5. Multi-empresa mais fácil (um workflow por empresa)

## Arquivos a Criar

### Django

```
📁 api/
  ├── serializers.py
  ├── urls.py
  ├── views.py (AgendamentoViewSet, etc)
  └── permissions.py (N8nAPIKeyPermission)

📁 webhooks/
  ├── n8n_handler.py (envia para n8n)
  └── evolution_handler.py (já existe, melhorar)

📁 empresas/migrations/
  └── 000X_add_n8n_fields.py
```

### n8n (adaptar workflows)

```
- Substituir Google Sheets por HTTP Request para Django API
- Adicionar autenticação nos requests
- Parametrizar por empresa (empresa_id)
```

### Documentação

```
📁 docs/
  ├── N8N_SETUP.md (como instalar/configurar)
  ├── N8N_WORKFLOWS.md (documentação de cada workflow)
  └── API_ENDPOINTS.md (documentação dos endpoints)
```

## Questões em Aberto

1. **n8n Cloud ou Self-hosted?**
   - Cloud: Mais fácil, mas pago (~$20/mês)
   - Self-hosted: Gratuito, mas precisa gerenciar servidor

2. **Um n8n para todas as empresas ou um por empresa?**
   - Um centralizado com parametrização (recomendado)
   - Um por empresa (muito complexo)

3. **Google Sheets ou Django como fonte de verdade?**
   - Django (recomendado) - Sheets só como cache/visualização
   - Sheets - Django apenas valida

4. **Processar áudio no Django ou n8n?**
   - n8n tem nodes prontos para Whisper/OpenAI
   - Django precisa implementar do zero

5. **Multi-idioma?**
   - Workflows suportam PT-BR
   - Precisa adaptar para outros idiomas?
