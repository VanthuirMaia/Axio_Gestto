# LIMPEZA AUTOMÁTICA DE LOGS DE ANALYTICS

## Problema
Os logs de analytics (PageView e UserEvent) podem crescer muito e encher o banco de dados.

## Solução Implementada

### 1. Comando Manual
```bash
# Ver o que seria deletado (dry-run)
python manage.py limpar_logs_analytics --dry-run

# Deletar logs com mais de 90 dias (padrão)
python manage.py limpar_logs_analytics

# Deletar logs com mais de 30 dias
python manage.py limpar_logs_analytics --days=30

# Deletar logs com mais de 180 dias (6 meses)
python manage.py limpar_logs_analytics --days=180
```

### 2. Automação via Celery Beat (Recomendado)

Adicione no `config/celery.py`:

```python
from celery.schedules import crontab

app.conf.beat_schedule = {
    # ... outras tarefas ...
    
    'limpar-logs-analytics': {
        'task': 'landing.tasks.limpar_logs_analytics_antigos',
        'schedule': crontab(hour=3, minute=0, day_of_week=0),  # Todo domingo às 3h
    },
}
```

### 3. Cron Manual (Alternativa)

Se não usar Celery, adicione no crontab do servidor:

```bash
# Editar crontab
crontab -e

# Adicionar linha (executa todo domingo às 3h da manhã)
0 3 * * 0 cd /var/www/gestto && docker exec gestto_web python manage.py limpar_logs_analytics --days=90
```

## Recomendações

### Retenção de Dados
- **30 dias**: Para sites com muito tráfego (milhares de acessos/dia)
- **90 dias**: Recomendado para maioria dos casos ✅
- **180 dias**: Se quiser análises de longo prazo
- **365 dias**: Apenas se tiver muito espaço em disco

### Frequência de Limpeza
- **Semanal**: Recomendado (todo domingo de madrugada)
- **Mensal**: Aceitável para sites com pouco tráfego
- **Diária**: Apenas se tiver tráfego MUITO alto

## Monitoramento

### Ver tamanho atual dos logs
```sql
-- No PostgreSQL
SELECT 
    pg_size_pretty(pg_total_relation_size('landing_pageview')) as pageview_size,
    pg_size_pretty(pg_total_relation_size('landing_userevent')) as userevent_size,
    (SELECT COUNT(*) FROM landing_pageview) as pageview_count,
    (SELECT COUNT(*) FROM landing_userevent) as userevent_count;
```

### No Django Admin
Acesse `/admin/landing/pageview/` e `/admin/landing/userevent/` para ver a quantidade de registros.

## Importante

- ✅ Google Analytics mantém os dados indefinidamente (até o limite de retenção configurado)
- ✅ Logs no Django são apenas backup/análise local
- ✅ É seguro deletar logs antigos do Django
- ✅ Sempre faça backup antes de deletar em produção

## Executar Agora (Teste)

```bash
# No servidor
docker exec gestto_web python manage.py limpar_logs_analytics --dry-run --days=90
```

Isso mostrará quantos registros seriam deletados sem deletar nada.
