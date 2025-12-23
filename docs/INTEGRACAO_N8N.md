# Integração n8n → Django

## Análise da Estrutura Atual

### Workflows Analisados

#### 1. **Workflow Principal - Secretaria** (229KB)
**Função:** Gateway de entrada e processamento de mensagens

**Fluxo:**
1. Recebe mensagem do WhatsApp (Evolution API)
2. **Buffer de mensagens** - agrupa mensagens rápidas
3. **Transcrição de áudio** - OpenAI Whisper
4. **Descrição de imagens** - Gemini Flash 2.5
5. **Quebra de mensagens longas** - Agente OpenAI formata mensagens
6. **Interpretação** - Agente IA identifica intenção
7. **Roteamento** - Envia para workflow apropriado
8. **Resposta** - Envia texto formatado ao usuário

**Tecnologias:**
- Evolution API (WhatsApp)
- OpenAI GPT-4.1-mini (agente principal)
- OpenAI Whisper (transcrição)
- Google Gemini Flash 2.5 (visão)
- PostgreSQL (memória de conversa)

---

#### 2. **Workflow Agente de Agendamento** (21KB)
**Função:** Lógica de agendamento com IA

**Fluxo:**
1. Recebe: `duvida`, `identificadorLead`, `servico`, `profissional`
2. Consulta **Google Sheets** (3 abas):
   - `serviTool` → Serviços e duração
   - `horarios` → Horários de funcionamento semanal
   - `datas_especiais` → Feriados e horários especiais
3. Chama **sub-workflow do profissional**:
   - `pedroTool` → Agenda Pedro Brandão
   - `juanTool` → Agenda Juan Alves
4. Retorna resposta formatada

**Dados no Google Sheets:**
```
Planilha: "Serviços Barbearia"
├── Aba 1: Serviços (nome, duração, preço)
├── Aba 2: horarios (dias da semana, horários)
└── Aba 3: datas_especiais (feriados, horários alternativos)
```

---

#### 3. **Workflow Agendamento Fixo** (7KB) ⚠️ DEPRECAR
**Função:** Criar agendamentos recorrentes

**Status:** **SERÁ REMOVIDO** - Django já implementa recorrência via Celery

---

#### 4. **Workflow Follow-up / CRM** (14KB)
**Função:** Notificações automáticas

**Fluxo:**
1. **Trigger:** Schedule a cada 30 minutos
2. **Consulta Supabase:** `crm_geral` (status=confirmado)
3. **Calcula diferença** de tempo para o atendimento
4. **Envia notificação:**
   - **1 dia antes** (diff_dias entre 0.9 e 1.0)
   - **1 hora antes** (diff_horas entre 0.8 e 1.0)
5. **Atualiza flags:** `notificado_1dia`, `notificado_1hora`

**Banco de Dados Atual:** Supabase
```sql
Tabela: crm_geral
Campos:
- id
- nome
- telefone
- servico
- data (datetime)
- status (pendente/confirmado/cancelado)
- notificado_1dia (boolean)
- notificado_1hora (boolean)
```

---

#### 5-7. **Workflows por Profissional** (Pedro, Juan)
**Função:** Gerenciar agenda individual

**Sub-workflows:**
- `Pedro | Brandão Barbearia` - Lógica principal
- `Agendamento | Pedro` - CRUD de agendamentos
- `Fixo | Pedro Brandão` - Agendamentos recorrentes (deprecar)

**Integrações:**
- Google Calendar (API)
- Supabase (persistência)

---

## Pontos de Integração n8n ↔ Django

### 🔄 Fluxo Proposto

```
WhatsApp (Evolution API)
    ↓
[n8n] Workflow 1 - Secretaria
    ├── Transcrição áudio (OpenAI)
    ├── Descrição imagem (Gemini)
    ├── Buffer de mensagens
    └── Agente interpreta intenção
         ↓
[n8n] Workflow 2 - Agente Agendamento
    ├── Consulta Django API → Serviços disponíveis
    ├── Consulta Django API → Horários disponíveis
    ├── Consulta Django API → Profissionais ativos
    └── Envia p/ Django API → Criar/Cancelar/Reagendar
         ↓
[Django] API /api/bot/processar/
    ├── Valida dados
    ├── Verifica conflitos
    ├── Cria agendamento
    ├── Retorna confirmação
    └── [Django Celery] Tarefa follow-up agendada
         ↓
[n8n] Recebe resposta e envia WhatsApp
```

---

## Migrações Necessárias

### 1️⃣ **Google Sheets → Django Models**

**Aba: Serviços**
```python
# Já existe: empresas.models.Servico
- nome
- duracao_minutos
- preco
- ativo
```

**Aba: horarios**
```python
# CRIAR NOVO MODEL
class HorarioFuncionamento(models.Model):
    empresa = models.ForeignKey(Empresa)
    dia_semana = models.IntegerField(0-6)  # 0=seg, 6=dom
    hora_abertura = models.TimeField()
    hora_fechamento = models.TimeField()
    intervalo_inicio = models.TimeField(null=True)  # almoço
    intervalo_fim = models.TimeField(null=True)
    ativo = models.BooleanField(default=True)
```

**Aba: datas_especiais**
```python
# CRIAR NOVO MODEL
class DataEspecial(models.Model):
    empresa = models.ForeignKey(Empresa)
    data = models.DateField()
    descricao = models.CharField(max_length=200)  # "Natal", "Ano Novo"
    tipo = models.CharField(choices=[
        ('feriado', 'Feriado - Fechado'),
        ('especial', 'Horário Especial')
    ])
    hora_abertura = models.TimeField(null=True)
    hora_fechamento = models.TimeField(null=True)
```

---

### 2️⃣ **Supabase → Django Database**

**Tabela: crm_geral** → Já existe como `Agendamento`

Adicionar campos:
```python
# agendamentos/models.py
class Agendamento(models.Model):
    # ... campos existentes ...

    # ADICIONAR:
    notificado_1dia = models.BooleanField(default=False)
    notificado_1hora = models.BooleanField(default=False)
    origem = models.CharField(max_length=20, choices=[
        ('whatsapp', 'WhatsApp'),
        ('manual', 'Manual'),
        ('site', 'Site')
    ], default='manual')
```

---

### 3️⃣ **Follow-up: n8n → Django Celery**

**De:** Schedule Trigger (n8n) → Supabase → HTTP Request (Evolution API)

**Para:** Celery Beat (Django) → Django DB → Evolution API

**Implementar:**
```python
# agendamentos/tasks.py

@shared_task
def enviar_notificacao_1dia():
    """Roda diariamente às 09:00"""
    agora = timezone.now()
    amanha = agora + timedelta(days=1)

    agendamentos = Agendamento.objects.filter(
        status='confirmado',
        data_hora_inicio__date=amanha.date(),
        notificado_1dia=False
    )

    for ag in agendamentos:
        enviar_whatsapp(
            telefone=ag.cliente.telefone,
            mensagem=gerar_mensagem_1dia(ag)
        )
        ag.notificado_1dia = True
        ag.save()

@shared_task
def enviar_notificacao_1hora():
    """Roda a cada 30 minutos"""
    agora = timezone.now()
    daqui_1h = agora + timedelta(hours=1)

    agendamentos = Agendamento.objects.filter(
        status='confirmado',
        data_hora_inicio__gte=agora,
        data_hora_inicio__lte=daqui_1h,
        notificado_1hora=False
    )

    for ag in agendamentos:
        enviar_whatsapp(
            telefone=ag.cliente.telefone,
            mensagem=gerar_mensagem_1hora(ag)
        )
        ag.notificado_1hora = True
        ag.save()
```

---

## APIs Django a Criar

### 1. **API de Consulta de Horários**

```python
# agendamentos/api_views.py

@api_view(['POST'])
@authentication_classes([APIKeyAuthentication])
def consultar_horarios_disponiveis(request):
    """
    n8n chama para mostrar horários livres

    POST /api/agendamentos/horarios-disponiveis/
    {
        "profissional_id": 1,
        "data": "2025-12-23",
        "servico_id": 2
    }

    Response:
    {
        "horarios": ["09:00", "10:00", "14:00", "15:30"],
        "profissional": "Pedro Brandão",
        "servico": "Corte + Barba",
        "duracao_minutos": 45
    }
    """
```

### 2. **API de Listagem de Serviços**

```python
@api_view(['GET'])
@authentication_classes([APIKeyAuthentication])
def listar_servicos(request):
    """
    GET /api/servicos/

    Response:
    {
        "servicos": [
            {
                "id": 1,
                "nome": "Corte de Cabelo",
                "duracao_minutos": 30,
                "preco": "40.00"
            },
            ...
        ]
    }
    """
```

### 3. **API de Profissionais**

```python
@api_view(['GET'])
@authentication_classes([APIKeyAuthentication])
def listar_profissionais(request):
    """
    GET /api/profissionais/

    Response:
    {
        "profissionais": [
            {
                "id": 1,
                "nome": "Pedro Brandão",
                "ativo": true
            },
            ...
        ]
    }
    """
```

### 4. **API de Agendamento (já existe, adaptar)**

Melhorar `/api/bot/processar/` para retornar:
```python
{
    "sucesso": true,
    "mensagem": "✅ Agendamento confirmado!...",
    "dados": {
        "agendamento_id": 123,
        "codigo": "ABC123",
        "data_hora": "23/12/2025 às 14:00",
        "profissional": "Pedro Brandão",
        "servico": "Corte + Barba",
        "valor": 55.00,
        "duracao_minutos": 45
    }
}
```

---

## Adaptações nos Workflows n8n

### Workflow 2 - Agente de Agendamento

**ANTES:**
- Tool: `serviTool` (Google Sheets)
- Tool: `horarios` (Google Sheets)
- Tool: `datas_especiais` (Google Sheets)
- Tool: `pedroTool` (sub-workflow → Google Calendar + Supabase)

**DEPOIS:**
- Tool: **HTTP Request → Django API** `/api/servicos/`
- Tool: **HTTP Request → Django API** `/api/horarios-funcionamento/`
- Tool: **HTTP Request → Django API** `/api/datas-especiais/`
- Tool: **HTTP Request → Django API** `/api/bot/processar/`

---

## Cronograma de Migração

### Fase 1: Preparar Django ✅ (já existe estrutura base)
- [x] Models de Agendamento
- [x] Models de Cliente
- [x] Models de Serviço
- [x] Models de Profissional

### Fase 2: Criar Models Faltantes
- [ ] HorarioFuncionamento
- [ ] DataEspecial
- [ ] Adicionar campos de notificação em Agendamento

### Fase 3: Migrar Dados
- [ ] Exportar Google Sheets
- [ ] Importar para Django Admin
- [ ] Exportar Supabase
- [ ] Importar para Django DB

### Fase 4: Criar APIs
- [ ] API listagem serviços
- [ ] API listagem profissionais
- [ ] API horários disponíveis
- [ ] API datas especiais
- [ ] Melhorar API de agendamento

### Fase 5: Adaptar n8n
- [ ] Substituir Google Sheets tools por HTTP Request
- [ ] Substituir Supabase por Django API
- [ ] Testar fluxo completo

### Fase 6: Implementar Follow-up Django
- [ ] Criar tasks Celery
- [ ] Criar schedule Celery Beat
- [ ] Integrar com Evolution API
- [ ] Desativar workflow 4 (n8n)

### Fase 7: Deprecar Workflows
- [ ] Remover workflow 3 (Agendamento Fixo)
- [ ] Remover workflows de "Fixo" dos profissionais

---

## Benefícios da Migração

✅ **Banco de dados centralizado** - Tudo no PostgreSQL/SQLite
✅ **Menos dependências externas** - Sem Google Sheets, sem Supabase
✅ **Melhor controle** - Admin Django para gerenciar tudo
✅ **Recorrência nativa** - Django já implementa
✅ **Follow-up automático** - Celery Beat
✅ **API única** - Todas operações passam pelo Django
✅ **Histórico completo** - Logs, auditoria
✅ **Escalabilidade** - Preparado para múltiplas empresas
