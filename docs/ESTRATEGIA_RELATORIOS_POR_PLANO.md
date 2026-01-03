# Estratégia de Relatórios por Plano

Data: 2025-01-02
Versão: 1.0

## Estrutura de Planos

### 🟢 Plano Essencial - R$ 79,90/mês
- **1 profissional**
- **200 agendamentos/mês**
- **Trial: 7 dias**

### 🔥 Plano Profissional - R$ 199,90/mês (CARRO-CHEFE)
- **4 profissionais**
- **1500 agendamentos/mês**
- **Trial: 14 dias**

### 💼 Plano Personalizado - A partir de R$ 800/mês
- **Mais de 4 profissionais**
- **Recursos ilimitados**
- **Sob consulta comercial**

---

## Distribuição de Funcionalidades por Plano

### 🟢 PLANO ESSENCIAL - "Operação Básica"

**Objetivo:** Fazer o usuário sentir a dor de não ter dados financeiros e análise de clientes

#### ✅ Relatórios INCLUÍDOS:

1. **Dashboard Principal BÁSICO** (`core/views.py:dashboard_view`)
   - ✅ Agendamentos hoje
   - ✅ Agendamentos da semana
   - ✅ Próximos agendamentos (lista top 5)
   - ✅ Agendamentos pendentes de confirmação
   - ❌ SEM métricas financeiras
   - ❌ SEM métricas de clientes
   - ❌ SEM gráficos

2. **Calendário** (`agendamentos/views.py:calendario_view`)
   - ✅ Visualização mensal de agendamentos
   - ✅ Status por cores

3. **Listagem de Agendamentos**
   - ✅ Lista simples de agendamentos
   - ✅ Filtros básicos

4. **Dashboard de Configurações** (`configuracoes/views.py:configuracoes_dashboard`)
   - ✅ Gerenciamento de serviços
   - ✅ Gerenciamento de profissionais
   - ✅ Status do plano
   - ✅ WhatsApp status

#### ❌ NÃO INCLUÍDO (gera urgência de upgrade):

- ❌ Todo o módulo Financeiro (dashboard, lançamentos, contas)
- ❌ Todo o módulo de Clientes (dashboard, rankings, análises)
- ❌ Listagem de clientes (nem básica)
- ❌ Detalhes do cliente
- ❌ Métricas (ticket médio, faturamento, saldo)
- ❌ Gráficos e análises
- ❌ Recorrências

---

### 🔥 PLANO PROFISSIONAL - "Gestão Completa" (CARRO-CHEFE)

**Objetivo:** Entregar TUDO que um negócio precisa para crescer

#### ✅ Tudo do Essencial +

5. **Dashboard Principal COMPLETO** (`core/views.py:dashboard_view`)
   - ✅ Todas as métricas de agendamentos
   - ✅ Métricas financeiras (faturamento, receitas, despesas, saldo)
   - ✅ Métricas de clientes (total, ativos, novos, ticket médio)
   - ✅ Alertas (contas vencidas, clientes em risco)
   - ✅ Gráfico de faturamento (7 dias)
   - ✅ Top 5 clientes VIP

6. **Dashboard Financeiro COMPLETO** (`financeiro/views.py:financeiro_dashboard`)
   - ✅ Receitas do mês (total, pagas, pendentes)
   - ✅ Despesas do mês (total, pagas, pendentes)
   - ✅ Saldo real e previsto
   - ✅ Contas a receber (próximos 30 dias)
   - ✅ Contas a pagar (próximos 30 dias)
   - ✅ Gráfico de receitas por categoria
   - ✅ Filtro por mês/ano

7. **Lançamentos Financeiros** (`financeiro/views.py:lancamentos_lista`)
   - ✅ Lista completa de receitas e despesas
   - ✅ Filtros (tipo, status, categoria)
   - ✅ Todas as informações detalhadas

8. **Dashboard de Clientes COMPLETO** (`clientes/views.py:dashboard_clientes`)
   - ✅ Métricas gerais (total, novos, ativos, ticket médio)
   - ✅ Gráfico: novos clientes (6 meses)
   - ✅ Top 10 Clientes VIP (maior gasto)
   - ✅ Top 10 Clientes Frequentes (mais visitas)
   - ✅ Clientes em Risco (sem agendar +30 dias)
   - ✅ Aniversariantes do mês
   - ✅ Taxa de retenção

9. **Listagem de Clientes** (`clientes/views.py:listar_clientes`)
   - ✅ Lista completa com métricas
   - ✅ Total de agendamentos por cliente
   - ✅ Último agendamento
   - ✅ Total gasto
   - ✅ Filtros (busca, status)

10. **Detalhes do Cliente** (`clientes/views.py:detalhes_cliente`)
    - ✅ Estatísticas pessoais
    - ✅ Total gasto
    - ✅ Total de visitas
    - ✅ Histórico completo (últimos 20 agendamentos)

11. **Recorrências** (`agendamentos/views.py:listar_recorrencias`)
    - ✅ Agendamentos automáticos repetidos
    - ✅ Gestão de frequência (diária/semanal/mensal)

---

### 💼 PLANO PERSONALIZADO - "Sob Medida"

**Não é um plano self-service. Requer contato comercial.**

#### ✅ Tudo do Profissional +

- ✅ Recursos ilimitados
- ✅ Profissionais ilimitados
- ✅ Agendamentos ilimitados
- ✅ Multi-unidades
- ✅ API customizada
- ✅ Infraestrutura dedicada
- ✅ Suporte prioritário
- ✅ Integrações exclusivas
- ✅ Exportação de relatórios (PDF, Excel)
- ✅ Relatórios customizados (sob demanda)

**Público-alvo:**
- Empresas com mais de 4 profissionais
- Redes com múltiplas filiais
- Franquias
- Empresas que precisam de integrações específicas

---

## Implementação Técnica

### Campo no Model Plano:
```python
# assinaturas/models.py
permite_relatorios_avancados = models.BooleanField(default=False)
```

**Valores atuais:**
- Essencial: `permite_relatorios_avancados = False`
- Profissional: `permite_relatorios_avancados = True`
- Personalizado: `permite_relatorios_avancados = True`

### Como usar nas views:

```python
# Exemplo de proteção de view
from django.contrib import messages
from django.shortcuts import redirect

def dashboard_clientes(request):
    empresa = request.user.empresa
    assinatura = empresa.assinatura_ativa

    # Verificar se o plano permite relatórios avançados
    if not assinatura.plano.permite_relatorios_avancados:
        messages.warning(request,
            'Este relatório está disponível apenas no Plano Profissional ou superior. '
            'Faça upgrade para ter acesso a análises de clientes.')
        return redirect('core:dashboard')

    # Continuar com a lógica normal...
```

### Como usar nos templates:

```django
<!-- Exemplo de proteção no menu lateral -->
{% if request.user.empresa.assinatura_ativa.plano.permite_relatorios_avancados %}
    <a href="{% url 'clientes:dashboard' %}">
        <i class="bi bi-people"></i> Relatório de Clientes
    </a>
{% else %}
    <a href="#" class="disabled" title="Disponível no Plano Profissional">
        <i class="bi bi-people"></i> Relatório de Clientes
        <span class="badge bg-warning">PRO</span>
    </a>
{% endif %}
```

---

## Próximos Passos

1. ✅ Atualizar fixtures dos planos
2. ✅ Desativar plano Empresarial
3. ✅ Ajustar página de preços
4. ⏳ Implementar proteção nas views de relatórios
5. ⏳ Adicionar badges visuais no menu (PRO)
6. ⏳ Criar modal de upgrade quando tentar acessar recurso bloqueado

---

## Resumo Visual

```
┌─────────────────────────────────────────────────────────────┐
│                    RECURSOS POR PLANO                        │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  Funcionalidade         │ Essencial │ Profissional │ Custom │
│  ─────────────────────────────────────────────────────────  │
│  Agendamentos           │     ✅    │      ✅      │   ✅   │
│  Calendário             │     ✅    │      ✅      │   ✅   │
│  Configurações          │     ✅    │      ✅      │   ✅   │
│  ─────────────────────────────────────────────────────────  │
│  Financeiro             │     ❌    │      ✅      │   ✅   │
│  Clientes (análise)     │     ❌    │      ✅      │   ✅   │
│  Recorrências           │     ❌    │      ✅      │   ✅   │
│  ─────────────────────────────────────────────────────────  │
│  Multi-unidades         │     ❌    │      ❌      │   ✅   │
│  API/Integrações        │     ❌    │      ❌      │   ✅   │
│  Exportações            │     ❌    │      ❌      │   ✅   │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

---

**Resultado esperado:**
- Usuários do Essencial sentem a necessidade de upgrade ao não ter visão financeira
- Profissional se torna o plano "óbvio" para quem quer crescer
- Personalizado atende empresas maiores sem criar complexidade para todos
