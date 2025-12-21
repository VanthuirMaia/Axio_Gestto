# 📅 Eventos Recorrentes - Guia Completo

## ✅ STATUS: IMPLEMENTADO E PRONTO PARA USO!

---

## 🎯 O que são Eventos Recorrentes?

Agendamentos que se repetem automaticamente segundo uma regra (diária, semanal ou mensal).

**Exemplos:**
- Cliente com fisioterapia **todos os dias às 10h**
- Personal trainer **toda segunda, quarta e sexta às 7h**
- Consulta de retorno **todo dia 15 do mês às 14h**

---

## 🚀 Como Funciona

### 1. Você cria uma regra de recorrência
```
Cliente: João Silva
Serviço: Fisioterapia
Profissional: Dra. Maria
Frequência: Semanal (Segunda, Quarta, Sexta)
Horário: 10:00
Válido: 01/01/2025 até 31/03/2025
```

### 2. Sistema gera agendamentos automaticamente
**Quando:** Diariamente à meia-noite (00:00)
**Quantos:** Próximos 60 dias
**Validações:**
- ✅ Não cria se já existe
- ✅ Não cria se horário está ocupado
- ✅ Respeita data início e fim

### 3. Agendamentos aparecem no calendário
Como agendamentos normais, mas com a nota: "📅 Agendamento recorrente gerado automaticamente"

---

## 📋 Tipos de Recorrência

### 🟢 Diária
Agendamento se repete **todos os dias**

**Exemplo:**
```
Frequência: Diária
Horário: 14:00
→ Resultado: Agendamento criado todos os dias às 14:00
```

**Caso de uso:**
- Tratamentos diários (fisioterapia, fonoaudiologia)
- Aulas particulares diárias

---

### 🔵 Semanal
Agendamento se repete em **dias específicos da semana**

**Exemplo:**
```
Frequência: Semanal
Dias: Segunda, Quarta, Sexta
Horário: 07:00
→ Resultado: Agendamentos criados toda seg/qua/sex às 07:00
```

**Caso de uso:**
- Personal trainer (MWF)
- Aulas de idioma (ter/qui)
- Terapia semanal (toda quinta)

---

### 🟣 Mensal
Agendamento se repete no **mesmo dia do mês**

**Exemplo:**
```
Frequência: Mensal
Dia do mês: 15
Horário: 14:00
→ Resultado: Agendamento criado todo dia 15 às 14:00
```

**Caso de uso:**
- Consulta de retorno mensal
- Manutenção preventiva
- Revisão mensal

---

## 🖥️ Como Usar

### Passo 1: Acessar Recorrências
```
Menu → Agendamentos → Ver Recorrências
ou
URL: /agendamentos/recorrencias/
```

### Passo 2: Criar Nova Recorrência
1. Clicar em **"Nova Recorrência"**
2. Preencher formulário:
   - Cliente
   - Serviço
   - Profissional (opcional)
   - Frequência (diária/semanal/mensal)
   - Horário
   - Data início
   - Data fim (opcional - deixe vazio para infinito)

3. **Se semanal:** Selecionar dias da semana
4. **Se mensal:** Informar dia do mês (1-31)

### Passo 3: Sistema gera automaticamente
- À meia-noite, sistema cria agendamentos dos próximos 60 dias
- Agendamentos aparecem normalmente no calendário

---

## ⚙️ Gerenciamento

### Pausar Recorrência
- Clicar no botão ⏸️ (Pausar)
- Recorrência fica inativa
- **Não afeta agendamentos já criados**
- Para reativar: clicar em ▶️ (Ativar)

### Excluir Recorrência
- Clicar no botão 🗑️ (Excluir)
- Confirmação necessária
- **Não afeta agendamentos já criados**
- Apenas para de gerar novos

### Editar Agendamentos Criados
- Agendamentos gerados podem ser editados/cancelados normalmente
- Editar um agendamento NÃO afeta a recorrência

---

## 🔧 Configuração Técnica

### Celery Beat Configurado
No `config/settings.py`:

```python
CELERY_BEAT_SCHEDULE = {
    'gerar-agendamentos-recorrentes': {
        'task': 'agendamentos.tasks.gerar_agendamentos_recorrentes',
        'schedule': crontab(hour=0, minute=0),  # Diariamente às 00:00
    },
}
```

### Task de Geração
Em `agendamentos/tasks.py`:

```python
@shared_task
def gerar_agendamentos_recorrentes():
    """
    Gera agendamentos para os próximos 60 dias
    baseado nas recorrências ativas
    """
    # ... código ...
```

### Executar Manualmente (desenvolvimento)
```bash
# Via shell do Docker
docker exec -it gestao_web python manage.py shell

>>> from agendamentos.tasks import gerar_agendamentos_recorrentes
>>> gerar_agendamentos_recorrentes()
```

Ou via celery:
```bash
docker exec -it gestao_celery celery -A config call agendamentos.tasks.gerar_agendamentos_recorrentes
```

---

## 📊 Model

```python
class AgendamentoRecorrente(models.Model):
    # Informações básicas
    empresa = ForeignKey(Empresa)
    cliente = ForeignKey(Cliente)
    servico = ForeignKey(Servico)
    profissional = ForeignKey(Profissional, null=True)

    # Recorrência
    frequencia = CharField(choices=['diaria', 'semanal', 'mensal'])
    dias_semana = JSONField(default=list)  # [0, 2, 4] = seg/qua/sex
    dia_mes = IntegerField(null=True)  # 1-31
    hora_inicio = TimeField()

    # Período
    data_inicio = DateField()
    data_fim = DateField(null=True, blank=True)

    # Status
    ativo = BooleanField(default=True)
```

---

## ✅ Validações Implementadas

### No Frontend
- ✅ Frequência obrigatória
- ✅ Se semanal: pelo menos 1 dia selecionado
- ✅ Se mensal: dia entre 1-31
- ✅ Data início obrigatória
- ✅ Horário obrigatório

### No Backend
- ✅ Não cria se agendamento igual já existe
- ✅ Não cria se horário está ocupado (mesmo profissional)
- ✅ Respeita data_inicio e data_fim
- ✅ Desativa automaticamente recorrências expiradas

---

## 🎨 Interface

### Lista de Recorrências
- ✅ Visualização em tabela
- ✅ Filtros e busca (admin)
- ✅ Status visual (ativo/pausado)
- ✅ Ações rápidas (pausar/excluir)
- ✅ Descrição legível da recorrência

### Formulário de Criação
- ✅ Campos condicionais (dias semana / dia mês)
- ✅ Validação em tempo real
- ✅ Ajuda contextual
- ✅ Exemplos de uso
- ✅ Design responsivo

---

## 📝 Migrations

Para aplicar as mudanças no banco:

```bash
# Criar migration
docker exec -it gestao_web python manage.py makemigrations

# Aplicar migration
docker exec -it gestao_web python manage.py migrate
```

**Arquivo gerado:** `agendamentos/migrations/000X_agendamentorecorrente.py`

---

## 🐛 Troubleshooting

### Agendamentos não estão sendo gerados

**Verificar Celery Beat:**
```bash
# Ver logs do celery
docker-compose logs -f celery

# Verificar se beat está rodando
docker exec -it gestao_celery celery -A config inspect active
```

**Executar task manualmente:**
```bash
docker exec -it gestao_celery celery -A config call agendamentos.tasks.gerar_agendamentos_recorrentes
```

### Recorrência criada mas não aparece

**Verificar:**
1. Recorrência está ativa? (campo `ativo=True`)
2. Data de início não é futura demais? (gera apenas 60 dias à frente)
3. Data de fim não passou? (desativa automaticamente)

**Ver no admin:**
```
/admin/agendamentos/agendamentorecorrente/
```

### Conflito de horários

**Normal:** Se o profissional já tem agendamento no horário, a recorrência pula aquele dia.

**Solução:** Verificar calendário do profissional e ajustar horários conflitantes.

---

## 📈 Melhorias Futuras (opcional)

### ✨ Features possíveis:
1. **Editar recorrência existente** (atualmente: criar nova)
2. **Aplicar mudanças retroativas** (atualmente: só novos)
3. **Notificar cliente ao criar** (via WhatsApp)
4. **Recorrência personalizada** (ex: "a cada 2 semanas")
5. **Exportar recorrências** (CSV/PDF)
6. **Dashboard de recorrências** (estatísticas)

---

## 🎯 Exemplos de Uso Real

### Exemplo 1: Personal Trainer
```
Cliente: João Silva
Serviço: Treino Personalizado
Profissional: Prof. Carlos
Frequência: Semanal
Dias: Segunda, Quarta, Sexta
Horário: 07:00
Início: 01/01/2025
Fim: 31/03/2025 (3 meses)
```

**Resultado:** 36-40 agendamentos gerados automaticamente (3 dias/semana x 12-13 semanas)

### Exemplo 2: Fisioterapia Diária
```
Cliente: Maria Santos
Serviço: Fisioterapia
Profissional: Dra. Ana
Frequência: Diária
Horário: 14:00
Início: 15/01/2025
Fim: 15/02/2025 (30 dias)
```

**Resultado:** 30 agendamentos gerados (1 por dia)

### Exemplo 3: Consulta Mensal
```
Cliente: Pedro Costa
Serviço: Consulta de Retorno
Profissional: Dr. Paulo
Frequência: Mensal
Dia do mês: 10
Horário: 16:00
Início: 01/01/2025
Fim: (vazio = infinito)
```

**Resultado:** 12 agendamentos/ano (dia 10 de cada mês)

---

## 🚀 Como Testar

### 1. Criar recorrência de teste
```
Cliente: Teste
Serviço: Consulta
Frequência: Semanal
Dias: Hoje + amanhã
Horário: Qualquer
Início: Hoje
Fim: +7 dias
```

### 2. Executar task manualmente
```bash
docker exec -it gestao_web python manage.py shell

from agendamentos.tasks import gerar_agendamentos_recorrentes
result = gerar_agendamentos_recorrentes()
print(result)
```

### 3. Verificar calendário
- Abrir `/agendamentos/calendario/`
- Verificar se agendamentos apareceram
- Conferir nota: "📅 Agendamento recorrente..."

---

## ✅ Checklist de Implementação

- ✅ Model `AgendamentoRecorrente` criado
- ✅ Task Celery `gerar_agendamentos_recorrentes` criada
- ✅ Views CRUD implementadas
- ✅ Templates criados (listar + criar)
- ✅ URLs configuradas
- ✅ Admin registrado
- ✅ Celery Beat configurado
- ✅ Validações implementadas
- ✅ Documentação completa

---

## 📞 Suporte

**Dúvidas sobre eventos recorrentes?**
- Consulte esta documentação
- Verifique o admin: `/admin/agendamentos/agendamentorecorrente/`
- Veja logs do Celery: `docker-compose logs -f celery`

---

**Sistema de Eventos Recorrentes - Pronto para Produção! 🚀**

**Implementado em:** 2025-12-21
**Versão:** 1.0.0
