# 🔄 Como Atualizar os Planos com Novos Preços

## Novos Valores (Atualizados)

| Plano | Profissionais | Preço |
|-------|---------------|-------|
| **Essencial** | 1 | R$ 49 |
| **Profissional** | 4 | R$ 179 |
| **Empresarial** | 8 | R$ 399 |

---

## Opção 1: Banco de Dados VAZIO (Recomendado)

Se você ainda **NÃO carregou** os planos no banco:

```bash
python manage.py loaddata assinaturas/fixtures/planos_iniciais.json
```

**Pronto!** Os planos serão criados com os valores corretos.

---

## Opção 2: Banco de Dados JÁ TEM planos (Atualizar)

Se você **JÁ carregou** os planos antigos:

### Via Django Shell (Rápido):

```bash
python manage.py shell
```

```python
from assinaturas.models import Plano

# Atualizar Profissional
prof = Plano.objects.get(nome='profissional')
prof.preco_mensal = 179.00
prof.max_profissionais = 4
prof.save()

# Atualizar Empresarial
emp = Plano.objects.get(nome='empresarial')
emp.preco_mensal = 399.00
emp.max_profissionais = 8
emp.save()

print("Planos atualizados!")
exit()
```

### Via Admin Django (Visual):

1. Acessar: `http://localhost:8000/admin/`
2. Ir em: **Assinaturas → Planos**
3. Editar **Profissional**:
   - Preço mensal: `179.00`
   - Max profissionais: `4`
   - Salvar
4. Editar **Empresarial**:
   - Preço mensal: `399.00`
   - Max profissionais: `8`
   - Salvar

---

## ⚠️ IMPORTANTE

### Assinaturas Existentes

**Planos já criados NÃO mudam automaticamente!**

Se já tem clientes com assinaturas antigas:
- ✅ Novos clientes usarão os novos valores
- ❌ Clientes antigos continuam com valores antigos (correto!)

### Para migrar clientes antigos:

**Opção A - Manually via Admin:**
1. Admin → Assinaturas → Assinaturas
2. Editar assinatura do cliente
3. Trocar o plano
4. Salvar

**Opção B - Script (se tiver muitos):**

```python
# Django shell
from assinaturas.models import Assinatura

# Atualizar TODAS as assinaturas do plano Profissional
assinaturas = Assinatura.objects.filter(plano__nome='profissional')
for assinatura in assinaturas:
    # Não precisa fazer nada, o plano já foi atualizado
    # Mas se quiser resetar a data de expiração:
    # assinatura.data_expiracao = now() + timedelta(days=30)
    # assinatura.save()
    pass

print(f"{assinaturas.count()} assinaturas afetadas")
```

---

## 🔄 No Stripe/Asaas

**ATENÇÃO:** Você também precisa atualizar os produtos nos gateways!

### Stripe:
1. https://dashboard.stripe.com/test/products
2. Editar produto "Plano Profissional"
3. Mudar preço para R$ 179 (ou USD equivalente)
4. Salvar
5. **Copiar o NOVO price_id**
6. Atualizar no Admin Django (campo `stripe_price_id`)

### Asaas:
1. Painel Asaas → Planos
2. Editar plano correspondente
3. Atualizar valor
4. Salvar

---

## ✅ Verificação

Após atualizar, confirme:

```python
# Django shell
from assinaturas.models import Plano

planos = Plano.objects.all()
for plano in planos:
    print(f"{plano.get_nome_display()}: R$ {plano.preco_mensal} - {plano.max_profissionais} prof")

# Deve mostrar:
# Essencial: R$ 49.00 - 1 prof
# Profissional: R$ 179.00 - 4 prof
# Empresarial: R$ 399.00 - 8 prof
```

---

**Atualizado em:** 25/12/2025
