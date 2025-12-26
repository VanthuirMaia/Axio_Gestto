# ✅ Sistema PRONTO para Integração com n8n

## Status Atual: **90% Completo**

Boa notícia! O sistema **JÁ TEM** quase tudo implementado para integrar com n8n!

## ✅ O Que JÁ TEMOS (Implementado)

### 1. APIs REST Completas

**Arquivo:** `agendamentos/api_n8n.py` (468 linhas)

✅ **Endpoints implementados:**

| Endpoint | Método | Descrição | Status |
|----------|--------|-----------|--------|
| `/api/n8n/servicos/` | GET | Lista serviços ativos | ✅ |
| `/api/n8n/profissionais/` | GET | Lista profissionais ativos | ✅ |
| `/api/n8n/horarios-funcionamento/` | GET | Horários por dia da semana | ✅ |
| `/api/n8n/datas-especiais/` | GET | Feriados e datas especiais | ✅ |
| `/api/n8n/horarios-disponiveis/` | POST | Consulta disponibilidade | ✅ |

**Exemplos de uso:**

```bash
# Listar serviços
GET /api/n8n/servicos/
Headers:
  apikey: sua-chave-secreta
  empresa_id: 1

Response:
{
  "sucesso": true,
  "total": 5,
  "servicos": [
    {
      "id": 1,
      "nome": "Corte de Cabelo",
      "descricao": "Corte masculino tradicional",
      "preco": "40.00",
      "duracao_minutos": 30
    }
  ]
}

# Consultar horários disponíveis
POST /api/n8n/horarios-disponiveis/
Headers:
  apikey: sua-chave-secreta
  empresa_id: 1
Body:
{
  "data": "2025-12-23",
  "profissional_id": 1,
  "servico_id": 2
}

Response:
{
  "sucesso": true,
  "data": "2025-12-23",
  "dia_semana": "Segunda-feira",
  "profissional": "Pedro Brandão",
  "servico": "Corte + Barba",
  "duracao_minutos": 45,
  "total_horarios": 12,
  "horarios_disponiveis": ["09:00", "09:30", "10:00", ...]
}
```

### 2. Bot API Completa

**Arquivo:** `agendamentos/bot_api.py` (676 linhas)

✅ **Funcionalidades implementadas:**

- `processar_comando_bot()` - Endpoint central que recebe comandos do n8n
- `processar_agendamento()` - Criar agendamentos via bot
- `processar_cancelamento()` - Cancelar por código
- `processar_consulta()` - Consultar horários disponíveis
- `processar_confirmacao()` - Confirmar agendamento pendente

**Fluxo completo:**

```
n8n (OpenAI) → Django API → Resposta → n8n → WhatsApp
```

**Exemplo de uso:**

```bash
POST /api/bot/comando/
Headers:
  apikey: sua-chave-secreta
  empresa_id: 1
Body:
{
  "telefone": "5511999998888",
  "mensagem_original": "Quero agendar corte amanhã 14h",
  "intencao": "agendar",
  "dados": {
    "servico": "corte de cabelo",
    "data": "2025-12-23",
    "hora": "14:00",
    "profissional": "Pedro"
  }
}

Response:
{
  "sucesso": true,
  "mensagem": "✅ Agendamento confirmado!\n\n📅 Serviço: Corte de Cabelo\n👤 Profissional: Pedro Brandão\n🕐 Data: 23/12/2025 às 14:00\n💰 Valor: R$ 40,00\n📝 Código: A3B9C7\n\nPara cancelar: CANCELAR A3B9C7",
  "dados": {
    "agendamento_id": 123,
    "codigo": "A3B9C7",
    "data_hora": "23/12/2025 às 14:00",
    "valor": 40.0
  }
}
```

### 3. Webhook Multi-Tenant (SaaS)

✅ **Webhook público implementado:**

- `whatsapp_webhook_saas()` - Recebe webhooks do WhatsApp
- Detecta empresa por `instance_id`
- Valida assinatura e limites do plano
- Bloqueia automaticamente se expirou
- Integra com sistema de billing

**URL:** `/api/webhooks/whatsapp/saas/`

### 4. Autenticação

**Arquivo:** `agendamentos/authentication.py`

✅ **APIKeyAuthentication implementada:**
- Aceita `X-API-Key` ou `apikey` no header
- Aceita `X-Empresa-ID` ou `empresa_id` no header
- Injeta `request.empresa` nas views
- Validação contra `settings.N8N_API_KEY`

### 5. Rate Limiting

**Arquivo:** `agendamentos/throttling.py`

✅ Proteção contra abuso de API

### 6. Logging de Mensagens

✅ **Model `LogMensagemBot`** implementado:
- Registra toda interação do bot
- Rastreia intenções detectadas
- Armazena erros para debug
- Vincula com agendamentos criados

## ⚠️ O Que FALTA (10%)

### 1. URLs não registradas

❌ As APIs existem mas não estão nas URLs!

**Precisa adicionar em algum `urls.py`:**

```python
# agendamentos/urls.py ou criar se não existir

from django.urls import path
from . import api_n8n, bot_api

urlpatterns = [
    # APIs para n8n
    path('api/n8n/servicos/', api_n8n.listar_servicos),
    path('api/n8n/profissionais/', api_n8n.listar_profissionais),
    path('api/n8n/horarios-funcionamento/', api_n8n.consultar_horarios_funcionamento),
    path('api/n8n/datas-especiais/', api_n8n.consultar_datas_especiais),
    path('api/n8n/horarios-disponiveis/', api_n8n.consultar_horarios_disponiveis),

    # Bot API
    path('api/bot/comando/', bot_api.processar_comando_bot),

    # Webhook multi-tenant
    path('api/webhooks/whatsapp/saas/', bot_api.whatsapp_webhook_saas),
]
```

### 2. Settings

❌ **Falta configurar em `config/settings.py`:**

```python
# API Key para n8n
N8N_API_KEY = config('N8N_API_KEY', default='change-me-in-production')

# URL do n8n (para chamar de volta, se necessário)
N8N_WEBHOOK_URL = config('N8N_WEBHOOK_URL', default='')
```

### 3. .env

❌ **Adicionar ao `.env`:**

```bash
# n8n Integration
N8N_API_KEY=seu-token-super-secreto-aqui
N8N_WEBHOOK_URL=https://seu-n8n.com/webhook/xxx
```

### 4. Models Adicionais (Opcional)

⚠️ **Verificar se existem:**

```python
# agendamentos/models.py

class LogMensagemBot(models.Model):
    """Log de interações do bot"""
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE)
    telefone = models.CharField(max_length=20)
    mensagem_original = models.TextField()
    intencao_detectada = models.CharField(max_length=50)
    dados_extraidos = models.JSONField()
    status = models.CharField(max_length=20)  # sucesso, erro, parcial
    resposta_enviada = models.TextField(blank=True)
    erro_detalhes = models.TextField(blank=True)
    agendamento = models.ForeignKey(Agendamento, null=True, blank=True, on_delete=models.SET_NULL)
    criado_em = models.DateTimeField(auto_now_add=True)
```

## 📋 Checklist de Integração

### Fase 1: Configurar Django (30 min)

- [ ] Adicionar URLs em `agendamentos/urls.py`
- [ ] Incluir em `config/urls.py`: `path('', include('agendamentos.urls'))`
- [ ] Adicionar `N8N_API_KEY` em `settings.py`
- [ ] Adicionar `N8N_API_KEY` no `.env`
- [ ] Verificar se model `LogMensagemBot` existe (criar migration se necessário)
- [ ] Testar endpoints com Postman/curl

### Fase 2: Configurar n8n (2h)

- [ ] Instalar n8n (cloud ou self-hosted)
- [ ] Importar workflows da pasta `n8n-workflows/`
- [ ] Substituir Google Sheets por HTTP Requests para Django API
- [ ] Configurar credenciais:
  - [ ] Evolution API (já configurado)
  - [ ] OpenAI API Key
  - [ ] Django API (URL + API Key)
- [ ] Testar workflow básico

### Fase 3: Adaptar Workflows (3-4h)

#### Workflow 1: Secretaria (Principal)

**Substituir:**
```
❌ Google Sheets "serviços"
→ ✅ HTTP Request GET /api/n8n/servicos/

❌ Google Sheets "profissionais"
→ ✅ HTTP Request GET /api/n8n/profissionais/

❌ Google Sheets "horários"
→ ✅ HTTP Request GET /api/n8n/horarios-funcionamento/

❌ Google Sheets "agenda"
→ ✅ HTTP Request POST /api/n8n/horarios-disponiveis/
```

#### Workflow 2: Agente de Agendamento

**Adicionar:**
```
Agente OpenAI processa →
HTTP Request POST /api/bot/comando/ →
Retorna resposta →
Evolution API envia resposta
```

### Fase 4: Testar End-to-End (1h)

- [ ] Enviar mensagem no WhatsApp
- [ ] Verificar se Evolution webhook chama n8n
- [ ] Verificar se n8n chama Django API
- [ ] Verificar se agendamento é criado
- [ ] Verificar se resposta volta ao WhatsApp
- [ ] Testar cancelamento
- [ ] Testar consulta de horários

### Fase 5: Multi-Tenant (2h)

- [ ] Criar múltiplas empresas no Django
- [ ] Configurar instâncias separadas na Evolution
- [ ] Testar roteamento por `instance_id`
- [ ] Validar isolamento de dados

## 🎯 Como Usar os Workflows Existentes

### Template Brandão Barbearia

Os workflows em `n8n-workflows/` são da Brandão Barbearia e usam:

❌ **Atualmente:**
- Google Sheets como banco de dados
- Instance fixa: `BrandaoBarbearia`
- Profissionais fixos: Pedro e Juan

✅ **Adaptar para:**
- Django API como banco de dados
- Parametrização por `empresa_id`
- Profissionais dinâmicos da empresa

### Estrutura dos Workflows

1. **Secretaria** - Recebe webhook, processa mensagem
2. **Agente de Agendamento** - IA que entende intenções
3. **Agendamento Fixo** - Roteia para profissional específico
4. **Follow-up/CRM** - Mensagens automáticas

### Substituições Necessárias

| Componente Atual | Substituir Por |
|------------------|----------------|
| Google Sheets node | HTTP Request node |
| `spreadsheetId: 1afoO...` | `url: /api/n8n/servicos/` |
| Hard-coded `BrandaoBarbearia` | `{{ $json.instance }}` dinâmico |
| Sheet "horarios" | `GET /api/n8n/horarios-funcionamento/` |
| Sheet "datas_especiais" | `GET /api/n8n/datas-especiais/` |

## 🚀 Próximos Passos Recomendados

### Opção A: MVP Rápido (1 dia)

1. Configurar URLs e settings (30 min)
2. Instalar n8n cloud (30 min)
3. Importar e adaptar workflow "Agente de Agendamento" apenas (2h)
4. Testar com 1 empresa (1h)
5. Ajustes e fixes (2h)

### Opção B: Completo (1 semana)

1. Configurar Django (1h)
2. Instalar n8n self-hosted (3h)
3. Adaptar todos os workflows (2 dias)
4. Implementar multi-tenant (1 dia)
5. Testes extensivos (1 dia)
6. Documentação e deploy (1 dia)

## 📝 Resumo

**Status:** ✅ **Sistema 90% pronto!**

**O que falta:**
- ⚠️ Registrar URLs (10 linhas de código)
- ⚠️ Configurar settings (2 linhas)
- ⚠️ Adaptar workflows n8n (substituir Google Sheets por HTTP)

**Tempo estimado para finalizar:**
- **MVP:** 4-6 horas
- **Completo:** 3-5 dias

**Recomendação:**
Use os workflows existentes como base, eles estão **muito bem feitos** e já testados em produção na Brandão Barbearia. Só precisa trocar a fonte de dados de Google Sheets para sua API Django.

## 🎁 Bônus: O Código Já Existente é Excelente!

Quem desenvolveu as APIs em `bot_api.py` e `api_n8n.py` fez um **trabalho excepcional**:

✅ Autenticação implementada
✅ Rate limiting
✅ Logging completo
✅ Tratamento de erros
✅ Multi-tenant pronto
✅ Validação de assinatura/limites
✅ Mensagens formatadas
✅ Geração de códigos
✅ Busca de clientes automática
✅ Verificação de conflitos

**Conclusão:** Você tem uma **API de produção** pronta para usar!
