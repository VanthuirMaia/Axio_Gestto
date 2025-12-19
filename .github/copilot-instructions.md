# Instruções Copilot / Agente AI para Axio Gestto

Propósito: Orientação curta e prática para ajudar um agente AI a fazer mudanças seguras e corretas neste repositório.

## Visão geral
- Aplicação monolítica Django (Django 5) dividida em apps: `core`, `empresas`, `agendamentos`, `clientes`, `financeiro`, `dashboard`, `configuracoes`.
- Multi-tenant real: objetos são vinculados a uma `Empresa` (ver `empresas/models.py`). A maioria das queries deve filtrar por `empresa` obtida via `request.user.empresa` (usuário custom `core.Usuario`).
- Frontend renderizado no servidor + JavaScript (FullCalendar em `templates/agendamentos/calendario.html`). Endpoints de API usam autenticação por sessão (ex.: `/agendamentos/api/`).
- Background: APScheduler é usado em desenvolvimento (`financeiro.apps.FinanceiroConfig.ready()`); em produção use o `scripts/cron-jobs.sh`. Celery está configurado (`config/celery.py`) e é executado como serviço no `docker-compose.yml`.

## Comandos úteis (desenvolvimento)
- Crie um `.env` (veja `README.md`) e defina `DEBUG=True` para dev.
- Migrações e admin:
  - `python manage.py migrate`
  - `python manage.py createsuperuser`
- Rodar servidor: `python manage.py runserver`
- Docker: `docker-compose up -d` (serviços: `db`, `redis`, `web`, `celery`). O serviço `web` executa migrações e inicia `gunicorn`.
- Celery: `celery -A config worker -l info` (ou `docker-compose up celery`).
- Scheduler (dev): APScheduler inicia automaticamente quando `DEBUG=True`. Em produção, use `python manage.py processar_agendamentos_concluidos` (cron em `scripts/cron-jobs.sh`).
- Testes: `python manage.py test`
- Comando financeiro em modo de segurança: `python manage.py processar_agendamentos_concluidos --dry-run`

## Convenções importantes (prioridade alta)
- **Sempre** filtrar queries por `empresa` para evitar vazamento de dados entre clientes. Exemplo:

```python
# padrão correto (exemplo em agendamentos/views.py)
agendamento = get_object_or_404(Agendamento, id=id, empresa=request.user.empresa)
```

- Use `select_related()` em queries com muitas FKs para performance.
- Atenção com timezone: `TIME_ZONE = 'America/Recife'` (em `config/settings.py`). Use `django.utils.timezone` e `timezone.localtime()` ao serializar datas/horários.
- Contrato do JSON do calendário (em `agendamentos/api_agendamentos`): retornar lista de eventos com pelo menos:
  - `id`, `title`, `start` (ISO), `end` (ISO), `backgroundColor`, `borderColor`, `textColor`, `status`, `cliente`, `servico`, `profissional`, `valor` (float).
  - O front usa: `fetch('/agendamentos/api/?mes=${m}&ano=${y}')` em `templates/agendamentos/calendario.html`.
- Detecção de conflito ao criar agendamento — mantenha este padrão:

```python
conflito = Agendamento.objects.filter(
    empresa=empresa,
    profissional=profissional,
    data_hora_inicio__lt=data_fim,
    data_hora_fim__gt=data_hora
).exists()
```

- Feedback ao usuário usa `django.contrib.messages`; templates podem esperar `form_values` para re-popular campos após erro (ver `agendamentos/views.py`).
- Verifique restrições de modelos (`unique_together`) antes de criar objetos duplicados (ex.: `('empresa','nome')`).

## Tarefas em background e agendamento
- `financeiro.scheduler.start_scheduler()` registra um job de 15 minutos que chama `processar_agendamentos_concluidos` (iniciado em dev quando `DEBUG=True`).
- Em produção, prefira um cron externo (`scripts/cron-jobs.sh`) para executar `processar_agendamentos_concluidos` periodicamente.
- Se criar tarefas com Celery, siga o padrão em `config/celery.py` e adicione `tasks.py` no app apropriado.

## API e Autenticação
- DRF está configurado para autenticação por sessão e `IsAuthenticated` por padrão (`config/settings.py`). Chamadas do navegador dependem de cookies de sessão.

## Onde procurar a lógica relacionada
- Ciclo de agendamentos e API JSON: `agendamentos/views.py`, `agendamentos/models.py`
- Processamento financeiro e agendador: `financeiro/management/commands/processar_agendamentos_concluidos.py`, `financeiro/scheduler.py`, `financeiro/apps.py`
- Modelos de empresa/serviço/profissional: `empresas/models.py`
- Usuário custom e tenant: `core/models.py` (`Usuario.empresa`)

## Checklist de PR / alterações (agentes)
- Adicione migrations ao alterar modelos: `python manage.py makemigrations`.
- Rode `python manage.py test` ao mudar lógica crítica.
- Para mudanças no financeiro/agendamentos, execute `python manage.py processar_agendamentos_concluidos --dry-run` antes de deploy.
- Certifique-se de que todas as queries que retornam ou alteram objetos multitenant filtram por `empresa`.
- Atualize templates e JavaScript quando o formato da API mudar (procure por `templates/agendamentos`).

---

Se quiser, posso expandir com exemplos de PR, padrões de testes ou um `AGENT.md` com tarefas automáticas comuns — diga qual seção você quer detalhar.
