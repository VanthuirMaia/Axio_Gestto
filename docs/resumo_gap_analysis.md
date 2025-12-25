# Gap Analysis: Sistema Atual → Plano SaaS

## 🎯 Resposta Direta

**SIM, o sistema pode seguir o plano, mas precisa implementar 30% de funcionalidades ausentes.**

---

## 📊 Comparação Rápida

| Feature | Plano Requer | Sistema Atual | Status | Esforço |
|---------|--------------|---------------|---------|---------|
| **Multi-tenant básico** | Empresas separadas | ✅ Modelo Empresa + FK | ✅ PRONTO | 0 dias |
| **API WhatsApp** | Bot responde msgs | ✅ bot_api.py completo | ✅ PRONTO | 0 dias |
| **Agendamentos** | CRUD completo | ✅ Models + views | ✅ PRONTO | 0 dias |
| **Profissionais/Serviços** | Cadastro | ✅ Models prontos | ✅ PRONTO | 0 dias |
| **Deploy Docker** | Container ready | ✅ docker-compose.yml | ✅ PRONTO | 0 dias |
| **Sistema de Pagamentos** | Stripe/Asaas | ❌ Não existe | ❌ FALTA | 5-6 dias |
| **Planos/Assinatura** | Essencial/Pro | ❌ Não existe | ❌ FALTA | 2 dias |
| **Onboarding Wizard** | 4 passos guiados | ❌ Não existe | ❌ FALTA | 4-5 dias |
| **Criação automática tenant** | API create_tenant | ❌ Não existe | ❌ FALTA | 1 dia |
| **Webhook multi-tenant** | 1 webhook → N empresas | ⚠️ Parcial (precisa empresa_id) | ⚠️ AJUSTAR | 3-4 dias |
| **Limites por plano** | 500 agend/mês | ❌ Não existe | ❌ FALTA | 2-3 dias |
| **Monitoramento uso** | Dashboard métricas | ⚠️ Parcial (tem dashboard) | ⚠️ MELHORAR | 1 dia |
| **Subdomínios** | empresa.gestto.com.br | ❌ Não configurado | ❌ FALTA | 2 dias |
| **Upgrade automático** | Botão upgrade plano | ❌ Não existe | ❌ FALTA | 1 dia |

---

## 📈 O que JÁ FUNCIONA (70% pronto)

```
✅ Gestão de Empresas
   └─ Modelo Empresa com slug, CNPJ, etc
   └─ Isolamento de dados por FK
   └─ Campo 'ativa' (suspender por falta pagamento)

✅ API WhatsApp Completa
   └─ POST /api/bot/processar/
   └─ Agendamento via IA
   └─ Cancelamento, consulta, confirmação
   └─ Logs de auditoria (LogMensagemBot)

✅ APIs para n8n
   └─ GET /api/n8n/servicos/
   └─ GET /api/n8n/profissionais/
   └─ POST /api/n8n/horarios-disponiveis/

✅ Sistema Multi-Tenant Básico
   └─ Usuários vinculados a Empresa
   └─ Dados isolados por empresa_id
   └─ Header X-Empresa-ID para identificar tenant

✅ Deploy Production-Ready
   └─ Docker Compose (5 containers)
   └─ Nginx + SSL/HTTPS
   └─ PostgreSQL + Redis
   └─ Celery (tarefas agendadas)
```

---

## ❌ O que FALTA IMPLEMENTAR (30%)

```
❌ Sistema de Pagamentos
   └─ Integração Stripe/Asaas
   └─ Webhooks de pagamento
   └─ Models: Plano, Assinatura
   └─ Status: trial/ativa/suspensa

❌ Onboarding Automatizado
   └─ Wizard 4 passos (serviços → profissional → whatsapp → pronto)
   └─ Templates de onboarding
   └─ Validações de formulário
   └─ Redirecionamento automático

❌ Auto-Provisionamento
   └─ API create_tenant()
   └─ Criação automática após pagamento
   └─ Email com credenciais
   └─ Senha temporária

❌ Limites por Plano
   └─ Middleware que checa max_agendamentos
   └─ Bloqueio ao atingir limite
   └─ Alerta 90% de uso
   └─ Botão "Fazer Upgrade"

❌ Webhook Multi-Tenant Inteligente
   └─ Endpoint único /api/whatsapp-webhook
   └─ Detecta empresa pelo telefone
   └─ Roteia automaticamente sem passar empresa_id

❌ Subdomínios Wildcard
   └─ Nginx config: *.gestto.com.br
   └─ SSL wildcard
   └─ Middleware captura subdomain
   └─ Roteia para empresa correta
```

---

## 🛠️ Código que PRECISA ser escrito

### 1. Novo App: `assinaturas/`

```python
# assinaturas/models.py
class Plano(models.Model):
    nome = models.CharField(choices=['essencial', 'profissional', 'empresarial'])
    preco_mensal = models.DecimalField(max_digits=10, decimal_places=2)
    max_profissionais = models.IntegerField()
    max_agendamentos_mes = models.IntegerField()
    trial_dias = models.IntegerField(default=7)

class Assinatura(models.Model):
    empresa = models.OneToOneField(Empresa, on_delete=models.CASCADE)
    plano = models.ForeignKey(Plano, on_delete=models.PROTECT)
    status = models.CharField(choices=['trial', 'ativa', 'suspensa', 'cancelada'])
    data_expiracao = models.DateTimeField()
    subscription_id_externo = models.CharField()  # Stripe/Asaas ID
```

### 2. Endpoint de Auto-Provisionamento

```python
# assinaturas/views.py
@api_view(['POST'])
def create_tenant(request):
    """
    Chamado pelo webhook Stripe/Asaas após pagamento
    Cria: Empresa → Assinatura → Usuario admin → Envia email
    """
    empresa = Empresa.objects.create(
        nome=request.data['company_name'],
        slug=slugify(request.data['company_name']),
        email=request.data['email'],
        cnpj=request.data['cnpj']
    )

    plano = Plano.objects.get(nome='essencial')

    Assinatura.objects.create(
        empresa=empresa,
        plano=plano,
        status='trial',
        data_expiracao=now() + timedelta(days=7)
    )

    senha_temp = gerar_senha_temporaria()
    Usuario.objects.create_user(
        username=f"admin@{empresa.slug}",
        email=request.data['email'],
        password=senha_temp,
        empresa=empresa
    )

    enviar_email_boas_vindas(...)

    return Response({
        'login_url': f'https://{empresa.slug}.gestto.com.br/onboarding'
    })
```

### 3. Webhook Stripe/Asaas

```python
# assinaturas/stripe_integration.py
@api_view(['POST'])
@csrf_exempt
def stripe_webhook(request):
    event = stripe.Webhook.construct_event(...)

    if event['type'] == 'checkout.session.completed':
        # Cliente pagou → criar tenant
        create_tenant(session['metadata'])

    elif event['type'] == 'invoice.payment_failed':
        # Suspender assinatura
        assinatura.status = 'suspensa'
        assinatura.save()

    return Response({'status': 'success'})
```

### 4. Onboarding Wizard

```python
# core/views.py
@login_required
def onboarding_step_1(request):
    """Passo 1: Cadastrar serviços"""
    if request.method == 'POST':
        # Salvar serviços
        for s in request.POST.getlist('servicos'):
            Servico.objects.create(empresa=request.user.empresa, ...)
        return redirect('onboarding_step_2')

    return render(request, 'onboarding/step_1_servicos.html')

# Similar para steps 2, 3, 4
```

### 5. Middleware de Limites

```python
# assinaturas/middleware.py
class LimitesPlanoMiddleware:
    def __call__(self, request):
        if request.path.startswith('/agendamentos/criar'):
            empresa = request.user.empresa
            plano = empresa.assinatura.plano

            total = Agendamento.objects.filter(
                empresa=empresa,
                criado_em__gte=inicio_mes
            ).count()

            if total >= plano.max_agendamentos_mes:
                return redirect('upgrade_plano')

        return self.get_response(request)
```

### 6. Webhook WhatsApp Multi-Tenant

```python
# agendamentos/views.py
@api_view(['POST'])
def whatsapp_webhook_unico(request):
    """
    Recebe msgs de TODOS clientes
    Descobre empresa pelo telefone/instância
    """
    instance_name = request.data['instance']  # "salao-bela-vida"
    phone = request.data['data']['key']['remoteJid']

    empresa = Empresa.objects.get(slug=instance_name)

    # Verificar se assinatura ativa
    if empresa.assinatura.status not in ['trial', 'ativa']:
        return Response({'error': 'Assinatura suspensa'}, status=403)

    # Encaminhar para n8n com tenant_id
    requests.post(
        f'https://n8n.com/webhook/{empresa.id}',
        json={'tenant_id': empresa.id, 'phone': phone, ...}
    )
```

---

## ⏱️ Cronograma Realista

| Semana | Tarefas | Dias |
|--------|---------|------|
| **Semana 1** | Models (Plano/Assinatura) + Migrations | 1 dia |
|  | Integração Stripe/Asaas (modo teste) | 3 dias |
|  | Endpoint create_tenant + webhooks | 2 dias |
| **Semana 2** | Templates onboarding (4 passos) | 2 dias |
|  | Views de wizard + validações | 2 dias |
|  | Email boas-vindas + senha temporária | 1 dia |
| **Semana 3** | Webhook WhatsApp multi-tenant | 2 dias |
|  | Middleware de limites | 1 dia |
|  | Dashboard com métricas uso | 1 dia |
|  | Página upgrade plano | 1 dia |
| **Semana 4** | Configurar subdomínios (nginx) | 1 dia |
|  | SSL wildcard (Let's Encrypt) | 1 dia |
|  | Testes integração completa | 2 dias |
|  | Deploy produção + smoke tests | 1 dia |

**Total:** 21 dias úteis = **4-5 semanas** (considerando imprevistos)

---

## 🎯 Alternativa RÁPIDA (MVP em 2-3 semanas)

Se quiser lançar mais rápido, **simplifique**:

### Versão Simplificada (não seguir plano 100%):

1. **SEM subdomínios** → usar `/empresa/slug/` (mais fácil)
2. **SEM wizard fancy** → formulário simples de cadastro
3. **SEM upgrade automático** → fazer upgrade manual via admin
4. **Stripe em modo manual** → gerar link de pagamento na mão

**Ganho:** MVP em **15 dias** (3 semanas)

**Trade-off:** Menos automatizado, mas funcional

---

## 📋 Checklist de Decisão

Antes de começar, decida:

- [ ] Usar subdomínios (`empresa.gestto.com.br`) ou caminhos (`/empresa/slug/`)?
- [ ] Stripe (internacional) ou Asaas (Brasil)?
- [ ] Wizard bonito ou formulário simples?
- [ ] Automatizar 100% ou aceitar processos manuais no início?
- [ ] Manter PostgreSQL ou migrar Supabase? (RECOMENDO manter PostgreSQL)

---

## ⚠️ Principais Riscos

1. **Integração pagamentos** → Parte mais complexa, teste MUITO
2. **SSL wildcard** → Requer DNS challenge, pode dar trabalho
3. **Webhooks falharem** → Ter retry e logs robustos
4. **Limites não bloquear** → Clientes passarem do plano sem pagar

---

## ✅ Conclusão

**Sistema atual:** Base sólida (70% pronto)

**Para virar SaaS:** Implementar camada de assinaturas/pagamentos (30%)

**Viável?** ✅ SIM, em 4-5 semanas seguindo o plano

**Recomendação:**
1. Começar pela Etapa 2 (pagamentos) - é a fundação
2. Simplificar onboarding na v1 (formulário básico)
3. Deixar subdomínios para v1.1
4. Focar em funcionar bem antes de ficar bonito

**MVP simplificado:** Viável em 3 semanas se cortar features avançadas
