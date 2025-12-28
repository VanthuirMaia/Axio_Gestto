# 📚 Documentação Gestto

Bem-vindo à documentação do **Gestto** - Sistema de Gestão com Agendamentos Automáticos via WhatsApp.

---

## 📖 Índice

### 🚀 Início Rápido

Para começar rapidamente:
1. **[Quick Start](../QUICK_START_AMBIENTES.md)** - Guia rápido de 5 minutos
2. **[Configuração de Ambientes](configuracao/ambientes.md)** - Dev e Produção
3. **[Variáveis de Ambiente](configuracao/variaveis-ambiente.md)** - .env explicado

---

## 🔧 Configuração

Guias para configurar o projeto:

| Documento | Descrição |
|-----------|-----------|
| **[Ambientes Dev/Prod](configuracao/ambientes.md)** | Sistema de ambientes separados |
| **[Variáveis de Ambiente](configuracao/variaveis-ambiente.md)** | Estrutura de .env |
| **[Email - Brevo](configuracao/email-brevo.md)** | Configurar SMTP Brevo |
| **[Sistema de Email](configuracao/email-sistema.md)** | Emails automáticos e templates |

---

## 🚢 Deploy

Guias de deploy e produção:

| Documento | Descrição |
|-----------|-----------|
| **[Guia de Deploy](deploy/guia-deploy.md)** | Deploy completo em produção |

---

## 🔌 Integrações

Integração com serviços externos:

| Documento | Descrição |
|-----------|-----------|
| **[Evolution API](integracao/evolution-api.md)** | WhatsApp via Evolution API |
| **[N8N](integracao/n8n.md)** | Automações e bot inteligente |
| **[Stripe](integracao/stripe.md)** | Pagamentos online |

---

## 💻 Desenvolvimento

Guias para desenvolvedores:

| Documento | Descrição |
|-----------|-----------|
| **[Arquitetura](desenvolvimento/arquitetura.md)** | Estrutura do projeto |
| **[Responsividade](desenvolvimento/responsividade.md)** | Sistema responsivo implementado |
| **[Eventos Recorrentes](desenvolvimento/eventos-recorrentes.md)** | Sistema de recorrência |

---

## ⚙️ Operação

Guias operacionais:

| Documento | Descrição |
|-----------|-----------|
| **[Criar Empresa Manualmente](operacao/criar-empresa.md)** | Como criar empresas via admin |
| **[Guia de Manutenção](operacao/manutencao.md)** | Manutenção e troubleshooting |

---

## 📦 Arquivos Arquivados

Documentação antiga e histórica foi movida para [`arquivados/`](arquivados/).

Esses arquivos são mantidos para referência histórica, mas não fazem parte da documentação ativa.

---

## 🌳 Estrutura da Documentação

```
docs/
├── README.md                    # Este arquivo (índice)
├── configuracao/                # Configuração do projeto
│   ├── ambientes.md
│   ├── variaveis-ambiente.md
│   ├── email-brevo.md
│   └── email-sistema.md
├── deploy/                      # Deploy e produção
│   └── guia-deploy.md
├── integracao/                  # Integrações externas
│   ├── evolution-api.md
│   ├── n8n.md
│   └── stripe.md
├── desenvolvimento/             # Guias para devs
│   ├── arquitetura.md
│   ├── responsividade.md
│   └── eventos-recorrentes.md
├── operacao/                    # Operação e manutenção
│   ├── criar-empresa.md
│   └── manutencao.md
└── arquivados/                  # Documentação antiga (54 arquivos)
```

---

## 📊 Estatísticas

- **Total de arquivos:** 13 ativos + 54 arquivados = 67
- **Redução:** De 69 arquivos soltos → 13 organizados (**81% mais organizado**)
- **Estrutura:** 5 categorias temáticas

---

## 🎯 Próximos Passos

Esta estrutura está preparada para:

1. **Geração automática de documentação** (MkDocs, Sphinx, etc)
2. **Publicação em GitHub Pages**
3. **Versionamento claro** da documentação
4. **Fácil manutenção** e atualização

---

## 💡 Como Contribuir

Para adicionar ou atualizar documentação:

1. **Identifique a categoria** apropriada
2. **Crie/edite o arquivo** na pasta correta
3. **Atualize este README.md** se necessário
4. **Commit com mensagem descritiva**

**Exemplo:**
```bash
# Adicionar novo documento de integração
touch docs/integracao/nova-api.md
# Editar o arquivo
# Atualizar docs/README.md se necessário
git add docs/
git commit -m "docs: adicionar integração Nova API"
```

---

## 📞 Suporte

- **Issues:** [GitHub Issues](https://github.com/VanthuirMaia/Axio_Gestto/issues)
- **Documentação Principal:** Este arquivo
- **Quick Start:** [`QUICK_START_AMBIENTES.md`](../QUICK_START_AMBIENTES.md)

---

**Última atualização:** 28/12/2025
**Versão da documentação:** 2.0 (reorganizada)
