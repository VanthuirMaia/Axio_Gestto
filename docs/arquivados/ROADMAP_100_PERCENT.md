# 🎯 Roadmap para 100% Produção - Axio Gestto

## 📊 Status Atual: **75%** ✅

---

## 🔴 CRÍTICO - Bloqueadores para Produção (25% restantes)

### 1. Sistema de Notificações (10%)
**Status:** ❌ Não implementado
**Impacto:** 🔴 Alto - Clientes esquecem agendamentos

**Implementar:**

#### A) Email Automático
```python
# agendamentos/tasks.py (Celery)
from celery import shared_task
from django.core.mail import send_mail
from datetime import datetime, timedelta
from .models import Agendamento

@shared_task
def enviar_lembretes_agendamentos():
    """
    Roda a cada hora.
    Envia email para agendamentos nas próximas 24h
    """
    agora = datetime.now()
    amanha = agora + timedelta(hours=24)

    agendamentos = Agendamento.objects.filter(
        data_hora_inicio__gte=agora,
        data_hora_inicio__lte=amanha,
        status='confirmado',
        lembrete_enviado=False  # novo campo
    )

    for ag in agendamentos:
        send_mail(
            subject=f'Lembrete: Agendamento {ag.servico.nome}',
            message=f'''
            Olá {ag.cliente.nome}!

            Lembrete do seu agendamento:

            📅 Data: {ag.data_hora_inicio.strftime("%d/%m/%Y às %H:%M")}
            ✂️ Serviço: {ag.servico.nome}
            👤 Profissional: {ag.profissional.nome}
            📍 Local: {ag.empresa.endereco}

            Até lá!
            {ag.empresa.nome}
            ''',
            from_email='noreply@axiogesto.com',
            recipient_list=[ag.cliente.email],
        )

        ag.lembrete_enviado = True
        ag.save()
```

**Adicionar ao models.py:**
```python
class Agendamento(models.Model):
    # ... campos existentes ...
    lembrete_enviado = models.BooleanField(default=False)
```

**Configurar Celery Beat:**
```python
# config/settings.py
from celery.schedules import crontab

CELERY_BEAT_SCHEDULE = {
    'enviar-lembretes': {
        'task': 'agendamentos.tasks.enviar_lembretes_agendamentos',
        'schedule': crontab(minute=0),  # A cada hora
    },
}
```

#### B) WhatsApp via n8n
```json
// Workflow n8n (Cron diário 8h)
{
  "nodes": [
    {
      "name": "Cron - 8h diário",
      "type": "n8n-nodes-base.cron",
      "parameters": {
        "triggerTimes": {
          "item": [
            {
              "hour": 8,
              "minute": 0
            }
          ]
        }
      }
    },
    {
      "name": "Buscar agendamentos do dia",
      "type": "n8n-nodes-base.httpRequest",
      "parameters": {
        "url": "https://seu-dominio.com/agendamentos/api/hoje/",
        "authentication": "headerAuth"
      }
    },
    {
      "name": "Para cada agendamento",
      "type": "n8n-nodes-base.splitInBatches"
    },
    {
      "name": "Enviar WhatsApp",
      "type": "n8n-nodes-base.whatsapp",
      "parameters": {
        "message": "Olá {{$json.cliente}}! Lembrete: você tem {{$json.servico}} às {{$json.hora}} hoje com {{$json.profissional}}. Até lá! 😊"
      }
    }
  ]
}
```

**Criar endpoint para agendamentos do dia:**
```python
# agendamentos/views.py
@login_required
def agendamentos_hoje(request):
    """API para n8n buscar agendamentos do dia"""
    empresa = request.user.empresa
    hoje = datetime.now().date()

    agendamentos = Agendamento.objects.filter(
        empresa=empresa,
        data_hora_inicio__date=hoje,
        status='confirmado'
    ).select_related('cliente', 'servico', 'profissional')

    dados = [{
        'cliente': ag.cliente.nome,
        'telefone': ag.cliente.telefone,
        'servico': ag.servico.nome,
        'profissional': ag.profissional.nome,
        'hora': ag.data_hora_inicio.strftime('%H:%M'),
    } for ag in agendamentos]

    return JsonResponse(dados, safe=False)
```

**Estimativa:** 8-12 horas de desenvolvimento

---

### 2. Eventos Recorrentes (5%)
**Status:** ❌ Não implementado
**Impacto:** 🟡 Médio - Dificulta agendamentos fixos

**Implementar:**

#### Model para Recorrência
```python
# agendamentos/models.py
class AgendamentoRecorrente(models.Model):
    FREQUENCIA_CHOICES = [
        ('diaria', 'Diária'),
        ('semanal', 'Semanal'),
        ('mensal', 'Mensal'),
    ]

    DIAS_SEMANA_CHOICES = [
        (0, 'Segunda'),
        (1, 'Terça'),
        (2, 'Quarta'),
        (3, 'Quinta'),
        (4, 'Sexta'),
        (5, 'Sábado'),
        (6, 'Domingo'),
    ]

    empresa = models.ForeignKey('empresas.Empresa', on_delete=models.CASCADE)
    cliente = models.ForeignKey('clientes.Cliente', on_delete=models.CASCADE)
    servico = models.ForeignKey('empresas.Servico', on_delete=models.CASCADE)
    profissional = models.ForeignKey('empresas.Profissional', on_delete=models.SET_NULL, null=True)

    # Recorrência
    frequencia = models.CharField(max_length=20, choices=FREQUENCIA_CHOICES)
    dias_semana = models.JSONField(default=list)  # [0, 2, 4] = Seg, Qua, Sex
    hora_inicio = models.TimeField()

    # Período
    data_inicio = models.DateField()
    data_fim = models.DateField(null=True, blank=True)  # null = infinito

    ativo = models.BooleanField(default=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.cliente} - {self.servico} ({self.get_frequencia_display()})"
```

#### Task Celery para Gerar Agendamentos
```python
# agendamentos/tasks.py
@shared_task
def gerar_agendamentos_recorrentes():
    """
    Roda diariamente às 00:00
    Gera agendamentos para os próximos 30 dias
    """
    from datetime import datetime, timedelta
    from .models import AgendamentoRecorrente, Agendamento

    hoje = datetime.now().date()
    limite = hoje + timedelta(days=30)

    recorrencias = AgendamentoRecorrente.objects.filter(ativo=True)

    for rec in recorrencias:
        # Gerar datas baseado na frequência
        datas = []

        if rec.frequencia == 'diaria':
            data = rec.data_inicio
            while data <= limite:
                if data >= hoje:
                    datas.append(data)
                data += timedelta(days=1)

        elif rec.frequencia == 'semanal':
            data = rec.data_inicio
            while data <= limite:
                if data >= hoje and data.weekday() in rec.dias_semana:
                    datas.append(data)
                data += timedelta(days=1)

        # Criar agendamentos se não existirem
        for data in datas:
            data_hora = datetime.combine(data, rec.hora_inicio)

            # Verificar se já existe
            existe = Agendamento.objects.filter(
                empresa=rec.empresa,
                cliente=rec.cliente,
                data_hora_inicio=data_hora
            ).exists()

            if not existe:
                Agendamento.objects.create(
                    empresa=rec.empresa,
                    cliente=rec.cliente,
                    servico=rec.servico,
                    profissional=rec.profissional,
                    data_hora_inicio=data_hora,
                    data_hora_fim=data_hora + timedelta(minutes=rec.servico.duracao_minutos),
                    status='confirmado',
                    valor_cobrado=rec.servico.preco,
                    notas=f'Agendamento recorrente gerado automaticamente'
                )
```

**Estimativa:** 12-16 horas de desenvolvimento

---

### 3. SSL Produção (2%)
**Status:** ⚠️ Certificado auto-assinado (dev only)
**Impacto:** 🔴 Crítico - Navegadores bloqueiam

**Implementar:**

```bash
# 1. Instalar Certbot
docker run -it --rm \
  -v ./certbot/conf:/etc/letsencrypt \
  -v ./certbot/www:/var/www/certbot \
  certbot/certbot certonly --webroot \
  -w /var/www/certbot \
  -d seu-dominio.com \
  -d www.seu-dominio.com \
  --email seu-email@gmail.com \
  --agree-tos

# 2. Copiar certificados para Nginx
cp certbot/conf/live/seu-dominio.com/fullchain.pem nginx/certs/cert.pem
cp certbot/conf/live/seu-dominio.com/privkey.pem nginx/certs/key.pem

# 3. Restart Nginx
docker-compose restart nginx

# 4. Configurar renovação automática (crontab)
0 0 * * * docker run --rm -v ./certbot/conf:/etc/letsencrypt certbot/certbot renew && docker-compose restart nginx
```

**Estimativa:** 2-3 horas

---

### 4. Confirmação de Clientes (3%)
**Status:** ❌ Não implementado
**Impacto:** 🟡 Médio - Aumenta no-show

**Implementar:**

#### A) Botão de Confirmação
```python
# agendamentos/views.py
@require_http_methods(["POST"])
def confirmar_agendamento_publico(request, codigo):
    """
    Link público: /agendamentos/confirmar/A3B9C2/
    Cliente clica no link do WhatsApp/Email
    """
    agendamento = get_object_or_404(
        Agendamento,
        notas__contains=codigo,
        status='pendente'
    )

    agendamento.status = 'confirmado'
    agendamento.save()

    return render(request, 'agendamentos/confirmado.html', {
        'agendamento': agendamento
    })
```

#### B) Link de Confirmação Automático
```python
# Modificar agendamentos/bot_api.py
def processar_agendamento(empresa, telefone, dados, log):
    # ... código existente ...

    # Gerar link de confirmação
    link_confirmacao = f"https://seu-dominio.com/agendamentos/confirmar/{codigo}/"

    return {
        'sucesso': True,
        'mensagem': f'''✅ Agendamento criado!

📅 Serviço: {servico.nome}
👤 Profissional: {profissional.nome}
🕐 Data: {data_hora_inicio.strftime("%d/%m/%Y às %H:%M")}
💰 Valor: R$ {servico.preco}
📝 Código: {codigo}

🔗 Confirmar presença: {link_confirmacao}

Para cancelar: CANCELAR {codigo}''',
        'dados': {
            'link_confirmacao': link_confirmacao,
            ...
        }
    }
```

**Estimativa:** 4-6 horas

---

### 5. Backup Automático (3%)
**Status:** ❌ Não implementado
**Impacto:** 🔴 Crítico - Perda de dados

**Implementar:**

```bash
# scripts/backup.sh
#!/bin/bash

BACKUP_DIR="/var/backups/axio_gestto"
DATE=$(date +%Y%m%d_%H%M%S)
RETENTION_DAYS=30

mkdir -p $BACKUP_DIR

# Backup PostgreSQL
docker exec gestao_db pg_dump -U postgres gestao_negocios | gzip > $BACKUP_DIR/db_$DATE.sql.gz

# Backup arquivos de mídia
tar -czf $BACKUP_DIR/media_$DATE.tar.gz -C /caminho/para/axio_gestto media/

# Limpar backups antigos
find $BACKUP_DIR -name "*.gz" -mtime +$RETENTION_DAYS -delete

# Enviar para cloud (opcional)
# aws s3 cp $BACKUP_DIR/db_$DATE.sql.gz s3://seu-bucket/backups/
```

**Crontab (diário às 2h):**
```bash
0 2 * * * /caminho/para/scripts/backup.sh
```

**Estimativa:** 3-4 horas

---

### 6. Validação de Dados (2%)
**Status:** ⚠️ Parcial
**Impacto:** 🟡 Médio - Dados inconsistentes

**Implementar:**

```python
# clientes/models.py
from django.core.validators import RegexValidator

class Cliente(models.Model):
    # ... campos existentes ...

    cpf = models.CharField(
        max_length=11,
        blank=True,
        validators=[
            RegexValidator(
                regex=r'^\d{11}$',
                message='CPF deve conter 11 dígitos'
            )
        ]
    )

    telefone = models.CharField(
        max_length=15,
        validators=[
            RegexValidator(
                regex=r'^(\+55)?[1-9]{2}9?\d{8}$',
                message='Telefone inválido. Use formato: 11999998888'
            )
        ]
    )

    email = models.EmailField(blank=True)

    def clean(self):
        """Validação customizada"""
        from django.core.exceptions import ValidationError

        # Validar CPF (algoritmo)
        if self.cpf and not self.validar_cpf(self.cpf):
            raise ValidationError({'cpf': 'CPF inválido'})

    @staticmethod
    def validar_cpf(cpf):
        """Valida CPF usando algoritmo oficial"""
        # Implementar algoritmo de validação
        # https://www.macoratti.net/alg_cpf.htm
        pass
```

**Estimativa:** 4-6 horas

---

## 🟡 IMPORTANTE - Melhorias de Produção (extras)

### 7. Arrastar e Soltar no Calendário (5%)
**Status:** ❌ Não implementado
**Impacto:** 🟢 Baixo - UX melhor

**Implementar:**

```javascript
// templates/agendamentos/calendario.html
const calendar = new FullCalendar.Calendar(calendarEl, {
    // ... config existente ...

    editable: true,  // ✅ Habilitar edição

    eventDrop(info) {
        // Evento arrastado para nova data/hora
        const novaData = info.event.start;

        fetch(`/agendamentos/reagendar/${info.event.id}/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({
                nova_data_hora: novaData.toISOString()
            })
        })
        .then(response => {
            if (!response.ok) {
                info.revert();  // Reverter se falhar
                alert('Erro ao reagendar. Horário pode estar ocupado.');
            }
        });
    },

    eventResize(info) {
        // Evento redimensionado (mudar duração)
        const novaDataFim = info.event.end;

        fetch(`/agendamentos/alterar-duracao/${info.event.id}/`, {
            method: 'POST',
            // ...
        });
    }
});
```

**Backend:**
```python
# agendamentos/views.py
@login_required
@require_http_methods(["POST"])
def reagendar(request, id):
    import json
    agendamento = get_object_or_404(Agendamento, id=id, empresa=request.user.empresa)

    dados = json.loads(request.body)
    nova_data_hora = parser.parse(dados['nova_data_hora'])

    # Calcular nova data fim
    duracao = agendamento.data_hora_fim - agendamento.data_hora_inicio
    nova_data_fim = nova_data_hora + duracao

    # Verificar conflito
    conflito = Agendamento.objects.filter(
        empresa=agendamento.empresa,
        profissional=agendamento.profissional,
        data_hora_inicio__lt=nova_data_fim,
        data_hora_fim__gt=nova_data_hora
    ).exclude(id=agendamento.id).exists()

    if conflito:
        return JsonResponse({'erro': 'Horário ocupado'}, status=400)

    agendamento.data_hora_inicio = nova_data_hora
    agendamento.data_hora_fim = nova_data_fim
    agendamento.save()

    return JsonResponse({'sucesso': True})
```

**Estimativa:** 6-8 horas

---

### 8. PWA (Progressive Web App) (3%)
**Status:** ❌ Não implementado
**Impacto:** 🟢 Baixo - Melhor mobile

**Implementar:**

```json
// static/manifest.json
{
  "name": "Axio Gestto",
  "short_name": "Gestto",
  "description": "Sistema de Gestão de Agendamentos",
  "start_url": "/",
  "display": "standalone",
  "background_color": "#ffffff",
  "theme_color": "#0d6efd",
  "icons": [
    {
      "src": "/static/icons/icon-192.png",
      "sizes": "192x192",
      "type": "image/png"
    },
    {
      "src": "/static/icons/icon-512.png",
      "sizes": "512x512",
      "type": "image/png"
    }
  ]
}
```

```javascript
// static/js/service-worker.js
self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open('gestto-v1').then((cache) => {
      return cache.addAll([
        '/',
        '/static/css/style.css',
        '/static/js/main.js',
      ]);
    })
  );
});

self.addEventListener('fetch', (event) => {
  event.respondWith(
    caches.match(event.request).then((response) => {
      return response || fetch(event.request);
    })
  );
});
```

```html
<!-- templates/base.html -->
<head>
    <!-- ... -->
    <link rel="manifest" href="{% static 'manifest.json' %}">
    <meta name="theme-color" content="#0d6efd">
</head>
```

**Estimativa:** 4-6 horas

---

### 9. Permissões Granulares (4%)
**Status:** ⚠️ Apenas login_required
**Impacto:** 🟡 Médio - Segurança

**Implementar:**

```python
# core/models.py
class Usuario(AbstractUser):
    # ... campos existentes ...

    TIPO_USUARIO = [
        ('admin', 'Administrador'),
        ('profissional', 'Profissional'),
        ('recepcionista', 'Recepcionista'),
    ]

    tipo = models.CharField(max_length=20, choices=TIPO_USUARIO, default='admin')
    profissional = models.ForeignKey(
        'empresas.Profissional',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text='Vincula usuário a um profissional'
    )
```

```python
# core/decorators.py
from functools import wraps
from django.http import HttpResponseForbidden

def admin_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if request.user.tipo != 'admin':
            return HttpResponseForbidden('Apenas administradores podem acessar.')
        return view_func(request, *args, **kwargs)
    return wrapper

def profissional_ou_admin(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if request.user.tipo not in ['admin', 'profissional']:
            return HttpResponseForbidden()
        return view_func(request, *args, **kwargs)
    return wrapper
```

**Uso:**
```python
# agendamentos/views.py
@login_required
@admin_required
def deletar_agendamento(request, id):
    # Apenas admin pode deletar
    pass

@login_required
@profissional_ou_admin
def editar_agendamento(request, id):
    # Profissional pode editar seus próprios agendamentos
    agendamento = get_object_or_404(Agendamento, id=id)

    # Se for profissional, só pode editar seus agendamentos
    if request.user.tipo == 'profissional':
        if agendamento.profissional != request.user.profissional:
            return HttpResponseForbidden()

    # ...
```

**Estimativa:** 8-10 horas

---

### 10. Dashboard Avançado (5%)
**Status:** ⚠️ Básico
**Impacto:** 🟢 Baixo - Analytics

**Implementar:**

```python
# dashboard/views.py
@login_required
def dashboard_view(request):
    empresa = request.user.empresa
    hoje = datetime.now().date()
    mes_atual = hoje.month
    ano_atual = hoje.year

    # Métricas do mês
    agendamentos_mes = Agendamento.objects.filter(
        empresa=empresa,
        data_hora_inicio__month=mes_atual,
        data_hora_inicio__year=ano_atual
    )

    # KPIs
    total_agendamentos = agendamentos_mes.count()
    confirmados = agendamentos_mes.filter(status='confirmado').count()
    cancelados = agendamentos_mes.filter(status='cancelado').count()
    concluidos = agendamentos_mes.filter(status='concluido').count()
    no_show = agendamentos_mes.filter(status='nao_compareceu').count()

    # Receita
    receita_mes = agendamentos_mes.filter(
        status='concluido'
    ).aggregate(total=Sum('valor_cobrado'))['total'] or 0

    # Taxa de conversão
    taxa_conclusao = (concluidos / total_agendamentos * 100) if total_agendamentos > 0 else 0
    taxa_cancelamento = (cancelados / total_agendamentos * 100) if total_agendamentos > 0 else 0
    taxa_no_show = (no_show / total_agendamentos * 100) if total_agendamentos > 0 else 0

    # Top serviços
    top_servicos = agendamentos_mes.values(
        'servico__nome'
    ).annotate(
        quantidade=Count('id'),
        receita=Sum('valor_cobrado')
    ).order_by('-quantidade')[:5]

    # Top profissionais
    top_profissionais = agendamentos_mes.values(
        'profissional__nome'
    ).annotate(
        quantidade=Count('id'),
        receita=Sum('valor_cobrado')
    ).order_by('-quantidade')[:5]

    # Gráfico de agendamentos por dia (últimos 30 dias)
    agendamentos_por_dia = []
    for i in range(30):
        dia = hoje - timedelta(days=i)
        count = Agendamento.objects.filter(
            empresa=empresa,
            data_hora_inicio__date=dia
        ).count()
        agendamentos_por_dia.append({
            'data': dia.strftime('%d/%m'),
            'quantidade': count
        })

    context = {
        'total_agendamentos': total_agendamentos,
        'confirmados': confirmados,
        'cancelados': cancelados,
        'concluidos': concluidos,
        'no_show': no_show,
        'receita_mes': receita_mes,
        'taxa_conclusao': round(taxa_conclusao, 1),
        'taxa_cancelamento': round(taxa_cancelamento, 1),
        'taxa_no_show': round(taxa_no_show, 1),
        'top_servicos': top_servicos,
        'top_profissionais': top_profissionais,
        'agendamentos_por_dia': list(reversed(agendamentos_por_dia)),
    }

    return render(request, 'dashboard/dashboard.html', context)
```

**Estimativa:** 10-12 horas

---

## 🟢 OPCIONAL - Nice to Have

### 11. Import/Export ICS (2%)
Para migração do Google Calendar

### 12. Multi-idioma (3%)
i18n para PT/EN/ES

### 13. Temas Customizáveis (2%)
Modo escuro, cores da empresa

### 14. Relatórios PDF (3%)
Exportar relatórios em PDF

### 15. Integração Pagamentos (5%)
Stripe, Mercado Pago, PIX

---

## 📊 Resumo Executivo

### Status Atual: 75%
```
████████████████████░░░░░ 75%
```

### Para chegar a 100%:

| Prioridade | Item | Esforço | Impacto |
|------------|------|---------|---------|
| 🔴 **CRÍTICO** | Notificações | 8-12h | Alto |
| 🔴 **CRÍTICO** | SSL Produção | 2-3h | Crítico |
| 🔴 **CRÍTICO** | Backup Automático | 3-4h | Crítico |
| 🟡 **ALTA** | Eventos Recorrentes | 12-16h | Médio |
| 🟡 **ALTA** | Confirmação Clientes | 4-6h | Médio |
| 🟡 **ALTA** | Validação de Dados | 4-6h | Médio |
| 🟢 **MÉDIA** | Arrastar/Soltar | 6-8h | Baixo |
| 🟢 **MÉDIA** | PWA | 4-6h | Baixo |
| 🟢 **MÉDIA** | Permissões | 8-10h | Médio |
| 🟢 **MÉDIA** | Dashboard Avançado | 10-12h | Baixo |

**Total Estimado:** 61-83 horas (~2 semanas de trabalho)

---

## 🎯 Plano de Ação Sugerido

### Semana 1 (Crítico):
- ✅ Dia 1-2: SSL Produção (2-3h)
- ✅ Dia 2-3: Backup Automático (3-4h)
- ✅ Dia 3-5: Sistema de Notificações (8-12h)

**Ao final:** Sistema seguro e usável em produção (90%)

### Semana 2 (Melhorias):
- ✅ Dia 1-3: Eventos Recorrentes (12-16h)
- ✅ Dia 4: Confirmação de Clientes (4-6h)
- ✅ Dia 5: Validação de Dados (4-6h)

**Ao final:** Sistema completo e robusto (100%)

### Fase 3 (Opcional):
- Arrastar/Soltar
- PWA
- Permissões
- Dashboard Avançado

---

## 🚀 Atalho para 90% Rapidamente

Se você quer subir **AGORA** com 90% de funcionalidade:

### Fazer HOJE (4-6 horas):
1. ✅ Configurar SSL Let's Encrypt (2h)
2. ✅ Configurar backup diário (1h)
3. ✅ Criar workflow n8n para lembretes WhatsApp (2h)

### Fazer SEMANA 1 (20 horas):
4. ✅ Implementar confirmação de clientes (4h)
5. ✅ Validação de CPF/telefone (4h)
6. ✅ Sistema de notificações email (8h)
7. ✅ Testes em produção (4h)

**Resultado:** Sistema 90% pronto, usável em produção com confiança!

---

## ✅ Conclusão

**Atual:** Sistema está 75% pronto
**Usável em produção?** ✅ SIM (com workarounds)
**100% profissional?** ⏳ Faltam 2 semanas de trabalho

**Recomendação:**
1. Suba AGORA em produção (75% é suficiente)
2. Implemente notificações via n8n (workaround)
3. Desenvolva os 25% restantes gradualmente

**O sistema JÁ É MELHOR que Google Calendar para negócios!** 🚀
