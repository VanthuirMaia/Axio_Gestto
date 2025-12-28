# Comandos para Deploy SaaS

## 📦 FASE 1: Models e Migrations (CONCLUÍDO ✅)

### Arquivos criados:
- ✅ `assinaturas/` - Novo app
- ✅ `assinaturas/models.py` - Plano, Assinatura, HistoricoPagamento
- ✅ `assinaturas/admin.py` - Interface admin completa
- ✅ `assinaturas/fixtures/planos_iniciais.json` - 3 planos (Essencial, Profissional, Empresarial)
- ✅ `empresas/models.py` - Atualizado com campos SaaS
- ✅ `config/settings.py` - App assinaturas adicionado

### Comandos para rodar na VPS:

```bash
# 1. Entrar no container Django
docker-compose exec web bash

# 2. Criar migrations
python manage.py makemigrations empresas
python manage.py makemigrations assinaturas

# 3. Aplicar migrations
python manage.py migrate

# 4. Carregar fixtures (planos iniciais)
python manage.py loaddata assinaturas/fixtures/planos_iniciais.json

# 5. Verificar se planos foram criados
python manage.py shell
>>> from assinaturas.models import Plano
>>> Plano.objects.all()
>>> exit()

# 6. Sair do container
exit
```

### Verificações:
- [ ] 3 planos criados (Essencial R$49, Profissional R$149, Empresarial R$299)
- [ ] Admin acessível em /admin/assinaturas/
- [ ] Campos novos aparecendo no admin de Empresas

---

## 🔄 PRÓXIMOS PASSOS (EM DESENVOLVIMENTO)

### FASE 2: Integrações de Pagamento
- [ ] Stripe integration
- [ ] Asaas integration
- [ ] Endpoint create_tenant
- [ ] Webhooks

### FASE 3: Onboarding
- [ ] Views wizard 4 passos
- [ ] Templates
- [ ] Email boas-vindas

### FASE 4: WhatsApp Multi-Tenant
- [ ] Webhook único
- [ ] Roteamento automático

### FASE 5: Limites e Monitoramento
- [ ] Middleware
- [ ] Dashboard

---

## 🎯 Planos Criados

| Plano | Preço | Profissionais | Agend/Mês | Trial |
|-------|-------|---------------|-----------|-------|
| **Essencial** | R$ 49 | 1 | 500 | 7 dias |
| **Profissional** | R$ 149 | 5 | 2.000 | 14 dias |
| **Empresarial** | R$ 299 | Ilimitado | Ilimitado | 30 dias |

---

**Status:** ✅ Fase 1 completa - Models prontos para uso
**Próximo:** Começando Fase 2 - Integração Stripe/Asaas
