## 🚀 Melhorias Implementadas

### Landing Page Single-Page
- ✅ Navegação suave com âncoras (#inicio, #precos, #sobre, #contato)
- ✅ Seção de preços integrada (R$ 79,99 e R$ 199,99)
- ✅ Layout padronizado em todas as páginas
- ✅ Scroll suave entre seções

### 🔒 Melhorias de Segurança
- ✅ **Rate Limiting** (django-ratelimit)
  - Home: 60 req/min por IP
  - Cadastro: 10 cadastros/hora por IP
- ✅ **Logs Separados**
  - `data/logs/landing.log` - Atividade da LP
  - `data/logs/security.log` - Eventos de segurança
  - `data/logs/app.log` - Logs gerais
- ✅ **Proteção Brute Force** (django-axes)
  - Bloqueia após 5 tentativas falhas
  - Bloqueio por 1 hora
- ✅ **Middleware de Monitoramento**
  - Detecção SQL Injection
  - Detecção XSS
  - Bloqueio de paths suspeitos
  - Headers de segurança adicionais
- ✅ **Documentação** completa em `docs/SEGURANCA_LP.md`

### 🐛 Correções CI/CD
- ✅ Corrigir warnings do django-axes (settings deprecated)
- ✅ Adicionar `corsheaders` ao INSTALLED_APPS
- ✅ Testes passando localmente

## 📋 Checklist

- [x] Código testado localmente
- [x] `python manage.py check` sem erros
- [x] Migrations criadas e testadas
- [x] Documentação atualizada
- [x] Requirements.txt atualizado

## 🔗 Commits Incluídos

- e25ad9d - feat: landing page single-page + melhorias de segurança
- 8af1431 - fix: corrigir warnings do django-axes
- 7b950e4 - fix: adicionar corsheaders ao INSTALLED_APPS

## ⚠️ Ações Necessárias no Servidor

Após merge e deploy:
```bash
pip install -r requirements.txt  # Novos pacotes
python manage.py migrate         # Novas migrations do axes
mkdir -p data/logs              # Criar pasta de logs
```

---
🤖 Generated with [Claude Code](https://claude.com/claude-code)
