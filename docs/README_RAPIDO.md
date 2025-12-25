# ⚡ README Rápido - O que você REALMENTE precisa saber

## 🎯 Em 3 frases:

1. **90% do sistema é igual ao que você já conhece** (Django básico - CRUD de agendamentos, clientes, etc)
2. **A parte SaaS funciona sozinha em background** (você nem percebe que existe)
3. **Se ficar complexo demais, você pode desativar a parte SaaS** (é só comentar 3 linhas)

---

## 📂 Estrutura do Código (Simplificada)

```
Gestto/
│
├── 📁 agendamentos/          ← VOCÊ MEXE AQUI
│   ├── models.py            ← Tabela de agendamentos
│   ├── views.py             ← Criar/editar/deletar agendamentos
│   └── bot_api.py           ← WhatsApp (já funciona, só mexe se precisar)
│
├── 📁 clientes/              ← VOCÊ MEXE AQUI
│   ├── models.py            ← Tabela de clientes
│   └── views.py             ← CRUD clientes
│
├── 📁 financeiro/            ← VOCÊ MEXE AQUI
│   ├── models.py            ← Receitas e despesas
│   └── views.py             ← Lançamentos financeiros
│
├── 📁 templates/             ← VOCÊ MEXE AQUI
│   ├── dashboard.html       ← Página principal
│   ├── agendamentos/        ← Telas de agendamento
│   └── onboarding/          ← Wizard de boas-vindas
│
├── 📁 assinaturas/           ← FUNCIONA SOZINHO (não precisa mexer)
│   ├── models.py            ← Planos e assinaturas
│   ├── stripe_integration   ← Pagamentos Stripe
│   └── asaas_integration    ← Pagamentos Asaas (PIX/Boleto)
│
├── 📁 core/
│   ├── views.py             ← Login, dashboard (mexe aqui)
│   ├── middleware.py        ← Limites automáticos (FUNCIONA SOZINHO)
│   └── onboarding_views.py  ← Wizard de setup (FUNCIONA SOZINHO)
│
└── 📁 config/
    ├── settings.py          ← Configurações (mexe 1x no deploy)
    └── urls.py              ← Rotas (raramente mexe)
```

---

## 🔥 Tarefas do Dia a Dia

### 1. Cliente pediu novo campo no agendamento

**Exemplo:** "Quero campo de observações"

```python
# agendamentos/models.py
class Agendamento(models.Model):
    # ... campos existentes ...
    observacoes = models.TextField(blank=True)  # ← ADICIONAR ESTA LINHA
```

```bash
python manage.py makemigrations
python manage.py migrate
```

```html
<!-- templates/agendamentos/criar.html -->
<textarea name="observacoes" placeholder="Observações"></textarea>
```

**Pronto!** 3 linhas de código.

---

### 2. Ver por que mensagem WhatsApp não chegou

```bash
# Acessar admin
# URL: https://seu-dominio.com/admin/
# Ir em: Agendamentos → Logs de mensagens bot
# Filtrar por telefone do cliente
# Ver campo "Status" e "Erro detalhes"
```

**0 linhas de código!** Só olhar no admin.

---

### 3. Cliente não consegue agendar (limite)

**Opção 1 - Cliente faz upgrade:**
- Cliente acessa `/configuracoes/assinatura/`
- Escolhe plano maior
- Paga

**Opção 2 - Você remove limite:**
```python
# Django shell
from assinaturas.models import Plano
plano = Plano.objects.get(nome='essencial')
plano.max_agendamentos_mes = 99999
plano.save()
```

**Opção 3 - Você desativa limites para todos:**
```python
# config/settings.py linha 45
# 'core.middleware.LimitesPlanoMiddleware',  # ← Adicionar # (comentar)
```

---

### 4. Adicionar novo cliente (empresa)

**Jeito fácil - Via Admin:**
1. `/admin/empresas/empresa/add/`
2. Preencher: Nome, Slug, Email
3. Salvar
4. `/admin/assinaturas/assinatura/add/`
5. Escolher empresa, plano, status=ativa, expira=daqui 1 ano
6. `/admin/auth/user/add/`
7. Criar usuário admin para a empresa

**Jeito rápido - Via Script:**
```python
# Copiar script do arquivo docs/COMO_SIMPLIFICAR.md
# "Script 3: Criar empresa sem auto-provisioning"
```

---

## 🆘 Problemas Comuns

### "Sistema fora do ar"

```bash
sudo systemctl status gestto    # Ver se Django está rodando
sudo systemctl restart gestto   # Reiniciar se precisar
```

### "Erro no webhook do WhatsApp"

1. Evolution API está configurada?
2. URL correta: `https://dominio.com/api/whatsapp-webhook/`
3. Instance ID bate com o cadastrado?

### "Pagamento não ativou assinatura"

```python
# Ativar manualmente (Django shell)
from assinaturas.models import Assinatura
a = Assinatura.objects.get(empresa__slug='cliente')
a.status = 'ativa'
a.save()
```

---

## 🎚️ 3 Níveis de Complexidade

### Nível 1: SIMPLES (Recomendado para começar)
```python
# config/settings.py
MIDDLEWARE = [
    # ... middlewares padrão do Django ...

    'core.middleware.AssinaturaExpiracaoMiddleware',  # Só avisos
    # 'core.middleware.LimitesPlanoMiddleware',       # ← COMENTADO = sem bloqueios
    'core.middleware.UsageTrackingMiddleware',
]
```

**Resultado:**
- ✅ Multi-tenant funciona
- ✅ Avisos de expiração
- ❌ Sem bloqueios por limite
- ✅ Você controla manualmente

### Nível 2: INTERMEDIÁRIO (SaaS sem pagamento automático)
```python
MIDDLEWARE = [
    # ... todos ativos ...
    'core.middleware.AssinaturaExpiracaoMiddleware',
    'core.middleware.LimitesPlanoMiddleware',       # ← ATIVO
    'core.middleware.UsageTrackingMiddleware',
]

# Mas você cria clientes manualmente no admin
# E cobra manualmente (boleto, PIX)
```

**Resultado:**
- ✅ Multi-tenant funciona
- ✅ Limites automáticos
- ❌ Sem Stripe/Asaas
- ✅ Cobrança manual

### Nível 3: COMPLETO (Full SaaS)
```python
# Tudo ativo
# Stripe/Asaas funcionando
# Auto-provisioning de clientes
# Cobranças automáticas
```

**Resultado:**
- ✅ Sistema 100% automatizado
- ✅ Clientes se cadastram sozinhos
- ✅ Pagamentos automáticos
- 🔴 Mais complexo para manter

---

## 📊 Você Decide

| Pergunta | Resposta Sim | Resposta Não |
|----------|--------------|--------------|
| Vai ter +1 cliente? | Use Nível 1 ou 2 | Pode usar single-tenant |
| Quer cobrar automático? | Use Nível 3 | Use Nível 1 ou 2 |
| Quer bloquear por limite? | Use Nível 2 ou 3 | Use Nível 1 |
| Quer o mais simples? | Use Nível 1 | Use single-tenant |

---

## ⚡ TL;DR (Muito Longo; Não Li)

**Para 99% dos casos, use isto:**

1. Mantenha sistema como está
2. Comente **só** esta linha: `# 'core.middleware.LimitesPlanoMiddleware',`
3. Crie clientes manualmente no Admin Django
4. Cobre manualmente (PIX/boleto)
5. Pronto! Sistema funcionando sem complexidade

**Se precisar ajuda:**
- Leia: `docs/GUIA_MANUTENCAO_SIMPLES.md`
- Ou: `docs/COMO_SIMPLIFICAR.md`

---

**Respira fundo. Você consegue. O sistema não é um bicho de 7 cabeças! 💪**
