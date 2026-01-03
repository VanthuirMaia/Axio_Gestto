# 🎯 MATRIZ DE PERMISSÕES POR PLANO

**Versão**: 2.0 - Estratégia 2 Planos Simplificada
**Data**: 03/01/2026
**Status**: ✅ IMPLEMENTADO

---

## 📊 RESUMO DOS PLANOS

### PLANO ESSENCIAL - R$ 79,90/mês
**Público**: Profissionais autônomos
**Trial**: 7 dias gratuitos

### PLANO PROFISSIONAL - R$ 199,90/mês
**Público**: Estabelecimentos com equipe
**Trial**: 14 dias gratuitos

### PLANO EMPRESARIAL - R$ 999,90/mês
**Público**: Grandes empresas (INATIVO - roadmap futuro)
**Trial**: 7 dias gratuitos

---

## 🔐 MATRIZ COMPLETA DE PERMISSÕES

| Recurso | Essencial | Profissional | Empresarial | Feature Flag | Arquivo |
|---------|-----------|--------------|-------------|--------------|---------|
| **AGENDAMENTOS** |
| Criar agendamento | ✅ Ilimitado | ✅ Ilimitado | ✅ Ilimitado | - | agendamentos/views.py:43 |
| Editar agendamento | ✅ | ✅ | ✅ | - | agendamentos/views.py:149 |
| Deletar agendamento | ✅ | ✅ | ✅ | - | agendamentos/views.py:193 |
| Calendário | ✅ | ✅ | ✅ | - | agendamentos/views.py:24 |
| Agendamentos recorrentes | ❌ | ✅ | ✅ | `permite_recorrencias` | agendamentos/views.py:256 |
| **CLIENTES** |
| Listar clientes | ✅ | ✅ | ✅ | - | clientes/views.py:187 |
| Criar cliente | ✅ | ✅ | ✅ | - | clientes/views.py:231 |
| Editar cliente | ✅ | ✅ | ✅ | - | clientes/views.py:274 |
| Deletar cliente | ✅ | ✅ | ✅ | - | clientes/views.py:306 |
| Ver detalhes do cliente | ✅ | ✅ | ✅ | - | clientes/views.py:327 |
| Dashboard de clientes | ❌ | ✅ | ✅ | `permite_dashboard_clientes` | clientes/views.py:18 |
| **FINANCEIRO** |
| Dashboard financeiro | ❌ | ✅ | ✅ | `permite_financeiro` | financeiro/views.py:14 |
| Listar lançamentos | ❌ | ✅ | ✅ | `permite_financeiro` | financeiro/views.py:160 |
| Criar lançamento | ❌ | ✅ | ✅ | `permite_financeiro` | financeiro/views.py:199 |
| Editar lançamento | ❌ | ✅ | ✅ | `permite_financeiro` | financeiro/views.py:245 |
| Deletar lançamento | ❌ | ✅ | ✅ | `permite_financeiro` | financeiro/views.py:280 |
| Marcar como pago | ❌ | ✅ | ✅ | `permite_financeiro` | financeiro/views.py:294 |
| Criar categoria | ❌ | ✅ | ✅ | `permite_financeiro` | configuracoes/views.py:182 |
| Criar forma de pagamento | ❌ | ✅ | ✅ | `permite_financeiro` | configuracoes/views.py:228 |
| **CONFIGURAÇÕES** |
| Gerenciar serviços | ✅ (limite 3) | ✅ (limite 20) | ✅ (ilimitado) | - | configuracoes/views.py:52 |
| Gerenciar profissionais | ✅ (limite 1) | ✅ (limite 4) | ✅ (ilimitado) | - | configuracoes/views.py:109 |
| Configurar WhatsApp | ✅ | ✅ | ✅ | - | configuracoes/views.py:416 |
| Horários de funcionamento | ✅ | ✅ | ✅ | - | configuracoes/views.py:287 |
| Ver assinatura | ✅ | ✅ | ✅ | - | configuracoes/views.py:354 |
| **PÚBLICO** |
| Página de agendamento | ✅ | ✅ | ✅ | - | agendamentos/public_views.py:18 |
| **BOT WHATSAPP** |
| Agendamento via bot | ✅ | ✅ | ✅ | - | agendamentos/bot_api.py:120 |
| Cancelamento via bot | ✅ | ✅ | ✅ | - | agendamentos/bot_api.py:270 |
| Consulta via bot | ✅ | ✅ | ✅ | - | agendamentos/bot_api.py:323 |

---

## 🔢 LIMITES QUANTITATIVOS

| Limite | Essencial | Profissional | Empresarial | Verificado em |
|--------|-----------|--------------|-------------|---------------|
| Profissionais | 1 | 4 | 999 | middleware.py:110 |
| Agendamentos/mês | Ilimitado | Ilimitado | Ilimitado | - |
| Serviços | 3 | 20 | 999 | middleware.py:127 |
| Usuários (logins) | 1 | 4 | 999 | ❌ Não implementado |
| Clientes | Ilimitado | Ilimitado | Ilimitado | - |

**Observações**:
- ✅ **Agendamentos ilimitados**: Decisão aprovada (não há custo operacional)
- ❌ **Limite de usuários**: CRUD não implementado (futuro)
- ✅ **Limite de serviços**: IMPLEMENTADO na migração

---

## 🎨 FEATURE FLAGS (Modelo Plano)

### Novas Flags (Estratégia 2 Planos)

| Flag | Tipo | Default | Descrição |
|------|------|---------|-----------|
| `permite_financeiro` | Boolean | False | Acesso ao módulo Financeiro completo |
| `permite_dashboard_clientes` | Boolean | False | Dashboard de Clientes com métricas |
| `permite_recorrencias` | Boolean | False | Agendamentos recorrentes |

### Flags Antigas (DEPRECATED)

| Flag | Status | Motivo |
|------|--------|--------|
| `permite_relatorios_avancados` | DEPRECATED | Substituída por flags específicas |
| `permite_integracao_contabil` | DEPRECATED | Funcionalidade não implementada |
| `permite_multi_unidades` | DEPRECATED | Funcionalidade não implementada |

**Compatibilidade**: Flags antigas mantidas no código para compatibilidade, mas não devem ser usadas.

---

## 📝 CONFIGURAÇÃO DOS PLANOS (Fixture)

### Essencial
```json
{
  "nome": "essencial",
  "preco_mensal": "79.90",
  "max_profissionais": 1,
  "max_agendamentos_mes": 999999,
  "max_usuarios": 1,
  "max_servicos": 3,
  "trial_dias": 7,
  "permite_financeiro": false,
  "permite_dashboard_clientes": false,
  "permite_recorrencias": false,
  "ativo": true
}
```

### Profissional
```json
{
  "nome": "profissional",
  "preco_mensal": "199.90",
  "max_profissionais": 4,
  "max_agendamentos_mes": 999999,
  "max_usuarios": 4,
  "max_servicos": 20,
  "trial_dias": 14,
  "permite_financeiro": true,
  "permite_dashboard_clientes": true,
  "permite_recorrencias": true,
  "ativo": true
}
```

### Empresarial
```json
{
  "nome": "empresarial",
  "preco_mensal": "999.90",
  "max_profissionais": 999,
  "max_agendamentos_mes": 999999,
  "max_usuarios": 999,
  "max_servicos": 999,
  "trial_dias": 7,
  "permite_financeiro": true,
  "permite_dashboard_clientes": true,
  "permite_recorrencias": true,
  "permite_integracao_contabil": true,
  "permite_multi_unidades": true,
  "ativo": false
}
```

---

## 🛠️ IMPLEMENTAÇÃO TÉCNICA

### Decorator @plano_required

**Arquivo**: `core/decorators.py`

**Uso correto (NOVO)**:
```python
@login_required
@plano_required(feature_flag='permite_financeiro', feature_name='Controle Financeiro')
def financeiro_dashboard(request):
    ...
```

**Uso antigo (compatível mas não recomendado)**:
```python
@login_required
@plano_required(feature_name='Dashboard Financeiro')  # Usa permite_relatorios_avancados
def dashboard_antigo(request):
    ...
```

### Middleware LimitesPlanoMiddleware

**Arquivo**: `core/middleware.py`

**Rotas protegidas**:
- `/app/agendamentos/criar/` - Verifica limite de agendamentos
- `/app/configuracoes/profissionais/criar/` - Verifica limite de profissionais
- `/app/configuracoes/servicos/criar/` - Verifica limite de serviços (NOVO)
- `/app/agendamentos/recorrencias/criar/` - Exige plano Profissional

**Avisos progressivos**:
- 80% do limite: Warning amarelo
- 100% do limite: Bloqueio vermelho

### Templates

**Sidebar** (`templates/components/sidebar.html`):
```django
<!-- Clientes - LIBERADO PARA TODOS -->
<a href="{% url 'listar_clientes' %}">Clientes</a>

<!-- Financeiro - APENAS PROFISSIONAL -->
{% if empresa.assinatura_ativa and empresa.assinatura_ativa.plano.permite_financeiro %}
  <a href="{% url 'financeiro_dashboard' %}">Financeiro</a>
{% else %}
  <a class="nav-link-locked">
    Financeiro
    <span class="badge bg-warning">PRO</span>
  </a>
{% endif %}
```

---

## 📊 CAMINHO DE UPGRADE

### Quando o Cliente Deve Fazer Upgrade?

**Essencial → Profissional** quando:
1. ✅ Contratar o **primeiro funcionário** (limite 1 profissional)
2. ✅ Querer **controle de caixa** (não tem financeiro)
3. ✅ Ter **clientes fixos** (não tem recorrência)
4. ✅ Querer **métricas de clientes** (não tem dashboard)
5. ✅ Precisar de **mais de 3 serviços** (limite serviços)

### Gatilhos Automáticos de Upgrade

| Situação | Ação do Sistema |
|----------|-----------------|
| Tentou criar 2º profissional | Bloqueia + mensagem de upgrade |
| Tentou criar 4º serviço | Bloqueia + mensagem de upgrade |
| Clicou em "Financeiro" | Redireciona para página de upgrade |
| Tentou criar recorrência | Bloqueia + mensagem de upgrade |
| Clicou em "Dashboard Clientes" | Redireciona para página de upgrade |

---

## 🎯 VALOR POR PLANO

### Essencial R$ 79,90/mês = R$ 2,66/dia

**O que está incluído**:
- ✅ Bot WhatsApp inteligente 24/7
- ✅ Agendamentos online ilimitados
- ✅ Página de agendamento personalizada
- ✅ Gestão básica de clientes
- ✅ Notificações automáticas
- ✅ Calendário completo
- ✅ 1 profissional, 3 serviços

**ROI**: 3 agendamentos novos/mês = paga o sistema

### Profissional R$ 199,90/mês = R$ 6,66/dia

**TUDO DO ESSENCIAL +**:
- ✅ Controle financeiro completo
- ✅ Dashboard de métricas de clientes
- ✅ Agendamentos recorrentes
- ✅ 4 profissionais, 4 usuários
- ✅ 20 serviços

**ROI**: Com 4 profissionais = R$ 8k faturamento. Sistema paga em 1-2 dias.

---

## 🔄 MIGRAÇÃO E ATUALIZAÇÃO

### Aplicar Mudanças no Banco

1. **Ativar ambiente virtual**:
   ```bash
   venv\Scripts\activate  # Windows
   source venv/bin/activate  # Linux/Mac
   ```

2. **Aplicar migração**:
   ```bash
   python manage.py migrate assinaturas
   ```

3. **Carregar novos planos**:
   ```bash
   python manage.py loaddata assinaturas/fixtures/planos_iniciais.json
   ```

4. **Verificar planos**:
   ```bash
   python manage.py shell
   >>> from assinaturas.models import Plano
   >>> for p in Plano.objects.all():
   ...     print(f"{p.nome}: financeiro={p.permite_financeiro}, dashboard={p.permite_dashboard_clientes}, recorrencias={p.permite_recorrencias}")
   ```

### Atualizar Planos Existentes (SQL Direto)

Se já tiver empresas cadastradas:
```sql
-- Atualizar plano Essencial
UPDATE assinaturas_plano
SET permite_financeiro = 0,
    permite_dashboard_clientes = 0,
    permite_recorrencias = 0,
    max_servicos = 3,
    max_agendamentos_mes = 999999
WHERE nome = 'essencial';

-- Atualizar plano Profissional
UPDATE assinaturas_plano
SET permite_financeiro = 1,
    permite_dashboard_clientes = 1,
    permite_recorrencias = 1,
    max_servicos = 20,
    max_agendamentos_mes = 999999
WHERE nome = 'profissional';

-- Desativar plano Empresarial
UPDATE assinaturas_plano
SET ativo = 0
WHERE nome = 'empresarial';
```

---

## ✅ CHECKLIST DE IMPLEMENTAÇÃO

### Código (COMPLETO ✅)

- [x] Adicionar 3 novas feature flags ao modelo Plano
- [x] Refatorar decorator @plano_required para aceitar flag específica
- [x] Atualizar todas views de Financeiro (6 views)
- [x] Atualizar Dashboard de Clientes (1 view)
- [x] Liberar CRUD de Clientes para todos (3 views)
- [x] Atualizar Agendamentos Recorrentes (4 views)
- [x] Implementar verificação max_servicos no middleware
- [x] Atualizar template sidebar (Clientes liberado, Financeiro bloqueado)
- [x] Atualizar fixture de planos
- [x] Gerar migração do banco de dados

### Banco de Dados (PENDENTE ⏳)

- [ ] Ativar ambiente virtual
- [ ] Aplicar migração (`python manage.py migrate`)
- [ ] Carregar fixture atualizada (`loaddata planos_iniciais.json`)
- [ ] Verificar planos no banco

### Testes (PENDENTE ⏳)

- [ ] Testar login com plano Essencial
- [ ] Verificar Clientes liberado para Essencial
- [ ] Verificar Financeiro bloqueado para Essencial
- [ ] Testar criação de 4º serviço (deve bloquear)
- [ ] Testar login com plano Profissional
- [ ] Verificar tudo liberado no Profissional
- [ ] Testar upgrade Essencial → Profissional

### Documentação (COMPLETO ✅)

- [x] Criar matriz de permissões
- [x] Documentar feature flags
- [x] Criar guia de migração
- [x] Proposta de planos simplificada

---

## 📞 SUPORTE

**Dúvidas sobre implementação**: Ver `docs/PROPOSTA_PLANOS_SIMPLIFICADA.md`
**Revisão completa do sistema**: Ver `docs/REVISAO_COMPLETA_SISTEMA.md`
**Mudanças aplicadas**: Ver este arquivo (MATRIZ_PERMISSOES_PLANOS.md)
