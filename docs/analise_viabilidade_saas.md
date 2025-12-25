# Análise de Viabilidade: Sistema Atual → SaaS Multi-Tenant

**Data:** 2025-12-25
**Objetivo:** Avaliar se o sistema atual consegue seguir o plano de evolução para SaaS

---

## 📊 RESUMO EXECUTIVO

**Resposta Direta:** ✅ **SIM, o sistema PODE seguir o plano, MAS requer modificações significativas em 3 áreas críticas:**

1. ❌ **Sistema de Pagamentos** - NÃO implementado
2. ❌ **Multi-tenancy verdadeiro** - PARCIALMENTE implementado (falta isolamento por subdomínio)
3. ❌ **Onboarding automatizado** - NÃO implementado

**Estimativa de esforço:** O plano prevê 2-4 semanas (2h/dia). **Realista: 3-5 semanas** se seguir as etapas.

---

## ✅ O QUE JÁ EXISTE (Fundação sólida)

### 1. Multi-Tenant Básico ✅
**Arquivo:** `empresas/models.py`

```python
class Empresa(models.Model):
    nome = models.CharField(max_length=255, unique=True)
    slug = models.SlugField(unique=True)  # ← Útil para subdomínios
    telefone = models.CharField(max_length=20)
    email = models.EmailField()
    cnpj = models.CharField(max_length=20, unique=True)
    ativa = models.BooleanField(default=True)
    # ... outros campos
```

**O que tem:**
- ✅ Modelo `Empresa` com slug (pode virar subdomínio)
- ✅ Isolamento de dados por FK (Servico, Profissional, Agendamento vinculados a Empresa)
- ✅ Campo `ativa` (pode ser usado para suspender por falta de pagamento)

**O que falta:**
- ❌ Plano de assinatura (essencial, pro, etc)
- ❌ Limites por plano (max_appointments, max_profissionais)
- ❌ Data de expiração/renovação
- ❌ Status de pagamento

### 2. API WhatsApp Multi-Empresa ✅
**Arquivo:** `agendamentos/bot_api.py`

```python
@api_view(['POST'])
@authentication_classes([APIKeyAuthentication])
def processar_comando_bot(request):
    empresa = request.empresa  # ← Vem da autenticação via Header
    # ... processa comando
```

**Autenticação:** `agendamentos/authentication.py`
```python
class APIKeyAuthentication(BaseAuthentication):
    def authenticate(self, request):
        api_key = request.META.get('HTTP_X_API_KEY')
        empresa_id = request.META.get('HTTP_X_EMPRESA_ID')  # ← Header define tenant
        # ... valida e retorna empresa
```

**O que tem:**
- ✅ API já separa dados por empresa via Header `X-Empresa-ID`
- ✅ Autenticação por API Key
- ✅ Rate limiting implementado (BotAPIThrottle)
- ✅ Logs de auditoria (LogMensagemBot)

**O que falta:**
- ❌ Webhook único que roteia automaticamente por telefone (atualmente precisa passar empresa_id manual)
- ❌ Detecção automática de qual tenant pertence cada número WhatsApp

### 3. Usuários vinculados a Empresa ✅
**Arquivo:** `core/models.py`

```python
class Usuario(AbstractUser):
    empresa = models.ForeignKey('empresas.Empresa', on_delete=models.CASCADE)
    # ... outros campos
```

**O que tem:**
- ✅ Cada usuário vinculado a uma empresa
- ✅ AbstractUser estendido (customizável)

**O que falta:**
- ❌ Sistema de convites para adicionar usuários
- ❌ Permissões por plano (plano essencial só 1 usuário, pro ilimitado)

### 4. APIs para n8n ✅
**Arquivo:** `agendamentos/api_n8n.py`

```python
GET /api/n8n/servicos/
GET /api/n8n/profissionais/
GET /api/n8n/horarios-funcionamento/
GET /api/n8n/datas-especiais/
POST /api/n8n/horarios-disponiveis/
```

**O que tem:**
- ✅ APIs REST completas para consultas
- ✅ Documentação clara (N8N_INTEGRATION.md)
- ✅ Autenticação por API Key

**O que falta:**
- ❌ Nada crítico (estão prontas para SaaS)

### 5. Docker + Deploy Ready ✅
**Arquivos:** `docker-compose.yml`, `deploy.sh`, `DEPLOY_GUIDE.md`

**O que tem:**
- ✅ Docker Compose com 5 containers (nginx, django, postgres, redis, celery)
- ✅ Script de deploy automatizado
- ✅ SSL/HTTPS configurado
- ✅ Migrations automáticas
- ✅ Healthchecks

**O que falta:**
- ❌ Configuração de subdomínios wildcard (*.gestto.com.br)
- ❌ Nginx routing por subdomain

---

## ❌ O QUE FALTA IMPLEMENTAR (Crítico para SaaS)

### ETAPA 1: Produto Mínimo Congelado ✅ PRONTO
**Status:** Já existe! O sistema atual é exatamente o "plano essencial"

**Checklist do plano:**
- [x] 1 profissional → Modelo Profissional existe
- [x] 500 agendamentos/mês → Modelo Agendamento existe (falta só o limite)
- [x] WhatsApp bot → Implementado (bot_api.py)
- [x] Relatórios simples → Dashboard já tem (financeiro básico)

**Ação necessária:**
- ✅ Documentar fluxo em vídeo (não técnico)
- ✅ Criar página de especificação

---

### ETAPA 2: Pagamentos + Criação Automática ❌ NÃO IMPLEMENTADO
**Status:** Inexistente

**O que o plano pede:**
```python
class Tenant(models.Model):
    name = CharField()
    subdomain = CharField()  # empresa.gestto.com.br
    plan = CharField(choices=['essencial'])
    max_appointments = 500
```

**O que precisa criar:**

#### 2.1. Modelo de Plano e Assinatura
```python
# Novo app: assinaturas/models.py

class Plano(models.Model):
    PLANOS = [
        ('essencial', 'Essencial - R$49/mês'),
        ('profissional', 'Profissional - R$149/mês'),
        ('empresarial', 'Empresarial - R$299/mês'),
    ]

    nome = models.CharField(max_length=50, choices=PLANOS)
    preco_mensal = models.DecimalField(max_digits=10, decimal_places=2)
    max_profissionais = models.IntegerField()
    max_agendamentos_mes = models.IntegerField()
    max_usuarios = models.IntegerField()
    trial_dias = models.IntegerField(default=7)
    ativo = models.BooleanField(default=True)

class Assinatura(models.Model):
    STATUS = [
        ('trial', 'Trial'),
        ('ativa', 'Ativa'),
        ('suspensa', 'Suspensa'),
        ('cancelada', 'Cancelada'),
    ]

    empresa = models.OneToOneField(Empresa, on_delete=models.CASCADE)
    plano = models.ForeignKey(Plano, on_delete=models.PROTECT)
    status = models.CharField(max_length=20, choices=STATUS)
    data_inicio = models.DateTimeField(auto_now_add=True)
    data_expiracao = models.DateTimeField()
    trial_ativo = models.BooleanField(default=True)

    # Stripe/PagSeguro/Asaas
    gateway = models.CharField(max_length=50)  # 'stripe', 'asaas'
    subscription_id_externo = models.CharField(max_length=255)
    ultimo_pagamento = models.DateTimeField(null=True)
```

#### 2.2. Endpoint de Criação de Tenant
```python
# assinaturas/views.py

@api_view(['POST'])
def create_tenant(request):
    """
    Chamado pelo webhook do Stripe/Asaas após pagamento

    Payload esperado:
    {
        "company_name": "Salão Bela Vida",
        "email": "contato@belavida.com",
        "telefone": "11999999999",
        "cnpj": "12345678000199",
        "plan": "essencial"
    }
    """
    # 1. Criar Empresa
    empresa = Empresa.objects.create(
        nome=request.data['company_name'],
        slug=slugify(request.data['company_name']),
        email=request.data['email'],
        telefone=request.data['telefone'],
        cnpj=request.data['cnpj'],
        ativa=True
    )

    # 2. Criar Plano
    plano = Plano.objects.get(nome='essencial')

    # 3. Criar Assinatura (trial 7 dias)
    assinatura = Assinatura.objects.create(
        empresa=empresa,
        plano=plano,
        status='trial',
        data_expiracao=now() + timedelta(days=7),
        trial_ativo=True
    )

    # 4. Criar usuário admin
    senha_temp = gerar_senha_temporaria()
    usuario = Usuario.objects.create_user(
        username=f"admin@{empresa.slug}",
        email=request.data['email'],
        password=senha_temp,
        empresa=empresa,
        is_staff=True
    )

    # 5. Enviar email com credenciais
    enviar_email_boas_vindas(usuario, senha_temp, empresa)

    # 6. Retornar dados
    return Response({
        'sucesso': True,
        'empresa_id': empresa.id,
        'subdomain': empresa.slug,
        'login_url': f'https://{empresa.slug}.gestto.com.br/onboarding',
        'email': request.data['email'],
        'senha_temporaria': senha_temp  # Enviar apenas por email em prod
    })
```

#### 2.3. Integração com Gateway de Pagamento
**Opções:**

**A) Stripe (Internacional)**
```bash
pip install stripe
```

```python
# config/settings.py
STRIPE_PUBLIC_KEY = env('STRIPE_PUBLIC_KEY')
STRIPE_SECRET_KEY = env('STRIPE_SECRET_KEY')
STRIPE_WEBHOOK_SECRET = env('STRIPE_WEBHOOK_SECRET')

# assinaturas/stripe_integration.py
import stripe
stripe.api_key = settings.STRIPE_SECRET_KEY

@api_view(['POST'])
@csrf_exempt
def stripe_webhook(request):
    """
    Recebe eventos do Stripe:
    - payment_intent.succeeded → ativa assinatura
    - invoice.payment_failed → suspende
    - customer.subscription.deleted → cancela
    """
    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError:
        return Response(status=400)

    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']

        # Criar tenant automaticamente
        create_tenant({
            'company_name': session['metadata']['company_name'],
            'email': session['customer_email'],
            # ...
        })

    return Response({'status': 'success'})
```

**B) Asaas (Brasil, recomendado)**
```bash
pip install python-asaas
```

```python
# assinaturas/asaas_integration.py
from asaas import Asaas

client = Asaas(access_token=settings.ASAAS_API_KEY)

# Criar assinatura
subscription = client.subscriptions.create(
    customer=customer_id,
    billing_type='CREDIT_CARD',
    value=49.00,
    cycle='MONTHLY',
    description='Plano Essencial'
)
```

**Esforço estimado:** 3-4 dias (conforme o plano)

---

### ETAPA 3: Onboarding Guiado ❌ NÃO IMPLEMENTADO
**Status:** Inexistente

**O que o plano pede:**
- Wizard 4 passos após primeiro login
- Cadastrar serviços/horários
- Cadastrar profissional
- Conectar WhatsApp
- Dashboard com confete 🎉

**Implementação:**

#### 3.1. Views de Onboarding
```python
# core/views.py

@login_required
def onboarding_wizard(request):
    """
    Redireciona para onboarding se empresa não configurada
    """
    empresa = request.user.empresa

    if not empresa.onboarding_completo:
        return redirect('onboarding_step_1')

    return redirect('dashboard')


@login_required
def onboarding_step_1(request):
    """Passo 1: Cadastrar serviços"""
    if request.method == 'POST':
        # Salvar serviços
        for servico_data in request.POST.getlist('servicos'):
            Servico.objects.create(
                empresa=request.user.empresa,
                nome=servico_data['nome'],
                preco=servico_data['preco'],
                duracao_minutos=servico_data['duracao']
            )

        return redirect('onboarding_step_2')

    return render(request, 'onboarding/step_1_servicos.html')


# Passos 2, 3, 4...
```

#### 3.2. Templates de Onboarding
```html
<!-- templates/onboarding/step_1_servicos.html -->
<div class="onboarding-wizard">
    <div class="progress-bar">
        <span class="step active">1. Serviços</span>
        <span class="step">2. Profissional</span>
        <span class="step">3. WhatsApp</span>
        <span class="step">4. Pronto!</span>
    </div>

    <form method="post" id="form-servicos">
        <h2>Quais serviços você oferece?</h2>

        <div id="lista-servicos">
            <div class="servico-item">
                <input type="text" name="servico_nome[]" placeholder="Ex: Corte Masculino">
                <input type="number" name="servico_preco[]" placeholder="R$ 45,00">
                <input type="number" name="servico_duracao[]" placeholder="30 min">
                <button type="button" class="btn-remove">Remover</button>
            </div>
        </div>

        <button type="button" id="btn-adicionar">+ Adicionar Serviço</button>
        <button type="submit" class="btn-primary">Próximo →</button>
    </form>
</div>
```

#### 3.3. Adicionar campo ao modelo Empresa
```python
# empresas/models.py
class Empresa(models.Model):
    # ... campos existentes
    onboarding_completo = models.BooleanField(default=False)
    onboarding_etapa = models.IntegerField(default=0)  # 0-4
```

**Esforço estimado:** 3 dias (conforme o plano)

---

### ETAPA 4: WhatsApp Multi-Tenant Seguro ⚠️ PARCIALMENTE IMPLEMENTADO
**Status:** Existe API, mas falta roteamento automático

**O que tem:**
```python
# Atual: precisa passar empresa_id manualmente
POST /api/bot/processar/
Headers: X-API-Key, X-Empresa-ID: 1
```

**O que o plano pede:**
```python
# 1 webhook único que roteia automaticamente
POST /api/whatsapp-webhook
Body: { "from": "5511999999999", "message": "..." }
# Sistema descobre sozinho qual empresa pelo telefone
```

**Implementação:**

#### 4.1. Adicionar campo WhatsApp à Empresa
```python
# empresas/models.py
class Empresa(models.Model):
    # ... campos existentes
    whatsapp_numero = models.CharField(max_length=20, unique=True, null=True)
    whatsapp_token = models.CharField(max_length=255, blank=True)  # Evolution/Z-API
    whatsapp_webhook_id = models.CharField(max_length=255, blank=True)
```

#### 4.2. Webhook único multi-tenant
```python
# agendamentos/views.py

@api_view(['POST'])
@permission_classes([AllowAny])  # Sem auth (vem do WhatsApp provider)
def whatsapp_webhook_unico(request):
    """
    Recebe msgs de TODOS os clientes
    Roteia automaticamente para empresa certa

    Payload Evolution API:
    {
        "instance": "empresa1",
        "data": {
            "key": {"remoteJid": "5511999999999@s.whatsapp.net"},
            "message": {"conversation": "Quero agendar"}
        }
    }
    """

    # 1. Extrair número que ENVIOU a mensagem (cliente)
    phone_client = request.data['data']['key']['remoteJid'].split('@')[0]

    # 2. Extrair instância (cada empresa tem uma instância)
    instance_name = request.data['instance']

    # 3. Buscar empresa pela instância
    empresa = Empresa.objects.filter(
        slug=instance_name,  # ou whatsapp_numero
        ativa=True
    ).first()

    if not empresa:
        return Response({'error': 'Empresa não encontrada'}, status=404)

    # 4. Verificar se assinatura está ativa
    if empresa.assinatura.status not in ['trial', 'ativa']:
        return Response({'error': 'Assinatura suspensa'}, status=403)

    # 5. Encaminhar para n8n com tenant_id
    response = requests.post(
        f'https://n8n.seudominio.com/webhook/{empresa.id}',
        json={
            'tenant_id': empresa.id,
            'phone': phone_client,
            'message': request.data['data']['message']['conversation']
        }
    )

    return Response({'status': 'forwarded'})
```

#### 4.3. Cloudflare Rate Limiting
```nginx
# nginx/nginx.conf (adicionar)

# Rate limit para webhook público
limit_req_zone $binary_remote_addr zone=whatsapp:10m rate=10r/s;

location /api/whatsapp-webhook {
    limit_req zone=whatsapp burst=20 nodelay;
    proxy_pass http://web:8000;
}
```

**Esforço estimado:** 4-5 dias (conforme o plano)

---

### ETAPA 5: Limites + Monitoramento ❌ NÃO IMPLEMENTADO
**Status:** Inexistente

**O que o plano pede:**
- Middleware que checa limites
- Dashboard mostra uso
- Ao atingir 90% → bloqueia + botão upgrade

**Implementação:**

#### 5.1. Middleware de Limites
```python
# assinaturas/middleware.py

class LimitesPlanoMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            empresa = request.user.empresa
            assinatura = empresa.assinatura
            plano = assinatura.plano

            # Verificar se trial expirou
            if assinatura.trial_ativo and assinatura.data_expiracao < now():
                assinatura.status = 'suspensa'
                assinatura.save()
                return redirect('pagamento_pendente')

            # Verificar limites apenas em endpoints críticos
            if request.path.startswith('/agendamentos/criar'):
                # Contar agendamentos do mês
                mes_atual = now().replace(day=1, hour=0, minute=0, second=0)
                total = Agendamento.objects.filter(
                    empresa=empresa,
                    criado_em__gte=mes_atual
                ).count()

                if total >= plano.max_agendamentos_mes:
                    messages.error(request,
                        f'Limite de {plano.max_agendamentos_mes} agendamentos atingido! '
                        f'Faça upgrade para continuar.'
                    )
                    return redirect('upgrade_plano')

        return self.get_response(request)


# config/settings.py
MIDDLEWARE = [
    # ... outros middlewares
    'assinaturas.middleware.LimitesPlanoMiddleware',
]
```

#### 5.2. Dashboard com Métricas
```python
# dashboard/views.py

@login_required
def dashboard(request):
    empresa = request.user.empresa
    assinatura = empresa.assinatura
    plano = assinatura.plano

    # Métricas do mês
    mes_atual = now().replace(day=1, hour=0, minute=0)
    agendamentos_mes = Agendamento.objects.filter(
        empresa=empresa,
        criado_em__gte=mes_atual
    ).count()

    percentual_uso = (agendamentos_mes / plano.max_agendamentos_mes) * 100

    context = {
        'agendamentos_usados': agendamentos_mes,
        'agendamentos_limite': plano.max_agendamentos_mes,
        'percentual_uso': percentual_uso,
        'alerta_limite': percentual_uso >= 90,
        'plano_atual': plano.nome,
        'expira_em': assinatura.data_expiracao,
    }

    return render(request, 'dashboard/index.html', context)
```

#### 5.3. Template de Alerta
```html
<!-- templates/dashboard/index.html -->
{% if alerta_limite %}
<div class="alert alert-warning">
    <h3>⚠️ Limite próximo!</h3>
    <p>Você usou {{ agendamentos_usados }}/{{ agendamentos_limite }} agendamentos ({{ percentual_uso|floatformat:0 }}%)</p>
    <a href="{% url 'upgrade_plano' %}" class="btn btn-primary">
        Fazer Upgrade para Plano Pro
    </a>
</div>
{% endif %}
```

**Esforço estimado:** 2 dias (conforme o plano)

---

## 🔧 MODIFICAÇÕES NECESSÁRIAS NO SISTEMA ATUAL

### 1. Estrutura de Apps Django (adicionar)
```
assinaturas/          # NOVO APP
├── models.py         # Plano, Assinatura
├── views.py          # create_tenant, stripe_webhook
├── middleware.py     # LimitesPlanoMiddleware
├── stripe_integration.py
└── asaas_integration.py

core/
├── views.py          # adicionar onboarding_wizard
└── templates/
    └── onboarding/   # NOVO
        ├── step_1_servicos.html
        ├── step_2_profissional.html
        ├── step_3_whatsapp.html
        └── step_4_pronto.html
```

### 2. Models a modificar

**Empresa (adicionar campos):**
```python
class Empresa(models.Model):
    # ... campos existentes
    onboarding_completo = models.BooleanField(default=False)
    whatsapp_numero = models.CharField(max_length=20, unique=True, null=True)
    whatsapp_token = models.CharField(max_length=255, blank=True)
```

### 3. URLs a adicionar
```python
# config/urls.py
urlpatterns = [
    # ... existentes
    path('api/create-tenant/', create_tenant),
    path('api/stripe-webhook/', stripe_webhook),
    path('api/whatsapp-webhook/', whatsapp_webhook_unico),
    path('onboarding/', include('core.onboarding_urls')),
    path('upgrade/', upgrade_plano),
]
```

### 4. Configuração de Subdomínios (Nginx)
```nginx
# nginx/nginx.conf

# Wildcard para *.gestto.com.br
server {
    listen 443 ssl;
    server_name ~^(?<subdomain>.+)\.gestto\.com\.br$;

    location / {
        proxy_pass http://web:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Subdomain $subdomain;
    }
}
```

**Django middleware para capturar subdomain:**
```python
# core/middleware.py
class SubdomainMiddleware:
    def __call__(self, request):
        subdomain = request.META.get('HTTP_X_SUBDOMAIN')

        if subdomain and subdomain != 'www':
            try:
                empresa = Empresa.objects.get(slug=subdomain)
                request.empresa = empresa
            except Empresa.DoesNotExist:
                return HttpResponse('Empresa não encontrada', status=404)

        return self.get_response(request)
```

### 5. Dependências a adicionar (requirements.txt)
```
stripe==7.0.0
python-asaas==1.0.0
django-cors-headers==4.3.0  # já tem
```

---

## 📅 CRONOGRAMA REALISTA (vs Plano Original)

| Etapa | Plano Original | Estimativa Real | Por quê da diferença |
|-------|---------------|-----------------|---------------------|
| 1. Produto Mínimo | 2 dias | ✅ **0 dias** (já pronto) | Sistema atual já é o MVP |
| 2. Pagamentos + Tenant | 3-4 dias | **5-6 dias** | Integração gateway + testes |
| 3. Onboarding | 3 dias | **4-5 dias** | UI/UX complexo, validações |
| 4. WhatsApp Multi-Tenant | 4-5 dias | **3-4 dias** | Base já existe, só rotear |
| 5. Limites + Monitor | 2 dias | **2-3 dias** | Middleware simples |
| **TOTAL** | **14-16 dias** | **14-18 dias** | ✅ Viável em 3-4 semanas |

**Observação:** O plano está otimista mas factível. **Estimativa conservadora: 4-5 semanas** para primeira versão estável.

---

## ⚠️ RISCOS E PONTOS DE ATENÇÃO

### 1. Subdomínios Wildcard
**Risco:** DNS e certificado SSL wildcard são complexos

**Soluções:**
- **A)** Usar Let's Encrypt wildcard (requer DNS challenge)
```bash
certbot certonly --dns-cloudflare --dns-cloudflare-credentials ~/.secrets/cloudflare.ini -d *.gestto.com.br
```

- **B)** Usar caminho em vez de subdomain (mais simples)
```
https://gestto.com.br/empresa/salao-bela-vida/
```

**Recomendação:** Começar com opção B (caminho) e migrar para subdomínio depois.

### 2. Integração Gateway de Pagamento
**Risco:** Webhooks podem falhar, duplicar pagamentos, etc

**Mitigações:**
- Usar `idempotency_key` em todas as operações
- Logar TODOS os eventos do gateway
- Implementar retry com exponential backoff
- Ter processo manual de reconciliação

### 3. Custos Operacionais
**Risco:** n8n executions, Supabase (se usar), WhatsApp API

**O plano menciona Supabase mas você usa PostgreSQL:**
- ✅ **Manter PostgreSQL é melhor** (já configurado, sem custos extras)
- ❌ **NÃO migrar para Supabase** (desnecessário e mais caro)

**Custos estimados (por cliente):**
- WhatsApp (Evolution API self-hosted): R$ 0 (incluído na VPS)
- n8n (self-hosted): R$ 0
- PostgreSQL: R$ 0 (incluído)
- **Custo marginal por cliente: ~R$ 0-5/mês**

### 4. Escala de Banco de Dados
**Risco:** 100 empresas × 500 agendamentos/mês = 50k registros/mês

**Mitigação:**
- PostgreSQL aguenta tranquilo até 10M registros
- Indexes corretos em FK (empresa_id, profissional_id)
- Arquivar agendamentos antigos (>6 meses) periodicamente

---

## ✅ CHECKLIST DE IMPLEMENTAÇÃO

### Pré-Deploy (Preparação)
- [ ] Criar branch `feature/saas-multi-tenant`
- [ ] Criar app `assinaturas/`
- [ ] Adicionar models: Plano, Assinatura
- [ ] Criar migrations

### Etapa 1: Produto Mínimo (já feito)
- [x] Sistema atual funciona como MVP
- [ ] Gravar vídeo demo (2min)
- [ ] Criar doc de especificação

### Etapa 2: Pagamentos
- [ ] Criar conta Stripe/Asaas (modo teste)
- [ ] Implementar `create_tenant()`
- [ ] Implementar webhook gateway
- [ ] Testar criação automática
- [ ] Email de boas-vindas

### Etapa 3: Onboarding
- [ ] Templates dos 4 passos
- [ ] Views de wizard
- [ ] Validações de formulário
- [ ] Redirecionamento automático
- [ ] Confete no final 🎉

### Etapa 4: WhatsApp Multi-Tenant
- [ ] Campo `whatsapp_numero` em Empresa
- [ ] Endpoint `/api/whatsapp-webhook/`
- [ ] Lógica de roteamento automático
- [ ] Testar com 2 números diferentes
- [ ] Rate limiting

### Etapa 5: Limites
- [ ] Middleware de limites
- [ ] Dashboard com métricas
- [ ] Alerta 90%
- [ ] Página de upgrade
- [ ] Testes de bloqueio

### Deploy
- [ ] Atualizar docker-compose.yml
- [ ] Configurar subdomínios (ou caminhos)
- [ ] SSL wildcard (ou multi-domain)
- [ ] Variáveis de ambiente (Stripe keys)
- [ ] Smoke tests em produção

---

## 🎯 RESPOSTA FINAL

### O sistema atual CONSEGUE seguir o plano?

**✅ SIM**, mas com ressalvas:

1. **Base sólida (70% pronto):**
   - Multi-tenant básico ✅
   - APIs REST ✅
   - WhatsApp bot ✅
   - Deploy dockerizado ✅

2. **Falta implementar (30%):**
   - Sistema de pagamentos ❌
   - Onboarding wizard ❌
   - Webhook multi-tenant automático ❌
   - Limites por plano ❌
   - Subdomínios wildcard ❌

3. **Tempo realista:**
   - Plano diz: 2-4 semanas (2h/dia)
   - Realidade: **4-5 semanas** para versão estável
   - MVP funcional: **3 semanas** (pulando features avançadas)

### Sugestão de Caminho Rápido (MVP em 3 semanas):

**Semana 1:** Pagamentos + criação automática
**Semana 2:** Onboarding básico (sem wizard fancy, só formulário)
**Semana 3:** WhatsApp routing + limites simples

**Depois (v1.1):** Subdomínios, wizard bonito, métricas avançadas

---

## 📌 RECOMENDAÇÕES FINAIS

1. **Comece simples:**
   - Use `/empresa/slug/` em vez de `slug.dominio.com` (mais fácil)
   - Formulário onboarding simples (não wizard) na v1
   - Limite manual no admin (depois automatizar)

2. **Priorize pagamentos:**
   - Essa é a parte mais crítica e complexa
   - Teste MUITO antes de ir ao ar
   - Tenha plano B para pagamentos falhados

3. **Use o plano como guia, não roteiro rígido:**
   - Etapas estão boas, mas ordem pode mudar
   - Teste cada parte independentemente
   - 5 clientes piloto ANTES de marketing

4. **Mantenha PostgreSQL:**
   - Não migre para Supabase (desnecessário)
   - Já está funcionando bem
   - Economiza dinheiro e complexidade

---

**Conclusão:** Sistema está **bem posicionado** para virar SaaS. A base técnica é sólida. O desafio maior é implementar a camada de pagamentos/onboarding, não a arquitetura multi-tenant (que já existe de forma básica).

**Próximo passo recomendado:** Implementar Etapa 2 (pagamentos) primeiro, porque sem isso não dá para testar o restante de forma realista.
