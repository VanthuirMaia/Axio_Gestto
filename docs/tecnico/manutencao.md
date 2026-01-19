# 🔧 Guia de Manutenção Simplificado - Gestto SaaS

## ⚠️ NÃO ENTRE EM PÂNICO!

O sistema parece complexo, mas **90% dele você nunca vai precisar mexer**. Este guia mostra exatamente onde você vai trabalhar no dia a dia.

---

## 📦 O que você REALMENTE precisa saber

### Sistema dividido em 3 camadas:

```
┌─────────────────────────────────────────┐
│  CAMADA 1: CORE DO NEGÓCIO              │ ← VOCÊ VAI MEXER AQUI 90% DO TEMPO
│  - Agendamentos                         │
│  - Clientes                             │
│  - Financeiro                           │
│  - Dashboard                            │
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│  CAMADA 2: SAAS (já configurado)        │ ← MEXE 1x/MÊS OU MENOS
│  - Assinaturas (já funciona sozinho)   │
│  - Webhooks de pagamento (automático)   │
│  - Limites (middleware cuida sozinho)   │
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│  CAMADA 3: INFRAESTRUTURA               │ ← SÓ NO DEPLOY (1x)
│  - Nginx, SSL, Banco                    │
│  - Você configura 1 vez e esquece       │
└─────────────────────────────────────────┘
```

---

## 🎯 Tarefas Comuns e ONDE fazer

### "Quero adicionar um novo campo no agendamento"

**Onde mexer:**
1. `agendamentos/models.py` - Adicionar campo no model
2. `python manage.py makemigrations && python manage.py migrate`
3. `templates/agendamentos/criar.html` - Adicionar campo no formulário
4. **Pronto!** O resto funciona sozinho.

**NÃO precisa mexer em:** Webhooks, Assinaturas, Middlewares

---

### "Cliente reclamou que não recebeu notificação"

**Onde olhar:**
1. `agendamentos/models.py` linha 150-200 - Model `LogMensagemBot`
2. Admin Django: `/admin/agendamentos/logmensagembot/`
3. Ver o campo `status` e `erro_detalhes`

**Como ver logs:**
```python
# No Django shell
from agendamentos.models import LogMensagemBot
logs = LogMensagemBot.objects.filter(telefone='5511999998888').order_by('-criado_em')[:10]
for log in logs:
    print(f"{log.intencao_detectada}: {log.status} - {log.resposta_enviada}")
```

**NÃO precisa mexer em:** Código do webhook (já funciona)

---

### "Preciso mudar o preço de um plano"

**Onde mexer:**
1. Admin Django: `/admin/assinaturas/plano/`
2. Editar o plano "Essencial" e mudar `preco_mensal`
3. **Pronto!** Novas assinaturas usarão o novo preço.

**Assinaturas antigas:** Não mudam automaticamente (correto)

**NÃO precisa mexer em:** Código Python

---

### "Cliente pediu para aumentar limite de agendamentos"

**Opção 1 - Fazer upgrade do plano (recomendado):**
- Cliente vai em `/configuracoes/assinatura/`
- Clica em "Fazer upgrade"
- Paga a diferença

**Opção 2 - Aumentar manualmente (emergencial):**
1. Admin Django: `/admin/assinaturas/plano/`
2. Editar o plano da empresa
3. Aumentar `max_agendamentos_mes`
4. Salvar

**NÃO precisa mexer em:** Middlewares (leem do banco automaticamente)

---

### "Webhook do WhatsApp parou de funcionar"

**Checklist de diagnóstico:**

1. **Empresa está com assinatura ativa?**
   ```python
   # Django shell
   from empresas.models import Empresa
   empresa = Empresa.objects.get(slug='nome-cliente')
   print(empresa.assinatura.status)  # Deve ser 'ativa' ou 'trial'
   ```

2. **Instance ID está correto?**
   ```python
   print(empresa.whatsapp_instance_id)  # Ex: "empresa123"
   print(empresa.whatsapp_conectado)    # Deve ser True
   ```

3. **Evolution API está enviando para URL correta?**
   - URL deve ser: `https://seu-dominio.com/api/whatsapp-webhook/`
   - Verifique no painel da Evolution API

4. **Ver logs de erro:**
   ```bash
   # No servidor
   tail -f /var/log/gestto/error.log
   ```

**NÃO precisa mexer em:** Código do webhook (a menos que ache um bug)

---

### "Cliente não consegue criar agendamento (diz que atingiu limite)"

**Causa:** Atingiu o limite do plano dele

**Verificar:**
```python
from assinaturas.models import Assinatura
from agendamentos.models import Agendamento
from django.utils.timezone import now

empresa = Empresa.objects.get(slug='cliente')
assinatura = empresa.assinatura

inicio_mes = now().replace(day=1, hour=0, minute=0, second=0)
agendamentos_mes = Agendamento.objects.filter(
    empresa=empresa,
    criado_em__gte=inicio_mes
).count()

print(f"Usou: {agendamentos_mes} / {assinatura.plano.max_agendamentos_mes}")
```

**Solução:**
- Cliente faz upgrade do plano
- OU aguarda próximo mês (contador reseta dia 1)

**NÃO precisa mexer em:** Middleware (está funcionando correto)

---

## 🔥 Arquivos que você VAI mexer frequentemente

### 1. `agendamentos/views.py`
**O que faz:** Lógica de criar, editar, deletar agendamentos
**Quando mexer:** Adicionar campos, mudar validações, adicionar funcionalidades

### 2. `templates/dashboard.html`
**O que faz:** Página principal após login
**Quando mexer:** Adicionar gráficos, mudar layout, adicionar cards

### 3. `clientes/models.py` e `clientes/views.py`
**O que faz:** Cadastro e gestão de clientes
**Quando mexer:** Adicionar campos customizados (data de nascimento, CPF, etc)

### 4. `agendamentos/bot_api.py` (processar_agendamento)
**O que faz:** Lógica quando cliente agenda via WhatsApp
**Quando mexer:** Mudar validações, adicionar regras de negócio

---

## 🚫 Arquivos que você NUNCA vai mexer (ou muito raramente)

### 1. `assinaturas/stripe_integration.py`
**O que faz:** Comunicação com Stripe
**Quando mexer:** NUNCA (a menos que Stripe mude a API)

### 2. `assinaturas/asaas_integration.py`
**O que faz:** Comunicação com Asaas
**Quando mexer:** NUNCA (a menos que Asaas mude a API)

### 3. `core/middleware.py`
**O que faz:** Verifica limites automaticamente
**Quando mexer:** NUNCA (já funciona perfeitamente)

### 4. `assinaturas/views.py` (create_tenant, webhooks)
**O que faz:** Cria novos clientes automaticamente
**Quando mexer:** NUNCA (processo crítico, não mexer)

---

## 🆘 Cenários de Emergência

### "O sistema inteiro parou! Socorro!"

**Checklist:**

1. **Serviço Django está rodando?**
   ```bash
   sudo systemctl status gestto
   # Se stopped: sudo systemctl start gestto
   ```

2. **Banco de dados está rodando?**
   ```bash
   sudo systemctl status postgresql
   # Se stopped: sudo systemctl start postgresql
   ```

3. **Nginx está rodando?**
   ```bash
   sudo systemctl status nginx
   # Se stopped: sudo systemctl start nginx
   ```

4. **Ver logs de erro:**
   ```bash
   tail -100 /var/log/gestto/error.log
   ```

5. **Reiniciar tudo (última opção):**
   ```bash
   sudo systemctl restart postgresql
   sudo systemctl restart gestto
   sudo systemctl restart nginx
   ```

---

### "Pagamento foi feito mas assinatura não ativou"

**Causa:** Webhook do gateway não chegou ou falhou

**Solução manual:**

```python
# Django shell
from assinaturas.models import Assinatura
from django.utils.timezone import now
from datetime import timedelta

assinatura = Assinatura.objects.get(empresa__slug='cliente')
assinatura.status = 'ativa'
assinatura.data_expiracao = now() + timedelta(days=30)
assinatura.save()

print("Assinatura ativada manualmente!")
```

**Depois investigar:** Por que webhook falhou? Ver logs.

---

### "Quero desativar o sistema SaaS e voltar para single-tenant"

**Fácil! Só comentar os middlewares:**

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

    # SaaS Middlewares (COMENTAR PARA DESATIVAR LIMITES)
    # 'core.middleware.AssinaturaExpiracaoMiddleware',
    # 'core.middleware.LimitesPlanoMiddleware',
    # 'core.middleware.UsageTrackingMiddleware',
]
```

**Pronto!** Sistema volta a funcionar sem limites.

---

## 📚 Comandos Django Essenciais

### Ver todos os clientes (empresas)
```bash
python manage.py shell
from empresas.models import Empresa
empresas = Empresa.objects.all()
for e in empresas:
    print(f"{e.nome} - {e.slug} - {e.assinatura.status if hasattr(e, 'assinatura') else 'Sem assinatura'}")
```

### Ver todos os agendamentos de hoje
```python
from agendamentos.models import Agendamento
from django.utils.timezone import now

hoje = now().date()
agendamentos = Agendamento.objects.filter(data_hora_inicio__date=hoje)
for a in agendamentos:
    print(f"{a.empresa.nome}: {a.cliente.nome} - {a.servico.nome} - {a.status}")
```

### Ver assinaturas que expiram em 7 dias
```python
from assinaturas.models import Assinatura
from django.utils.timezone import now
from datetime import timedelta

limite = now() + timedelta(days=7)
expirando = Assinatura.objects.filter(
    status='ativa',
    data_expiracao__lte=limite
)

for a in expirando:
    dias = (a.data_expiracao - now()).days
    print(f"{a.empresa.nome} expira em {dias} dias")
```

### Criar manualmente um novo cliente (empresa)
```python
from assinaturas.models import Plano, Assinatura
from empresas.models import Empresa
from core.models import Usuario
from django.utils.timezone import now
from datetime import timedelta

# 1. Criar empresa
empresa = Empresa.objects.create(
    nome="Barbearia Teste",
    slug="barbearia-teste",
    ativa=True
)

# 2. Criar assinatura
plano = Plano.objects.get(nome='essencial')
assinatura = Assinatura.objects.create(
    empresa=empresa,
    plano=plano,
    status='trial',
    data_inicio=now(),
    data_expiracao=now() + timedelta(days=7)
)

# 3. Criar usuário admin
usuario = Usuario.objects.create_user(
    username=f"admin_{empresa.slug}",
    email="admin@teste.com",
    password="senha123",
    empresa=empresa,
    nome="Administrador"
)

print(f"Empresa criada! Login: {usuario.username} / senha123")
```

---

## 🎯 Resumo: O que importa?

### VOCÊ VAI MEXER AQUI (90% do tempo):
- ✅ `agendamentos/` - Lógica de agendamentos
- ✅ `clientes/` - Cadastro de clientes
- ✅ `financeiro/` - Receitas e despesas
- ✅ `templates/` - Visual do sistema
- ✅ Admin Django - Gerenciar dados

### DEIXA QUIETO (funciona sozinho):
- 🔒 `assinaturas/stripe_integration.py`
- 🔒 `assinaturas/asaas_integration.py`
- 🔒 `core/middleware.py`
- 🔒 Webhooks de pagamento

### SÓ MEXE 1 VEZ (no deploy):
- ⚙️ `config/settings.py`
- ⚙️ Nginx, SSL
- ⚙️ Variáveis `.env`

---

## 💡 Dica de Ouro

**Se algo quebrar e você não souber consertar:**

1. **Não entre em pânico**
2. **Veja os logs:** `tail -100 /var/log/gestto/error.log`
3. **Teste no Django shell** (comandos acima)
4. **Google o erro** (99% dos erros Django já foram resolvidos)
5. **Reverta para backup** se tudo falhar

---

## 📞 Onde pedir ajuda

- **Documentação Django:** https://docs.djangoproject.com/
- **Stack Overflow:** Pesquise "django [seu erro]"
- **ChatGPT/Claude:** Cole o erro e peça explicação
- **Comunidade Django Brasil:** https://t.me/pythonbrasil

---

## ✅ Checklist de Confiança

- [ ] Sei onde está a lógica de agendamentos (`agendamentos/views.py`)
- [ ] Sei como ver logs de WhatsApp (Admin Django)
- [ ] Sei como ativar assinatura manualmente (shell acima)
- [ ] Sei como desativar limites (comentar middlewares)
- [ ] Tenho backup do banco de dados
- [ ] Testei criar agendamento no sistema
- [ ] Testei webhook do WhatsApp
- [ ] Sei reiniciar os serviços (systemctl)

---

**Lembre-se:** 80% da manutenção é CRUD básico (criar, ler, atualizar, deletar).
O sistema SaaS roda sozinho em background, você nem vai notar que existe! 🚀
