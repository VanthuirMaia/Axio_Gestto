# Scripts de Debug e Testes

Scripts úteis para desenvolvimento, testes e troubleshooting do sistema.

## 📝 Scripts Disponíveis

### `testar_evolution_api.py`
Testa conexão com Evolution API.

```bash
python scripts/debug/testar_evolution_api.py
```

**O que faz:**
- Verifica se EVOLUTION_API_URL e EVOLUTION_API_KEY estão configurados
- Testa endpoint /instance/fetchInstances
- Lista instâncias ativas
- Opcionalmente cria instância de teste

### `listar_usuarios.py`
Lista todos os usuários e suas empresas/assinaturas.

```bash
python scripts/debug/listar_usuarios.py
```

**O que faz:**
- Lista todos os usuários do sistema
- Mostra empresa associada
- Mostra status da assinatura
- Útil para debug de multi-tenancy

### `verificar_ultima_empresa.py`
Verifica dados da última empresa criada.

```bash
python scripts/debug/verificar_ultima_empresa.py
```

**O que faz:**
- Mostra detalhes da última empresa cadastrada
- Útil após cadastros via landing page

### `teste_cadastro.py`
Testa fluxo de cadastro completo.

```bash
python scripts/debug/teste_cadastro.py
```

**O que faz:**
- Simula cadastro de nova empresa
- Testa integração com Stripe
- Valida criação de assinatura

### `testar_webhook.py`
Testa processamento de webhooks do Stripe.

```bash
python scripts/debug/testar_webhook.py
```

**O que faz:**
- Simula eventos do Stripe
- Testa ativação de assinaturas
- Verifica processamento de pagamentos

## 🚨 Atenção

Estes scripts são apenas para **desenvolvimento e debug**.

**Não executar em produção** sem revisar o código antes.
