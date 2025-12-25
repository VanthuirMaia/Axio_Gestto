# Roadmap de Implementação SaaS
## Da Versão Atual → SaaS Multi-Tenant

**Objetivo:** Transformar Gestto single-tenant em plataforma SaaS self-service

**Prazo:** 4-5 semanas (2h/dia) ou 3 semanas full-time

---

## 🎯 FASE 0: Preparação (1 dia)

### Tarefas
- [ ] Criar branch `feature/saas-transformation`
- [ ] Fazer backup completo do banco de dados
- [ ] Documentar estado atual (screenshots, dados de teste)
- [ ] Definir domínio (gestto.com.br ou outro)
- [ ] Criar conta Stripe/Asaas (modo sandbox)
- [ ] Configurar ambiente de staging

### Comandos
```bash
# Criar branch
git checkout -b feature/saas-transformation

# Backup
docker-compose exec db pg_dump -U postgres gestao_negocios > backup_pre_saas.sql

# Criar ambiente staging
cp .env .env.staging
# Editar .env.staging com dados de teste
```

---

## 📦 FASE 1: Models e Infraestrutura (2-3 dias)

### Dia 1: Criar app de assinaturas

**Tarefas:**
- [ ] Criar app `assinaturas/`
- [ ] Implementar models: `Plano`, `Assinatura`
- [ ] Adicionar campos em `Empresa`: `onboarding_completo`, `whatsapp_numero`
- [ ] Criar migrations
- [ ] Popular planos iniciais (fixtures)

**Código:**
```bash
# Criar app
python manage.py startapp assinaturas

# Adicionar em INSTALLED_APPS
# config/settings.py
INSTALLED_APPS = [
    # ...
    'assinaturas',
]
```

**Models:**
```python
# assinaturas/models.py
from django.db import models
from django.utils.timezone import now, timedelta

class Plano(models.Model):
    PLANOS = [
        ('essencial', 'Essencial'),
        ('profissional', 'Profissional'),
        ('empresarial', 'Empresarial'),
    ]

    nome = models.CharField(max_length=50, choices=PLANOS, unique=True)
    descricao = models.TextField()
    preco_mensal = models.DecimalField(max_digits=10, decimal_places=2)

    # Limites
    max_profissionais = models.IntegerField(default=1)
    max_agendamentos_mes = models.IntegerField(default=500)
    max_usuarios = models.IntegerField(default=1)
    max_servicos = models.IntegerField(default=10)

    # Trial
    trial_dias = models.IntegerField(default=7)

    ativo = models.BooleanField(default=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.get_nome_display()} - R$ {self.preco_mensal}/mês"


class Assinatura(models.Model):
    STATUS = [
        ('trial', 'Trial'),
        ('ativa', 'Ativa'),
        ('suspensa', 'Suspensa por Falta de Pagamento'),
        ('cancelada', 'Cancelada'),
        ('expirada', 'Expirada'),
    ]

    empresa = models.OneToOneField('empresas.Empresa', on_delete=models.CASCADE, related_name='assinatura')
    plano = models.ForeignKey(Plano, on_delete=models.PROTECT)
    status = models.CharField(max_length=20, choices=STATUS, default='trial')

    # Datas
    data_inicio = models.DateTimeField(auto_now_add=True)
    data_expiracao = models.DateTimeField()
    trial_ativo = models.BooleanField(default=True)
    ultimo_pagamento = models.DateTimeField(null=True, blank=True)

    # Gateway
    gateway = models.CharField(max_length=50, blank=True)  # 'stripe', 'asaas', 'manual'
    subscription_id_externo = models.CharField(max_length=255, blank=True)
    customer_id_externo = models.CharField(max_length=255, blank=True)

    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.empresa.nome} - {self.plano.nome} ({self.status})"

    def renovar(self, dias=30):
        """Renova assinatura por X dias"""
        self.data_expiracao = now() + timedelta(days=dias)
        self.ultimo_pagamento = now()
        self.status = 'ativa'
        self.trial_ativo = False
        self.save()

    def suspender(self):
        """Suspende por falta de pagamento"""
        self.status = 'suspensa'
        self.save()

    def cancelar(self):
        """Cancela permanentemente"""
        self.status = 'cancelada'
        self.save()
```

**Atualizar Empresa:**
```python
# empresas/models.py
class Empresa(models.Model):
    # ... campos existentes

    # NOVOS CAMPOS para SaaS
    onboarding_completo = models.BooleanField(default=False)
    onboarding_etapa = models.IntegerField(default=0)  # 0-4

    whatsapp_numero = models.CharField(max_length=20, unique=True, null=True, blank=True)
    whatsapp_token = models.CharField(max_length=255, blank=True)  # Evolution/Z-API
    whatsapp_instance_id = models.CharField(max_length=255, blank=True)
```

**Criar migrations:**
```bash
python manage.py makemigrations
python manage.py migrate
```

**Criar fixture de planos:**
```python
# assinaturas/fixtures/planos_iniciais.json
[
  {
    "model": "assinaturas.plano",
    "pk": 1,
    "fields": {
      "nome": "essencial",
      "descricao": "Ideal para profissionais autônomos",
      "preco_mensal": "49.00",
      "max_profissionais": 1,
      "max_agendamentos_mes": 500,
      "max_usuarios": 1,
      "max_servicos": 10,
      "trial_dias": 7,
      "ativo": true
    }
  },
  {
    "model": "assinaturas.plano",
    "pk": 2,
    "fields": {
      "nome": "profissional",
      "descricao": "Para pequenas equipes",
      "preco_mensal": "149.00",
      "max_profissionais": 5,
      "max_agendamentos_mes": 2000,
      "max_usuarios": 3,
      "max_servicos": 50,
      "trial_dias": 14,
      "ativo": true
    }
  }
]
```

```bash
python manage.py loaddata assinaturas/fixtures/planos_iniciais.json
```

---

### Dia 2-3: Integração Gateway de Pagamento

**Escolher gateway:**
- **Stripe** (internacional, cartão)
- **Asaas** (Brasil, boleto/pix/cartão) ← RECOMENDADO

**Instalar dependências:**
```bash
pip install stripe
# OU
pip install asaas
```

**Configurar settings:**
```python
# config/settings.py

# Stripe
STRIPE_PUBLIC_KEY = env('STRIPE_PUBLIC_KEY', default='')
STRIPE_SECRET_KEY = env('STRIPE_SECRET_KEY', default='')
STRIPE_WEBHOOK_SECRET = env('STRIPE_WEBHOOK_SECRET', default='')

# Asaas
ASAAS_API_KEY = env('ASAAS_API_KEY', default='')
ASAAS_SANDBOX = env('ASAAS_SANDBOX', default=True)
```

**Implementar integração:**

```python
# assinaturas/stripe_integration.py
import stripe
from django.conf import settings

stripe.api_key = settings.STRIPE_SECRET_KEY

def criar_checkout_session(empresa, plano):
    """Cria sessão de checkout Stripe"""
    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=[{
            'price_data': {
                'currency': 'brl',
                'product_data': {
                    'name': f'Plano {plano.get_nome_display()}',
                },
                'unit_amount': int(plano.preco_mensal * 100),  # centavos
            },
            'quantity': 1,
        }],
        mode='subscription',
        success_url=f'https://gestto.com.br/sucesso?session_id={{CHECKOUT_SESSION_ID}}',
        cancel_url='https://gestto.com.br/cancelado',
        metadata={
            'empresa_id': empresa.id,
            'plano_id': plano.id,
        }
    )
    return session


def processar_webhook_stripe(payload, sig_header):
    """Processa eventos do Stripe"""
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError:
        return {'error': 'Invalid payload'}
    except stripe.error.SignatureVerificationError:
        return {'error': 'Invalid signature'}

    # Checkout completado
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        empresa_id = session['metadata']['empresa_id']
        plano_id = session['metadata']['plano_id']

        # Ativar assinatura
        assinatura = Assinatura.objects.get(empresa_id=empresa_id)
        assinatura.renovar(dias=30)
        assinatura.subscription_id_externo = session['subscription']
        assinatura.save()

    # Pagamento falhou
    elif event['type'] == 'invoice.payment_failed':
        subscription_id = event['data']['object']['subscription']
        assinatura = Assinatura.objects.get(subscription_id_externo=subscription_id)
        assinatura.suspender()

    return {'status': 'success'}
```

**Criar endpoint webhook:**
```python
# assinaturas/views.py
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from .stripe_integration import processar_webhook_stripe

@api_view(['POST'])
@csrf_exempt
@permission_classes([AllowAny])
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')

    resultado = processar_webhook_stripe(payload, sig_header)

    if 'error' in resultado:
        return Response(resultado, status=400)

    return Response(resultado)
```

**Configurar URLs:**
```python
# config/urls.py
urlpatterns = [
    # ...
    path('api/webhooks/stripe/', stripe_webhook, name='stripe_webhook'),
]
```

**Testar webhook:**
```bash
# Instalar Stripe CLI
stripe listen --forward-to localhost:8000/api/webhooks/stripe/

# Disparar evento de teste
stripe trigger checkout.session.completed
```

**Checklist:**
- [ ] Conta Stripe/Asaas criada (modo sandbox)
- [ ] Keys configuradas no .env
- [ ] Função criar_checkout_session() implementada
- [ ] Webhook endpoint criado
- [ ] Teste de evento bem-sucedido

---

## 🚪 FASE 2: Auto-Provisionamento (2 dias)

### Objetivo
Cliente paga → sistema cria empresa automaticamente

**Implementar endpoint:**
```python
# assinaturas/views.py
from empresas.models import Empresa
from core.models import Usuario
from .models import Plano, Assinatura
from django.utils.text import slugify
from django.utils.timezone import now, timedelta
import secrets
import string

@api_view(['POST'])
@permission_classes([AllowAny])  # Chamado por webhook público
def create_tenant(request):
    """
    Cria empresa + assinatura + usuário admin automaticamente

    Payload esperado (vem do webhook Stripe/Asaas):
    {
        "company_name": "Salão Bela Vida",
        "email": "contato@belavida.com",
        "telefone": "11999999999",
        "cnpj": "12345678000199",
        "plano": "essencial"
    }
    """

    # 1. Validar dados
    required = ['company_name', 'email', 'telefone', 'cnpj']
    for field in required:
        if not request.data.get(field):
            return Response({'error': f'Campo {field} obrigatório'}, status=400)

    # 2. Verificar se empresa já existe
    cnpj = request.data['cnpj'].replace('.', '').replace('/', '').replace('-', '')
    if Empresa.objects.filter(cnpj=cnpj).exists():
        return Response({'error': 'Empresa já cadastrada'}, status=400)

    # 3. Criar Empresa
    slug = slugify(request.data['company_name'])

    # Garantir slug único
    base_slug = slug
    counter = 1
    while Empresa.objects.filter(slug=slug).exists():
        slug = f"{base_slug}-{counter}"
        counter += 1

    empresa = Empresa.objects.create(
        nome=request.data['company_name'],
        slug=slug,
        email=request.data['email'],
        telefone=request.data['telefone'],
        cnpj=cnpj,
        ativa=True,
        onboarding_completo=False,
        # Dados mínimos (resto preenche no onboarding)
        descricao='',
        endereco='',
        cidade='',
        estado='',
        cep=''
    )

    # 4. Criar Assinatura (trial)
    plano_nome = request.data.get('plano', 'essencial')
    plano = Plano.objects.get(nome=plano_nome)

    assinatura = Assinatura.objects.create(
        empresa=empresa,
        plano=plano,
        status='trial',
        data_expiracao=now() + timedelta(days=plano.trial_dias),
        trial_ativo=True,
        gateway=request.data.get('gateway', 'stripe')
    )

    # 5. Criar usuário admin
    senha_temporaria = gerar_senha_temporaria()

    usuario = Usuario.objects.create_user(
        username=f"admin_{empresa.id}",
        email=request.data['email'],
        password=senha_temporaria,
        empresa=empresa,
        is_staff=True,
        ativo=True
    )

    # 6. Enviar email de boas-vindas
    enviar_email_boas_vindas(usuario, empresa, senha_temporaria)

    # 7. Retornar dados
    return Response({
        'sucesso': True,
        'empresa_id': empresa.id,
        'slug': empresa.slug,
        'login_url': f'https://gestto.com.br/empresa/{empresa.slug}/onboarding',
        'trial_expira_em': assinatura.data_expiracao.isoformat(),
        'credenciais': {
            'email': request.data['email'],
            'senha_temporaria': senha_temporaria  # Apenas em dev, remover em prod
        }
    }, status=201)


def gerar_senha_temporaria(length=12):
    """Gera senha aleatória forte"""
    chars = string.ascii_letters + string.digits + '!@#$%'
    return ''.join(secrets.choice(chars) for _ in range(length))


def enviar_email_boas_vindas(usuario, empresa, senha):
    """Envia email com credenciais de acesso"""
    from django.core.mail import send_mail
    from django.conf import settings

    assunto = f'Bem-vindo ao Gestto - {empresa.nome}'

    mensagem = f"""
Olá!

Sua conta no Gestto foi criada com sucesso! 🎉

Empresa: {empresa.nome}
Trial: {empresa.assinatura.plano.trial_dias} dias grátis

Acesse agora:
https://gestto.com.br/empresa/{empresa.slug}/onboarding

Credenciais:
Email: {usuario.email}
Senha temporária: {senha}

Por favor, altere sua senha no primeiro acesso.

Qualquer dúvida, estamos à disposição!

Equipe Gestto
    """

    send_mail(
        assunto,
        mensagem,
        settings.DEFAULT_FROM_EMAIL,
        [usuario.email],
        fail_silently=False,
    )
```

**Adicionar URL:**
```python
# config/urls.py
path('api/create-tenant/', create_tenant, name='create_tenant'),
```

**Testar manualmente:**
```bash
curl -X POST http://localhost:8000/api/create-tenant/ \
  -H "Content-Type: application/json" \
  -d '{
    "company_name": "Teste Salão",
    "email": "teste@teste.com",
    "telefone": "11999999999",
    "cnpj": "12345678000199",
    "plano": "essencial"
  }'
```

**Checklist:**
- [ ] Endpoint `/api/create-tenant/` funciona
- [ ] Empresa criada no banco
- [ ] Assinatura trial criada
- [ ] Usuário admin criado
- [ ] Email enviado com credenciais
- [ ] Slug único garantido

---

## 🎓 FASE 3: Onboarding (3-4 dias)

### Objetivo
Novo cliente configura empresa em 4 passos guiados

**Estrutura:**
```
templates/onboarding/
├── base_wizard.html
├── step_1_servicos.html
├── step_2_profissional.html
├── step_3_whatsapp.html
└── step_4_pronto.html
```

**Views:**
```python
# core/onboarding_views.py
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from empresas.models import Servico, Profissional
from django.contrib import messages

@login_required
def onboarding_wizard(request):
    """Redireciona para etapa correta do onboarding"""
    empresa = request.user.empresa

    if empresa.onboarding_completo:
        return redirect('dashboard')

    # Redirecionar para etapa atual
    etapa = empresa.onboarding_etapa
    return redirect(f'onboarding_step_{etapa + 1}')


@login_required
def onboarding_step_1_servicos(request):
    """Passo 1: Cadastrar serviços"""
    empresa = request.user.empresa

    if request.method == 'POST':
        # Processar formulário de serviços
        servicos_data = request.POST.getlist('servico_nome')
        precos = request.POST.getlist('servico_preco')
        duracoes = request.POST.getlist('servico_duracao')

        for nome, preco, duracao in zip(servicos_data, precos, duracoes):
            if nome and preco and duracao:
                Servico.objects.create(
                    empresa=empresa,
                    nome=nome,
                    preco=preco,
                    duracao_minutos=int(duracao),
                    ativo=True
                )

        # Avançar para próxima etapa
        empresa.onboarding_etapa = 1
        empresa.save()

        messages.success(request, 'Serviços cadastrados com sucesso!')
        return redirect('onboarding_step_2')

    servicos = Servico.objects.filter(empresa=empresa)

    return render(request, 'onboarding/step_1_servicos.html', {
        'empresa': empresa,
        'servicos': servicos,
        'etapa_atual': 1
    })


@login_required
def onboarding_step_2_profissional(request):
    """Passo 2: Cadastrar pelo menos 1 profissional"""
    empresa = request.user.empresa

    if request.method == 'POST':
        nome = request.POST.get('prof_nome')
        email = request.POST.get('prof_email')
        telefone = request.POST.get('prof_telefone')
        servicos_ids = request.POST.getlist('prof_servicos')

        profissional = Profissional.objects.create(
            empresa=empresa,
            nome=nome,
            email=email,
            telefone=telefone,
            ativo=True
        )

        profissional.servicos.set(servicos_ids)

        empresa.onboarding_etapa = 2
        empresa.save()

        messages.success(request, 'Profissional cadastrado!')
        return redirect('onboarding_step_3')

    servicos = Servico.objects.filter(empresa=empresa, ativo=True)

    return render(request, 'onboarding/step_2_profissional.html', {
        'empresa': empresa,
        'servicos': servicos,
        'etapa_atual': 2
    })


@login_required
def onboarding_step_3_whatsapp(request):
    """Passo 3: Conectar WhatsApp"""
    empresa = request.user.empresa

    if request.method == 'POST':
        whatsapp_numero = request.POST.get('whatsapp_numero')
        whatsapp_token = request.POST.get('whatsapp_token')

        # Validar conexão WhatsApp (opcional)
        # testar_conexao_whatsapp(whatsapp_token)

        empresa.whatsapp_numero = whatsapp_numero
        empresa.whatsapp_token = whatsapp_token
        empresa.onboarding_etapa = 3
        empresa.save()

        messages.success(request, 'WhatsApp conectado!')
        return redirect('onboarding_step_4')

    return render(request, 'onboarding/step_3_whatsapp.html', {
        'empresa': empresa,
        'etapa_atual': 3
    })


@login_required
def onboarding_step_4_pronto(request):
    """Passo 4: Finalização com confete!"""
    empresa = request.user.empresa

    # Marcar onboarding como completo
    empresa.onboarding_completo = True
    empresa.onboarding_etapa = 4
    empresa.save()

    return render(request, 'onboarding/step_4_pronto.html', {
        'empresa': empresa,
        'link_agendamento': f'https://gestto.com.br/empresa/{empresa.slug}/agendar'
    })
```

**Template base:**
```html
<!-- templates/onboarding/base_wizard.html -->
<!DOCTYPE html>
<html>
<head>
    <title>Configuração Inicial - Gestto</title>
    <style>
        .wizard-progress {
            display: flex;
            justify-content: space-between;
            margin: 20px 0;
        }
        .wizard-step {
            flex: 1;
            text-align: center;
            padding: 10px;
            border-bottom: 3px solid #ccc;
        }
        .wizard-step.active {
            border-bottom-color: #3b82f6;
            color: #3b82f6;
            font-weight: bold;
        }
        .wizard-step.completed {
            border-bottom-color: #10b981;
            color: #10b981;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Bem-vindo ao Gestto, {{ empresa.nome }}! 🎉</h1>

        <div class="wizard-progress">
            <div class="wizard-step {% if etapa_atual == 1 %}active{% elif etapa_atual > 1 %}completed{% endif %}">
                1. Serviços
            </div>
            <div class="wizard-step {% if etapa_atual == 2 %}active{% elif etapa_atual > 2 %}completed{% endif %}">
                2. Profissional
            </div>
            <div class="wizard-step {% if etapa_atual == 3 %}active{% elif etapa_atual > 3 %}completed{% endif %}">
                3. WhatsApp
            </div>
            <div class="wizard-step {% if etapa_atual == 4 %}active{% endif %}">
                4. Pronto!
            </div>
        </div>

        {% block content %}{% endblock %}
    </div>

    <script>
        // Confete no último passo
        {% if etapa_atual == 4 %}
        // Adicionar lib de confetti.js
        confetti({
            particleCount: 100,
            spread: 70,
            origin: { y: 0.6 }
        });
        {% endif %}
    </script>
</body>
</html>
```

**URLs:**
```python
# core/urls.py (criar novo arquivo)
from django.urls import path
from . import onboarding_views

urlpatterns = [
    path('onboarding/', onboarding_views.onboarding_wizard, name='onboarding'),
    path('onboarding/1/', onboarding_views.onboarding_step_1_servicos, name='onboarding_step_1'),
    path('onboarding/2/', onboarding_views.onboarding_step_2_profissional, name='onboarding_step_2'),
    path('onboarding/3/', onboarding_views.onboarding_step_3_whatsapp, name='onboarding_step_3'),
    path('onboarding/4/', onboarding_views.onboarding_step_4_pronto, name='onboarding_step_4'),
]
```

```python
# config/urls.py
path('', include('core.urls')),
```

**Checklist:**
- [ ] 4 templates de onboarding criados
- [ ] Views de cada passo implementadas
- [ ] Validações de formulário
- [ ] Navegação entre passos funciona
- [ ] Etapa salva no banco (onboarding_etapa)
- [ ] Confete no passo 4 🎉

---

## 🔗 FASE 4: Webhook Multi-Tenant (2-3 dias)

### Objetivo
1 webhook recebe msgs de TODAS empresas e roteia automaticamente

**Implementar:**
```python
# agendamentos/views.py (adicionar)
from empresas.models import Empresa
import requests

@api_view(['POST'])
@permission_classes([AllowAny])  # Webhook público
def whatsapp_webhook_unico(request):
    """
    Recebe mensagens de TODOS os clientes
    Detecta empresa pelo campo 'instance' da Evolution API

    Payload Evolution API:
    {
        "instance": "salao-bela-vida",  ← slug da empresa
        "data": {
            "key": {"remoteJid": "5511999999999@s.whatsapp.net"},
            "message": {"conversation": "Quero agendar"}
        }
    }
    """

    # 1. Extrair dados
    instance_name = request.data.get('instance')
    phone_from = request.data.get('data', {}).get('key', {}).get('remoteJid', '').split('@')[0]
    message_text = request.data.get('data', {}).get('message', {}).get('conversation', '')

    if not instance_name:
        return Response({'error': 'Instance não informada'}, status=400)

    # 2. Buscar empresa pelo slug (instance)
    try:
        empresa = Empresa.objects.get(slug=instance_name, ativa=True)
    except Empresa.DoesNotExist:
        return Response({'error': 'Empresa não encontrada'}, status=404)

    # 3. Verificar assinatura
    try:
        assinatura = empresa.assinatura

        if assinatura.status not in ['trial', 'ativa']:
            return Response({
                'error': f'Assinatura {assinatura.status}. Entre em contato com o suporte.'
            }, status=403)

        # Verificar se trial expirou
        if assinatura.trial_ativo and assinatura.data_expiracao < now():
            assinatura.status = 'expirada'
            assinatura.save()
            return Response({'error': 'Trial expirado. Faça upgrade.'}, status=403)

    except Assinatura.DoesNotExist:
        return Response({'error': 'Empresa sem assinatura ativa'}, status=403)

    # 4. Encaminhar para n8n com tenant_id
    n8n_webhook_url = f'https://n8n.seudominio.com/webhook/{empresa.id}'

    try:
        response = requests.post(n8n_webhook_url, json={
            'tenant_id': empresa.id,
            'tenant_slug': empresa.slug,
            'phone': phone_from,
            'message': message_text,
            'timestamp': now().isoformat()
        }, timeout=10)

        return Response({
            'status': 'forwarded',
            'empresa': empresa.nome,
            'n8n_response': response.json() if response.ok else None
        })

    except requests.RequestException as e:
        return Response({
            'error': 'Falha ao encaminhar para n8n',
            'details': str(e)
        }, status=500)
```

**Adicionar URL:**
```python
# config/urls.py
path('api/whatsapp-webhook/', whatsapp_webhook_unico, name='whatsapp_webhook'),
```

**Rate limiting nginx:**
```nginx
# nginx/nginx.conf
limit_req_zone $binary_remote_addr zone=whatsapp:10m rate=10r/s;

location /api/whatsapp-webhook/ {
    limit_req zone=whatsapp burst=20 nodelay;
    proxy_pass http://web:8000;
}
```

**Checklist:**
- [ ] Endpoint único `/api/whatsapp-webhook/` criado
- [ ] Detecta empresa pelo instance/slug
- [ ] Verifica status de assinatura
- [ ] Encaminha para n8n com tenant_id
- [ ] Rate limiting configurado
- [ ] Testado com 2 empresas diferentes

---

## 🚨 FASE 5: Limites e Monitoramento (2 dias)

### Objetivo
Bloquear ao atingir limite do plano

**Middleware:**
```python
# assinaturas/middleware.py
from django.shortcuts import redirect
from django.contrib import messages
from django.utils.timezone import now
from agendamentos.models import Agendamento

class LimitesPlanoMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Só verificar se usuário autenticado
        if request.user.is_authenticated and hasattr(request.user, 'empresa'):
            empresa = request.user.empresa

            try:
                assinatura = empresa.assinatura
                plano = assinatura.plano

                # Verificar trial expirado
                if assinatura.trial_ativo and assinatura.data_expiracao < now():
                    assinatura.status = 'expirada'
                    assinatura.save()
                    messages.warning(request, 'Seu trial expirou! Faça upgrade para continuar.')
                    return redirect('upgrade_plano')

                # Verificar assinatura ativa apenas em rotas críticas
                if assinatura.status not in ['trial', 'ativa']:
                    if request.path.startswith(('/agendamentos', '/clientes', '/dashboard')):
                        messages.error(request, 'Assinatura suspensa. Entre em contato.')
                        return redirect('assinatura_suspensa')

                # Verificar limites apenas ao criar agendamentos
                if request.path == '/agendamentos/criar/' and request.method == 'POST':
                    mes_atual = now().replace(day=1, hour=0, minute=0, second=0)
                    total_mes = Agendamento.objects.filter(
                        empresa=empresa,
                        criado_em__gte=mes_atual
                    ).count()

                    if total_mes >= plano.max_agendamentos_mes:
                        messages.error(request,
                            f'Limite de {plano.max_agendamentos_mes} agendamentos/mês atingido! '
                            f'Faça upgrade para continuar.'
                        )
                        return redirect('upgrade_plano')

            except Exception:
                pass  # Empresa sem assinatura (admin, etc)

        return self.get_response(request)
```

**Adicionar em settings:**
```python
# config/settings.py
MIDDLEWARE = [
    # ... outros middlewares
    'assinaturas.middleware.LimitesPlanoMiddleware',
]
```

**Dashboard com métricas:**
```python
# dashboard/views.py (atualizar)
@login_required
def dashboard(request):
    empresa = request.user.empresa

    # Métricas do mês
    mes_atual = now().replace(day=1, hour=0, minute=0)
    agendamentos_mes = Agendamento.objects.filter(
        empresa=empresa,
        criado_em__gte=mes_atual
    ).count()

    try:
        assinatura = empresa.assinatura
        plano = assinatura.plano
        percentual_uso = (agendamentos_mes / plano.max_agendamentos_mes) * 100
        alerta_limite = percentual_uso >= 90
    except:
        plano = None
        percentual_uso = 0
        alerta_limite = False

    context = {
        'agendamentos_mes': agendamentos_mes,
        'plano': plano,
        'percentual_uso': percentual_uso,
        'alerta_limite': alerta_limite,
        # ... outros dados
    }

    return render(request, 'dashboard/index.html', context)
```

**Template de alerta:**
```html
<!-- templates/dashboard/index.html -->
{% if alerta_limite %}
<div class="alert alert-warning">
    <h3>⚠️ Atenção: Limite próximo!</h3>
    <p>
        Você usou <strong>{{ agendamentos_mes }}/{{ plano.max_agendamentos_mes }}</strong>
        agendamentos este mês ({{ percentual_uso|floatformat:0 }}%)
    </p>
    <a href="{% url 'upgrade_plano' %}" class="btn btn-primary">
        🚀 Fazer Upgrade para Plano Profissional
    </a>
</div>
{% endif %}
```

**Checklist:**
- [ ] Middleware de limites implementado
- [ ] Dashboard mostra uso do mês
- [ ] Alerta de 90% funciona
- [ ] Bloqueio ao atingir 100%
- [ ] Página de upgrade criada

---

## 🌐 FASE 6: Deploy e Ajustes Finais (2 dias)

### Tarefas
- [ ] Configurar subdomínios wildcard (opcional)
- [ ] SSL wildcard Let's Encrypt
- [ ] Atualizar docker-compose.yml
- [ ] Migrar banco de produção
- [ ] Testes de carga
- [ ] Landing page integrada com checkout

### Deploy
```bash
# Na VPS
cd /home/axio_gestto
git pull origin feature/saas-transformation
docker-compose down
docker-compose build
python manage.py migrate
docker-compose up -d
```

**Checklist final:**
- [ ] Todos endpoints funcionando
- [ ] Webhook Stripe/Asaas testado
- [ ] Criação automática de tenant OK
- [ ] Onboarding completo
- [ ] Limites bloqueando corretamente
- [ ] Email enviando
- [ ] SSL válido
- [ ] Logs sem erros

---

## 📅 CRONOGRAMA COMPLETO

| Fase | Dias | Acumulado |
|------|------|-----------|
| 0. Preparação | 1 | 1 dia |
| 1. Models + Gateway | 3 | 4 dias |
| 2. Auto-Provisionamento | 2 | 6 dias |
| 3. Onboarding | 4 | 10 dias |
| 4. Webhook Multi-Tenant | 3 | 13 dias |
| 5. Limites | 2 | 15 dias |
| 6. Deploy | 2 | **17 dias** |

**Total:** 17 dias úteis = **3-4 semanas**

---

## ✅ PRÓXIMOS PASSOS APÓS LANÇAMENTO

1. **Marketing:**
   - Landing page
   - 5 clientes piloto grátis (30 dias)
   - Coletar feedback

2. **Monitoramento:**
   - Sentry para erros
   - Analytics (PostHog/Mixpanel)
   - Dashboard admin com métricas globais

3. **Melhorias v1.1:**
   - Subdomínios personalizados
   - Mais gateways de pagamento
   - Relatórios avançados
   - App mobile

---

**Boa sorte na implementação! 🚀**
