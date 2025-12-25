# 🔄 Como Simplificar o Sistema (se necessário)

## Opção 1: Manter SaaS mas DESATIVAR limites

Se você quer cobrar dos clientes mas **não quer bloquear** quando atingirem limites:

### Passo 1: Comentar middleware de limites

`config/settings.py`:
```python
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

    # SaaS Middlewares
    'core.middleware.AssinaturaExpiracaoMiddleware',  # ← Mantém avisos
    # 'core.middleware.LimitesPlanoMiddleware',       # ← DESATIVA bloqueios
    'core.middleware.UsageTrackingMiddleware',
]
```

**Resultado:**
- ✅ Sistema continua cobrando mensalidades
- ✅ Clientes veem avisos de expiração
- ❌ Mas NÃO são bloqueados por limites
- ✅ Você controla manualmente quem bloquear

---

## Opção 2: Manter SaaS mas com limites MUITO ALTOS

Se você quer limites "só para casos extremos":

### Passo 1: Editar planos no Admin

Acesse: `/admin/assinaturas/plano/`

Edite cada plano e coloque:
- `max_agendamentos_mes`: `99999` (basicamente ilimitado)
- `max_profissionais`: `999` (basicamente ilimitado)

**Resultado:**
- ✅ Sistema SaaS continua funcionando
- ✅ Clientes pagam normalmente
- ✅ Praticamente nunca atingem limites
- ✅ Você tem controle fino quando precisar

---

## Opção 3: Remover TODA a parte SaaS (voltar para single-tenant)

Se você quiser **um sistema para 1 empresa só** (sem cobranças, sem limites):

### Passo 1: Comentar apps SaaS

`config/settings.py`:
```python
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Apps do projeto
    'core.apps.CoreConfig',
    'empresas.apps.EmpresasConfig',
    'clientes.apps.ClientesConfig',
    'agendamentos.apps.AgendamentosConfig',
    'financeiro.apps.FinanceiroConfig',
    'configuracoes.apps.ConfiguracoesConfig',
    # 'assinaturas.apps.AssinaturasConfig',  # ← COMENTAR

    # Third party
    'django_apscheduler',
]
```

### Passo 2: Comentar middlewares SaaS

```python
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

    # SaaS Middlewares - COMENTAR TUDO
    # 'core.middleware.AssinaturaExpiracaoMiddleware',
    # 'core.middleware.LimitesPlanoMiddleware',
    # 'core.middleware.UsageTrackingMiddleware',
]
```

### Passo 3: Comentar URLs SaaS

`config/urls.py`:
```python
urlpatterns = [
    path('health/', health_check, name='health_check'),
    path('admin/', admin.site.urls),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),

    # Password reset...

    # API Bot WhatsApp (n8n)
    path('api/bot/processar/', processar_comando_bot, name='api_bot_processar'),

    # COMENTAR WEBHOOK SAAS
    # path('api/whatsapp-webhook/', whatsapp_webhook_saas, name='whatsapp_webhook_saas'),

    # COMENTAR APIs SaaS
    # path('api/', include('assinaturas.urls')),

    # COMENTAR Onboarding (ou manter se quiser o wizard)
    # path('', include('core.onboarding_urls')),

    path('dashboard/', dashboard_view, name='dashboard'),
    path('agendamentos/', include('agendamentos.urls')),
    path('clientes/', include('clientes.urls')),
    # ... resto
]
```

### Passo 4: Remover verificação de onboarding

`core/views.py` (login_view):
```python
def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        email_ou_usuario = request.POST.get('email_ou_usuario')
        senha = request.POST.get('senha')

        try:
            usuario = Usuario.objects.get(email=email_ou_usuario)
            user = authenticate(request, username=usuario.username, password=senha)
        except Usuario.DoesNotExist:
            user = authenticate(request, username=email_ou_usuario, password=senha)

        if user is not None and user.ativo:
            login(request, user)

            # COMENTAR VERIFICAÇÃO DE ONBOARDING
            # if hasattr(user, 'empresa') and user.empresa:
            #     if not user.empresa.onboarding_completo:
            #         return redirect('onboarding')

            return redirect('dashboard')
        else:
            messages.error(request, 'Email/Usuario ou senha incorretos.')

    return render(request, 'login.html')
```

`core/views.py` (dashboard_view):
```python
def dashboard_view(request):
    empresa = request.user.empresa
    if not empresa:
        messages.error(request, 'Usuário não associado a nenhuma empresa.')
        return redirect('logout')

    # COMENTAR VERIFICAÇÃO DE ONBOARDING
    # if not empresa.onboarding_completo:
    #     return redirect('onboarding')

    # ... resto da view
```

### Passo 5: Migração (opcional)

Se quiser limpar o banco de dados das tabelas SaaS:

```bash
# CUIDADO! Isso apaga dados de assinaturas
python manage.py migrate assinaturas zero
```

**Resultado:**
- ✅ Sistema volta a ser single-tenant
- ✅ Sem cobranças, sem limites
- ✅ Funciona para 1 empresa
- ❌ Perde capacidade de multi-tenant

---

## Opção 4: Modelo Híbrido (RECOMENDADO)

**Mantenha SaaS mas simplifique:**

### O que MANTER:
- ✅ App `assinaturas` (para ter controle de planos)
- ✅ Onboarding wizard (experiência boa para novos clientes)
- ✅ Middleware de expiração (avisos úteis)
- ✅ Webhook multi-tenant (essencial se tiver +1 cliente)

### O que DESATIVAR:
- ❌ Middleware de limites (comentar)
- ❌ Integrações Stripe/Asaas (se cobrar manualmente)
- ❌ Auto-provisioning (se criar clientes manual)

### Como fazer:

1. **Comentar middleware de limites:**
```python
# config/settings.py
MIDDLEWARE = [
    # ...
    'core.middleware.AssinaturaExpiracaoMiddleware',  # ← Mantém
    # 'core.middleware.LimitesPlanoMiddleware',       # ← Remove
    'core.middleware.UsageTrackingMiddleware',        # ← Mantém
]
```

2. **Criar clientes manualmente no Admin:**
- Acessa `/admin/empresas/empresa/add/`
- Cria empresa
- Acessa `/admin/assinaturas/assinatura/add/`
- Associa empresa a um plano
- Status: `ativa` / Data expiração: 1 ano na frente

3. **Cobrar manualmente:**
- No final do mês, você envia boleto/PIX
- Cliente paga
- Você atualiza `data_expiracao` no Admin

**Resultado:**
- ✅ Sistema multi-tenant funcionando
- ✅ Onboarding bonito para novos clientes
- ✅ Sem complexidade de pagamentos automáticos
- ✅ Sem bloqueios por limites
- ✅ Você controla tudo manualmente

---

## Comparação dos Modelos

| Característica | SaaS Completo | Híbrido | Single-Tenant |
|----------------|---------------|---------|---------------|
| **Múltiplos clientes** | ✅ Sim | ✅ Sim | ❌ Não (1 só) |
| **Pagamento automático** | ✅ Stripe/Asaas | ❌ Manual | ❌ N/A |
| **Limites de uso** | ✅ Automático | ❌ Desativado | ❌ N/A |
| **Onboarding wizard** | ✅ Sim | ✅ Sim | 🔄 Opcional |
| **Webhook multi-tenant** | ✅ Sim | ✅ Sim | ❌ Single |
| **Complexidade** | 🔴 Alta | 🟡 Média | 🟢 Baixa |
| **Manutenção** | 🔴 Mais trabalho | 🟡 Moderado | 🟢 Simples |
| **Escalabilidade** | 🟢 Infinita | 🟢 Infinita | 🔴 Limitada |

---

## 🎯 Minha Recomendação

**Use o modelo HÍBRIDO:**

### Por que?
1. ✅ **Flexibilidade:** Você pode adicionar +1 cliente facilmente
2. ✅ **Simplicidade:** Sem pagamentos automáticos (você controla)
3. ✅ **Sem riscos:** Sem bloqueios automáticos por limites
4. ✅ **Futuro:** Se crescer, só "ativar" o que estava comentado

### Como implementar:

**Passo 1:** Comentar só o middleware de limites
```python
# config/settings.py linha 45
# 'core.middleware.LimitesPlanoMiddleware',  # ← Adicionar # na frente
```

**Passo 2:** Criar clientes manualmente (via Admin)

**Passo 3:** Cobrar manualmente (boleto, PIX, transferência)

**Passo 4:** Pronto! Sistema rodando sem complexidade

---

## 🔧 Scripts de Simplificação

### Script 1: Remover limites de todos os planos

```python
# Django shell
from assinaturas.models import Plano

planos = Plano.objects.all()
for plano in planos:
    plano.max_agendamentos_mes = 99999
    plano.max_profissionais = 999
    plano.save()

print("Todos os planos agora têm limites altíssimos!")
```

### Script 2: Ativar todas as assinaturas por 1 ano

```python
from assinaturas.models import Assinatura
from django.utils.timezone import now
from datetime import timedelta

assinaturas = Assinatura.objects.all()
for assinatura in assinaturas:
    assinatura.status = 'ativa'
    assinatura.data_expiracao = now() + timedelta(days=365)
    assinatura.save()

print("Todas as assinaturas ativas por 1 ano!")
```

### Script 3: Criar empresa sem auto-provisioning

```python
from empresas.models import Empresa
from assinaturas.models import Plano, Assinatura
from core.models import Usuario
from django.utils.timezone import now
from datetime import timedelta

# 1. Criar empresa
empresa = Empresa.objects.create(
    nome="Nome do Cliente",
    slug="cliente-slug",
    ativa=True,
    onboarding_completo=False  # Para passar pelo wizard
)

# 2. Criar assinatura
plano_profissional = Plano.objects.get(nome='profissional')
Assinatura.objects.create(
    empresa=empresa,
    plano=plano_profissional,
    status='ativa',
    data_inicio=now(),
    data_expiracao=now() + timedelta(days=365)
)

# 3. Criar usuário
usuario = Usuario.objects.create_user(
    username=f"admin_{empresa.slug}",
    email="cliente@email.com",
    password="senha123",
    empresa=empresa
)

print(f"Cliente criado!")
print(f"Login: {usuario.username}")
print(f"Senha: senha123")
print(f"URL: https://seu-dominio.com/login/")
```

---

## ✅ Decisão Rápida

**Responda:**

1. **Você vai ter +1 cliente usando o sistema?**
   - Sim → Mantenha multi-tenant (modelo Híbrido)
   - Não → Pode simplificar para single-tenant

2. **Quer cobrar automaticamente (Stripe/Asaas)?**
   - Sim → Mantenha SaaS completo
   - Não → Modelo Híbrido (cobrança manual)

3. **Quer bloquear clientes quando atingirem limites?**
   - Sim → Mantenha middleware de limites
   - Não → Comente middleware

---

**Lembre-se:** Você pode **sempre voltar atrás**! Tudo é reversível.
Se comentar algo e quiser depois, só descomentar. 🔄
