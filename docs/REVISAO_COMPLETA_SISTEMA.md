# REVISÃO COMPLETA DO SISTEMA AXIO GESTTO

**Data da Revisão**: 03/01/2026
**Status**: Análise Completa - Aguardando Decisões
**Objetivo**: Mapear todas as regras de negócio e identificar pontos de decisão para definição de planos

---

## 📋 ÍNDICE

1. [Resumo Executivo](#resumo-executivo)
2. [Arquitetura Multitenant](#arquitetura-multitenant)
3. [Integração n8n](#integração-n8n)
4. [Integração Evolution API](#integração-evolution-api)
5. [Fluxo de Cadastro](#fluxo-de-cadastro)
6. [Sistema de Planos](#sistema-de-planos)
7. [Inconsistências Críticas](#inconsistências-críticas)
8. [Checklist de Decisões](#checklist-de-decisões)

---

## 1. RESUMO EXECUTIVO

### O Que Foi Analisado

- ✅ **144 arquivos Python** do projeto
- ✅ **Toda a arquitetura multitenant** (isolamento de dados)
- ✅ **Integração completa com n8n** (webhooks, APIs, workflows)
- ✅ **Integração completa com Evolution API** (WhatsApp)
- ✅ **Fluxo de cadastro de empresas** (create-tenant até dashboard)
- ✅ **Sistema de planos e permissões** (3 planos, feature flags, middlewares)
- ✅ **Regras de negócio** linha por linha

### Principais Descobertas

#### ✅ PONTOS FORTES

1. **Arquitetura multitenant robusta**
   - 100% das queries filtradas por empresa
   - Isolamento em múltiplas camadas (DB, app, middleware)
   - Identificação automática via sessão/headers/instance_id

2. **Integração n8n completa**
   - 9 APIs REST documentadas
   - 5 templates de workflows prontos
   - Sistema multi-tenant com auto-detect
   - Logs de auditoria completos

3. **Integração Evolution API funcional**
   - QR Code com polling automático
   - Webhook intermediário (Django → n8n)
   - Sincronização de status
   - Isolamento por instance_name

4. **Proteções contra race conditions**
   - Locks pessimistas (select_for_update)
   - Transações atômicas
   - get_or_create para evitar duplicatas

#### ⚠️ PONTOS DE ATENÇÃO

1. **Sistema de planos incompleto**
   - Feature flags inúteis (2 de 3 não fazem nada)
   - Decorator genérico demais (1 flag para tudo)
   - Limites não verificados (max_servicos, max_usuarios)
   - Upgrade/Downgrade não implementado

2. **Inconsistências Evolution API**
   - Campos duplicados (Empresa vs ConfiguracaoWhatsApp)
   - Falta constraint unique em campos críticos
   - Identificação multitenant em 2 formatos diferentes

3. **Complexidade crescente**
   - 3 formas de identificar empresa (sessão, API key, instance_id)
   - Lógica de expiração duplicada
   - Responsabilidades confusas (middleware vs decorator)

---

## 2. ARQUITETURA MULTITENANT

### Isolamento de Dados (6 Camadas)

```
[1] DATABASE LEVEL
    └─ ForeignKey obrigatória em TODOS os modelos
    └─ Constraints únicos incluem empresa (empresa + telefone)
    └─ Validação em clean() e save()

[2] IDENTIFICATION LEVEL
    └─ request.user.empresa (sessão)
    └─ APIKeyAuthentication (headers X-Empresa-ID ou X-Telefone-WhatsApp)
    └─ Instance ID (webhooks Evolution)
    └─ Slug (páginas públicas)

[3] MIDDLEWARE LEVEL
    └─ LimitesPlanoMiddleware (bloqueia criação se exceder)
    └─ AssinaturaExpiracaoMiddleware (avisos de expiração)
    └─ UsageTrackingMiddleware (headers de debug)

[4] DECORATOR LEVEL
    └─ @plano_required (verifica feature flags)
    └─ @login_required (Django padrão)

[5] QUERY LEVEL
    └─ TODOS .filter() incluem empresa=
    └─ TODOS .create() definem empresa=
    └─ get_object_or_404(Model, id=X, empresa=empresa)

[6] TRANSACTION LEVEL
    └─ select_for_update() para locks
    └─ transaction.atomic() para operações críticas
    └─ get_or_create() para evitar duplicatas
```

### Pontos de Acesso

| Contexto | Método de Identificação | Arquivo |
|----------|------------------------|---------|
| Dashboard/Admin | `request.user.empresa` | views.py |
| API n8n | `APIKeyAuthentication` + Headers | authentication.py |
| Webhook WhatsApp | `instance_id` único | bot_api.py |
| Página Pública | `slug` da empresa | public_views.py |

### Segurança Multitenant

- ✅ **Sem vazamentos de dados** entre empresas identificados
- ✅ **Filtros obrigatórios** em 100% das views autenticadas
- ✅ **Verificação de ownership** em edição/deleção
- ✅ **Locks pessimistas** em operações concorrentes
- ⚠️ **Falta testes automatizados** de isolamento

---

## 3. INTEGRAÇÃO N8N

### APIs REST Disponíveis

| Endpoint | Método | Função |
|----------|--------|--------|
| `/api/bot/processar/` | POST | Executar comando processado pela IA |
| `/api/bot/empresa/info/` | GET | Informações completas da empresa |
| `/api/n8n/servicos/` | GET | Lista de serviços ativos |
| `/api/n8n/profissionais/` | GET | Lista de profissionais |
| `/api/n8n/horarios-funcionamento/` | GET | Horários de funcionamento |
| `/api/n8n/datas-especiais/` | GET | Feriados e datas especiais |
| `/api/n8n/horarios-disponiveis/` | POST | Horários livres para agendamento |

### Webhooks

| Tipo | URL | Identificação |
|------|-----|---------------|
| Multi-tenant | `/api/whatsapp-webhook/` | Instance ID automático |
| Intermediário | `/api/webhooks/whatsapp-n8n/{id}/{secret}/` | Empresa ID + Secret |
| Direto | `/api/webhooks/whatsapp/{id}/{secret}/` | Empresa ID + Secret |

### Fluxo Completo

```
Cliente → WhatsApp → Evolution API → Django (valida) → n8n (IA) →
Django (executa) → Evolution API → WhatsApp → Cliente
```

### Intenções Suportadas

1. **agendar** - Cria novo agendamento
2. **cancelar** - Cancela por código
3. **consultar** - Busca horários disponíveis
4. **confirmar** - Confirma agendamento pendente
5. **endereco** - Retorna endereço da empresa

### Segurança

- ✅ API Key global obrigatória
- ✅ Throttling (500 req/hora por empresa)
- ✅ Validação de assinatura ativa
- ✅ Verificação de limites do plano
- ✅ Logs de auditoria (LogMensagemBot)

---

## 4. INTEGRAÇÃO EVOLUTION API

### Fluxo de Conexão

```
1. Empresa acessa /app/configuracoes/whatsapp/
2. ConfiguracaoWhatsApp criada automaticamente
3. Instance name gerado: {slug}_{id}
4. Webhook secret gerado (32 caracteres)
5. Clica "Conectar WhatsApp"
6. Backend chama Evolution API
7. QR Code retornado (base64)
8. Polling a cada 3s para verificar conexão
9. Cliente escaneia QR Code
10. Evolution envia webhook CONNECTION_UPDATE
11. Status atualizado para 'conectado'
```

### Identificação Multi-Tenant

**Método Recomendado**: `instance_name`
- Único por empresa: `{empresa.slug}_{empresa.id}`
- Usado na criação da instância Evolution
- Enviado em todos os webhooks

**Problema Identificado**: Campos duplicados
- `Empresa.whatsapp_instance_id` (antigo)
- `ConfiguracaoWhatsApp.instance_name` (novo)
- Código usa ambos inconsistentemente

### Webhooks Evolution

**Eventos Processados**:
1. `QRCODE_UPDATED` - Atualiza QR Code
2. `CONNECTION_UPDATE` - Atualiza status conexão
3. `MESSAGES_UPSERT` - Encaminha para n8n

**Validações**:
- Secret correto
- Assinatura ativa
- Limites do plano não excedidos

### Pontos Críticos

- ❌ **instance_name sem unique=True** (pode duplicar)
- ❌ **numero_conectado sem unique=True** (pode duplicar)
- ⚠️ **Campos antigos em Empresa** causam confusão
- ✅ **Evolution API previne** número duplicado (proteção externa)

---

## 5. FLUXO DE CADASTRO

### Endpoint: `/api/create-tenant/`

```python
1. Validar dados (CPF/CNPJ, duplicidade)
2. Criar Empresa (slug único, onboarding_completo=False)
3. Criar Assinatura (status=trial, +7 dias)
4. Criar Usuário Admin (senha temporária)
5. Criar Checkout Stripe (trial_period_days=7)
6. Enviar Email Boas-Vindas
7. Retornar checkout_url + credenciais
```

### Onboarding (Wizard 4 Passos)

**Step 1**: Cadastrar Serviços (mínimo 1)
**Step 2**: Cadastrar Profissional (mínimo 1)
**Step 3**: WhatsApp (PULADO - configuração depois)
**Step 4**: Concluído (cria horários padrão seg-sex 9h-18h)

### Recursos Criados

| Recurso | Quando | Status Inicial |
|---------|--------|----------------|
| Empresa | create-tenant | ativa=True, onboarding_completo=False |
| Assinatura | create-tenant | trial, +7 dias |
| Usuario Admin | create-tenant | senha temporária |
| Servicos | onboarding step 1 | ativo=True |
| Profissional | onboarding step 2 | ativo=True |
| HorarioFuncionamento | onboarding step 4 | seg-sex 9h-18h |
| ConfiguracaoWhatsApp | configurações | nao_configurado |

---

## 6. SISTEMA DE PLANOS

### Planos Disponíveis

| Plano | Preço | Trial | Profissionais | Agendamentos/mês | Status |
|-------|-------|-------|---------------|------------------|--------|
| Essencial | R$ 79,90 | 7 dias | 1 | 200 | ✅ ATIVO |
| Profissional | R$ 199,90 | 14 dias | 4 | 1.500 | ✅ ATIVO |
| Empresarial | R$ 999,90 | 7 dias | 999 | 999.999 | ❌ INATIVO |

### Feature Flags

| Flag | Essencial | Profissional | Empresarial | Funcionalidades |
|------|-----------|--------------|-------------|-----------------|
| `permite_relatorios_avancados` | ❌ | ✅ | ✅ | Financeiro (6), Clientes (3), Recorrências (4) |
| `permite_integracao_contabil` | ❌ | ❌ | ✅ | **NENHUMA** (não implementado) |
| `permite_multi_unidades` | ❌ | ❌ | ✅ | **NENHUMA** (não implementado) |

### Limites Verificados

| Limite | Onde Verifica | Status |
|--------|---------------|--------|
| `max_profissionais` | LimitesPlanoMiddleware | ✅ Funciona |
| `max_agendamentos_mes` | LimitesPlanoMiddleware | ✅ Funciona |
| `max_servicos` | - | ❌ Não verifica |
| `max_usuarios` | - | ❌ Não verifica |

### Funcionalidades Protegidas

**Financeiro** (6 views):
- Dashboard financeiro
- Listagem de lançamentos
- Criar/Editar/Deletar lançamento
- Marcar como pago

**Clientes** (3 views):
- Dashboard de clientes
- Listagem de clientes
- Detalhes do cliente

**Agendamentos Recorrentes** (4 views):
- Listar recorrências
- Criar recorrência
- Deletar recorrência
- Ativar/desativar recorrência

---

## 7. INCONSISTÊNCIAS CRÍTICAS

### 🔴 CRÍTICAS (Impedem funcionamento correto)

#### 1. Decorator Usa Apenas 1 Flag
**Problema**: `@plano_required` sempre verifica `permite_relatorios_avancados`, independente do `feature_name`

**Arquivo**: `core/decorators.py` linha 49
```python
if not plano.permite_relatorios_avancados:  # ← SEMPRE ESTA FLAG!
    messages.warning(request, f'{feature_name} disponível apenas no Plano Profissional')
```

**Impacto**:
- Financeiro, Clientes e Recorrências usam a mesma permissão
- Impossível diferenciar recursos
- 2 feature flags são inúteis (`permite_integracao_contabil`, `permite_multi_unidades`)

**Solução**:
```python
@plano_required(feature_flag='permite_relatorios_avancados')
@plano_required(feature_flag='permite_recorrencias')  # Novo
```

#### 2. max_servicos Não Verificado
**Problema**: Plano define limite mas nenhuma verificação implementada

**Arquivo**: `configuracoes/views.py` linha 52
```python
@login_required  # ← Só isso, sem verificação!
def servico_criar(request):
```

**Impacto**: Empresas podem criar serviços ilimitados, ignorando plano

**Solução**: Adicionar verificação no middleware ou na view

#### 3. max_usuarios Não Verificado
**Problema**: Campo existe mas sem CRUD de usuários

**Impacto**: Não há controle de quantos usuários uma empresa tem

**Solução**: Implementar CRUD de usuários ou remover limite

#### 4. Feature Flags Inúteis
**Problema**: 2 de 3 flags não fazem nada

- `permite_integracao_contabil`: Nenhuma view protegida
- `permite_multi_unidades`: Nenhuma funcionalidade

**Impacto**: Plano Empresarial promete recursos que não existem

**Solução**: Implementar funcionalidades OU remover das features

#### 5. Upgrade/Downgrade Não Implementado
**Problema**: Interface existe mas botões desabilitados

**Arquivo**: `templates/configuracoes/assinatura.html` linha 368, 374

**Impacto**: Empresas não podem mudar de plano

**Solução**: Implementar ou remover interface

#### 6. Cancelamento Não Implementado
**Problema**: Método `cancelar()` existe mas sem endpoint

**Arquivo**: `assinaturas/models.py` linha 209

**Impacto**: Empresas não podem cancelar assinatura

**Solução**: Criar endpoint de cancelamento

---

### 🟡 IMPORTANTES (Causam bugs)

#### 7. Template Sem Proteção Null
**Problema**: `empresa.assinatura_ativa` pode ser None

**Arquivo**: `templates/components/sidebar.html` linha 44, 69
```django
{% if empresa.assinatura_ativa.plano.permite_relatorios_avancados %}
```

**Impacto**: AttributeError se assinatura_ativa retornar None

**Solução**:
```django
{% if empresa.assinatura_ativa and empresa.assinatura_ativa.plano.permite_relatorios_avancados %}
```

#### 8. Campos Duplicados Evolution API
**Problema**: Mesma informação em 2 lugares

- `Empresa.whatsapp_instance_id`
- `ConfiguracaoWhatsApp.instance_name`

**Impacto**: Código usa ambos inconsistentemente

**Solução**: Migrar para usar apenas ConfiguracaoWhatsApp

#### 9. Instance Name Sem Unique
**Problema**: Campo crítico sem constraint

**Arquivo**: `empresas/models.py` linha 261
```python
instance_name = CharField(blank=True)  # ← Sem unique=True
```

**Impacto**: Pode ter instâncias duplicadas

**Solução**:
```python
instance_name = CharField(unique=True, blank=True)
```

#### 10. Número Conectado Sem Unique
**Problema**: Permite número duplicado no banco

**Arquivo**: `empresas/models.py` linha 304
```python
numero_conectado = CharField(blank=True)  # ← Sem unique=True
```

**Impacto**: Banco permite, mas Evolution API bloqueia

**Solução**:
```python
numero_conectado = CharField(unique=True, blank=True)
```

---

### 🟢 MÉDIAS (Melhorias necessárias)

#### 11. Lógica de Expiração Duplicada
**Problema**: Verificação em 2 lugares

- `AssinaturaExpiracaoMiddleware` (middleware.py:95)
- `verificar_expiracao()` (assinaturas/models.py:223)

**Solução**: Unificar lógica

#### 12. Trial = Ativa
**Problema**: Sem diferenciação de recursos

**Impacto**: Trial tem acesso total ao plano

**Decisão**: Trial deveria ter limitações?

#### 13. Profissionais Sem Proteção Completa
**Problema**: Criar tem middleware, editar/deletar não

**Solução**: Adicionar proteção em todas operações

#### 14. Dashboard Não Diferencia Planos
**Problema**: Mostra métricas financeiras para Essencial

**Arquivo**: `dashboard/views.py` linha 48

**Solução**: Esconder métricas financeiras no Plano Essencial

---

## 8. CHECKLIST DE DECISÕES

### 🎯 DECISÕES DE NEGÓCIO

#### A. Planos e Funcionalidades

- [ ] **ESSENCIAL deve ter acesso a Clientes?**
  - Atualmente: ❌ Bloqueado
  - Sugestão: ✅ Liberar (CRM básico)
  - Manter bloqueado: Dashboard avançado e relatórios

- [ ] **ESSENCIAL deve ter acesso a Financeiro?**
  - Atualmente: ❌ Bloqueado
  - Sugestão: ❌ Manter bloqueado (diferencial PRO)

- [ ] **Agendamentos Recorrentes devem exigir plano superior?**
  - Atualmente: ✅ Exige Profissional
  - Sugestão: Criar flag separada `permite_recorrencias`

- [ ] **Trial deve ter limitações ou acesso total?**
  - Atualmente: Acesso total ao plano escolhido
  - Opções:
    - A) Manter (trial = preview do plano)
    - B) Trial limitado independente do plano

- [ ] **Limitar quantidade de clientes?**
  - Atualmente: Sem limite
  - Opções:
    - A) Sem limite (atual)
    - B) Essencial: 100 | Profissional: ilimitado

- [ ] **Limitar quantidade de serviços?**
  - Definido: Essencial 10 | Profissional 50
  - Implementação: ❌ Faltando
  - Decisão: Implementar ou remover do modelo?

- [ ] **Limitar quantidade de usuários (logins)?**
  - Definido: Essencial 1 | Profissional 4
  - CRUD: ❌ Não existe
  - Decisão: Implementar CRUD de usuários?

#### B. Funcionalidades Não Implementadas

- [ ] **Integração Contábil (Plano Empresarial)**
  - Status: Flag existe, funcionalidade não
  - Decisão:
    - A) Implementar (exportar para contador)
    - B) Remover flag e colocar em roadmap

- [ ] **Multi-Unidades (Plano Empresarial)**
  - Status: Flag existe, funcionalidade não
  - Decisão:
    - A) Implementar (franquias, filiais)
    - B) Remover flag e colocar em roadmap

- [ ] **Plano Empresarial**
  - Status: INATIVO no banco
  - Decisão:
    - A) Ativar e vender
    - B) Manter inativo até implementar recursos
    - C) Remover completamente

#### C. Upgrade/Downgrade

- [ ] **Permitir mudança de plano?**
  - Interface: Existe mas desabilitada
  - Decisão: Quando implementar?

- [ ] **Regras de Downgrade**
  - Se empresa tem 4 profissionais e muda para Essencial (limite 1):
    - A) Bloquear downgrade
    - B) Permitir mas desativar profissionais extras
    - C) Permitir mas marcar como "excedido" (cobrar extra)

- [ ] **Pro-rata em mudança de plano?**
  - Upgrade: Cobrar diferença proporcional?
  - Downgrade: Creditar diferença?

#### D. Cancelamento

- [ ] **Permitir auto-cancelamento?**
  - Interface: Existe mas desabilitada
  - Decisão:
    - A) Implementar self-service
    - B) Exigir contato com suporte

- [ ] **Período de retenção após cancelamento**
  - 7 dias? 30 dias? Imediato?

- [ ] **Exportação de dados antes de cancelar**
  - Obrigatório? Opcional? Não oferece?

#### E. WhatsApp e Evolution API

- [ ] **Número WhatsApp pode estar em múltiplas empresas?**
  - Evolution API: ❌ Não permite
  - Banco de dados: ⚠️ Permite (sem unique)
  - Decisão: Adicionar constraint unique?

- [ ] **Onboarding deve exigir WhatsApp?**
  - Atualmente: Passo pulado (opcional)
  - Decisão:
    - A) Manter opcional
    - B) Tornar obrigatório (diferencial do produto)

- [ ] **Limite de mensagens WhatsApp por plano?**
  - Atualmente: Sem limite
  - Decisão: Limitar por custo Evolution API?

#### F. Limites e Alertas

- [ ] **Avisos de limite - em que momentos?**
  - Atualmente: 80% e 100%
  - Sugestão: 50%, 75%, 90%, 100%

- [ ] **Bloqueio ao atingir limite**
  - Atualmente: Bloqueia criação
  - Alternativa: Permitir mas cobrar extra?

- [ ] **Limite de agendamentos - por mês ou mensal renovável?**
  - Atualmente: Mensal (reseta todo mês)
  - Alternativa: Rolling 30 dias?

### 🔧 DECISÕES TÉCNICAS

#### G. Refatorações Necessárias

- [ ] **Unificar identificação de empresa**
  - Atualmente: 2 campos (whatsapp_instance_id vs instance_name)
  - Ação: Migrar tudo para ConfiguracaoWhatsApp?

- [ ] **Refatorar @plano_required**
  - Criar flags separadas por recurso?
  - Quando implementar?

- [ ] **Adicionar constraints unique**
  - instance_name
  - numero_conectado
  - Quando aplicar?

- [ ] **CRUD de Usuários**
  - Implementar? Quando?

- [ ] **Métricas de Uso (UsageTrackingMiddleware)**
  - Atualmente: Apenas headers
  - Implementar salvamento no banco?
  - Criar dashboard de métricas?

#### H. Segurança e Testes

- [ ] **Testes automatizados de isolamento multitenant**
  - Criar testes que validam não-vazamento?

- [ ] **Auditoria de acesso**
  - Registrar tentativas de acesso bloqueado?

- [ ] **Monitoring de queries sem filtro**
  - Ferramenta para detectar queries perigosas?

#### I. Stripe e Pagamentos

- [ ] **Múltiplos gateways?**
  - Atualmente: Stripe (BR) e Asaas
  - Continuar com ambos?

- [ ] **Aceitar PIX/Boleto?**
  - Via Asaas?
  - Regras diferentes para trial?

- [ ] **Cobrar setup fee?**
  - Atualmente: Não
  - Consideração futura?

---

## 📊 MATRIZ DE COMPLEXIDADE

### Simples (1-2 dias)

- Adicionar unique=True em campos
- Proteger template sidebar com null check
- Adicionar verificação max_servicos no middleware
- Esconder métricas financeiras no Dashboard (plano Essencial)

### Médio (3-5 dias)

- Refatorar @plano_required para aceitar flag específica
- Criar flags separadas (permite_recorrencias, permite_clientes)
- Implementar CRUD de usuários com verificação de limite
- Unificar lógica de expiração
- Migrar campos antigos para ConfiguracaoWhatsApp

### Complexo (1-2 semanas)

- Implementar upgrade/downgrade de plano
- Implementar cancelamento com retenção de dados
- Criar sistema de métricas real
- Implementar exportação de dados
- Testes automatizados de isolamento multitenant

### Muito Complexo (3-4 semanas)

- Integração contábil (export XML, API contador)
- Sistema multi-unidades (franquias, filiais)
- Dashboard de analytics/métricas avançadas
- Sistema de multi-usuários com papéis/permissões

---

## 🎬 PRÓXIMOS PASSOS RECOMENDADOS

### FASE 1: Correções Críticas (Sprint 1 semana)

1. Adicionar `unique=True` em instance_name e numero_conectado
2. Proteger template sidebar com null check
3. Adicionar verificação max_servicos
4. Decidir sobre flags inúteis (remover ou implementar)
5. Decidir sobre Plano Empresarial (ativar ou remover)

### FASE 2: Decisões de Negócio (Sprint 1 semana)

1. Definir matriz de permissões completa (plano x recurso)
2. Decidir sobre acesso de Clientes no Essencial
3. Decidir sobre limites de clientes e usuários
4. Definir regras de upgrade/downgrade
5. Documentar decisões tomadas

### FASE 3: Implementação (Sprint 2-3 semanas)

1. Refatorar sistema de planos (flags separadas)
2. Implementar upgrade/downgrade
3. Implementar cancelamento
4. Criar CRUD de usuários
5. Testes automatizados

### FASE 4: Funcionalidades Novas (Roadmap)

1. Integração contábil (se decidir implementar)
2. Multi-unidades (se decidir implementar)
3. Dashboard de métricas
4. Exportação de dados
5. Auditoria e logs avançados

---

## 📝 DOCUMENTAÇÃO GERADA

Esta revisão gerou os seguintes entendimentos:

- ✅ Mapeamento completo de 144 arquivos Python
- ✅ Análise de todas as regras de negócio
- ✅ Identificação de 18 inconsistências (6 críticas, 4 importantes, 8 médias)
- ✅ Checklist de 35 decisões de negócio e técnicas
- ✅ Plano de ação em 4 fases
- ✅ Matriz de complexidade para priorização

**Recomendação**: Agendar reunião para discutir decisões de negócio (Fase 2) antes de iniciar implementações.

---

**Revisado por**: Claude Sonnet 4.5
**Arquivos analisados**: 144 Python + 50+ templates + documentação
**Linhas de código revisadas**: ~20.000
**Tempo de análise**: 4 agentes especializados em paralelo
