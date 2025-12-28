# 📊 Comparação: Templates n8n VPS

## 🎯 Qual template usar?

Você tem **3 opções** de templates para VPS (sem sistema de credenciais):

---

## 📦 Versão 1: VPS Básico (Original)

**Arquivo:** `TEMPLATE_Bot_Universal_VPS.json`

### ✅ Características:
- Usa variáveis de ambiente: `$env.DJANGO_API_KEY`
- System prompt técnico e objetivo
- Temperature 0.7
- Respostas funcionais mas diretas

### 👍 Vantagens:
- ✅ Mais seguro (chaves em variáveis de ambiente)
- ✅ Fácil de versionar (workflow não contém chaves)
- ✅ Centralizado (um .env para todos os workflows)

### 👎 Desvantagens:
- ❌ Precisa configurar docker-compose.yml ou .env
- ❌ Precisa reiniciar n8n para mudar valores
- ❌ System prompt menos humanizado

### 🎯 Melhor para:
- Produção com múltiplos workflows
- Ambientes com acesso a variáveis de ambiente
- Quando segurança é prioridade

### 📝 Configuração:

```yaml
# docker-compose.yml
environment:
  - DJANGO_API_KEY=sua-chave
  - EVOLUTION_API_KEY=sua-chave
  - OPENAI_API_KEY=sk-proj-xxx
```

---

## 🌙 Versão 2: VPS Humanizado

**Arquivo:** `TEMPLATE_Bot_Universal_VPS_Humanizado.json`

### ✅ Características:
- Usa variáveis de ambiente: `$env.OPENAI_API_KEY`
- System prompt super humanizado (Luna 🌙)
- Temperature 0.8
- Respostas empáticas e naturais
- Node extra para formatar confirmação

### 👍 Vantagens:
- ✅ Comunicação muito natural
- ✅ Clientes sentem mais empatia
- ✅ Resposta personalizada por contexto
- ✅ Tratamento de erro amigável

### 👎 Desvantagens:
- ❌ Precisa configurar variáveis de ambiente
- ❌ Precisa reiniciar n8n
- ❌ Workflow um pouco mais complexo

### 🎯 Melhor para:
- Empresas que querem comunicação muito natural
- Clientes que valorizam atendimento humanizado
- Quando qualidade da comunicação é prioridade

### 📝 Diferencial:

```json
{
  "resposta_amigavel": "Maravilha! Agendado: Barba com o João amanhã às 14h. Te aguardamos! 💈"
}
```

---

## ⚡ Versão 3: VPS Simplificado (RECOMENDADO)

**Arquivo:** `TEMPLATE_Bot_Universal_VPS_Simplificado.json`

### ✅ Características:
- **URLs definidas no node "Configurações + Dados"**
- API Keys: tenta variável de ambiente, senão usa valor do node
- System prompt super humanizado (Luna 🌙)
- Temperature 0.8
- Respostas empáticas e naturais

### 👍 Vantagens:
- ✅ **Configuração visual** (edita direto no node)
- ✅ **Sem restart** (salva e já funciona)
- ✅ **Híbrido** (usa env var se existir, senão usa valor direto)
- ✅ **Fácil de duplicar** (importa, edita URLs, pronto)
- ✅ **Comunicação humanizada**
- ✅ **Melhor para VPS**

### 👎 Desvantagens:
- ⚠️ API Keys ficam visíveis no workflow (se não usar env vars)
- ⚠️ Precisa editar em cada workflow duplicado

### 🎯 Melhor para:
- **VPS self-hosted** (SUA SITUAÇÃO!)
- Quem quer configuração rápida e visual
- Testes e desenvolvimento
- Quando você quer ver tudo em um lugar

### 📝 Configuração:

**No node "⚙️ Configurações + Dados":**

```javascript
// URLs (OK expor)
config_django_url: "https://axiogestto.com"
config_evolution_url: "https://evolution.axiodev.cloud"

// API Keys (preferível em variáveis de ambiente, mas pode colocar direto)
config_django_key: "{{ $env.DJANGO_API_KEY || 'SUA-CHAVE-AQUI' }}"
config_evolution_key: "{{ $env.EVOLUTION_API_KEY || 'SUA-CHAVE-AQUI' }}"
config_openai_key: "{{ $env.OPENAI_API_KEY || 'sk-proj-AQUI' }}"
```

**Como funciona:**
1. Primeiro tenta pegar da variável de ambiente
2. Se não existir, usa o valor que você colocou direto
3. **Melhor dos dois mundos!**

---

## 📊 Tabela Comparativa

| Critério | VPS Básico | VPS Humanizado | VPS Simplificado ⭐ |
|----------|------------|----------------|---------------------|
| **Facilidade de setup** | ⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Configuração visual** | ❌ | ❌ | ✅ |
| **Sem restart n8n** | ❌ | ❌ | ✅ |
| **Segurança** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **Humanização** | ⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Empatia** | ⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Fácil duplicar** | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Versionamento** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| **Melhor para VPS** | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |

---

## 🎯 Recomendação por Cenário

### **Você está em VPS self-hosted** ✅ SUA SITUAÇÃO
👉 **Use: VPS Simplificado**
- Configuração mais rápida
- Tudo visual
- Sem restart

### **Você tem acesso a variáveis de ambiente e quer máxima segurança**
👉 **Use: VPS Humanizado**
- Chaves em variável de ambiente
- Comunicação top
- Mais seguro

### **Você quer algo funcional rápido para testar**
👉 **Use: VPS Básico**
- Setup rápido
- Funcional
- Depois migra para Simplificado

---

## 🚀 Como Migrar Entre Versões

### De Básico → Simplificado:

1. Importe `TEMPLATE_Bot_Universal_VPS_Simplificado.json`
2. Abra node "⚙️ Configurações + Dados"
3. Cole suas URLs e chaves
4. Salve e ative

### De Simplificado → Humanizado:

1. Configure variáveis de ambiente
2. Importe `TEMPLATE_Bot_Universal_VPS_Humanizado.json`
3. Reinicie n8n
4. Ative workflow

---

## 💡 Dicas de Uso

### **Para Produção:**

**Opção A (Mais Segura):**
- Use VPS Simplificado
- Configure variáveis de ambiente para API Keys
- Deixe apenas URLs no node

**Opção B (Mais Prática):**
- Use VPS Simplificado
- Coloque tudo direto no node
- ⚠️ Não comite o workflow em repositório público

### **Para Desenvolvimento:**

- Use VPS Simplificado
- Coloque valores de teste direto no node
- Rápido para iterar e testar

### **Para Múltiplas Empresas:**

- Importe VPS Simplificado
- Duplique o workflow para cada empresa
- Edite URLs/chaves em cada um
- Renomeie: "Bot Empresa 1", "Bot Empresa 2", etc.

---

## ⚙️ Personalização Adicional

### **Mudar o nome da assistente:**

Todas as 3 versões permitem personalizar. Edite o system prompt:

```javascript
// Trocar de "Luna" para outro nome
"Você é Luna, a recepcionista virtual..."

// Para:
"Você é Ana, a recepcionista virtual..."
```

### **Ajustar tom de voz:**

```javascript
// Mais formal
"Você é profissional, educada e cordial"

// Mais descontraído (barbearia)
"Você é descontraído, usa gírias leves e emojis de barbearia"

// Mais técnico (clínica)
"Você é profissional, empática e transmite confiança"
```

### **Mudar temperatura:**

```json
{
  "temperature": 0.5  // Mais conservador
  "temperature": 0.8  // Padrão (recomendado)
  "temperature": 1.2  // Mais criativo
}
```

---

## ✅ Conclusão

**Para VPS self-hosted (sua situação):**

🏆 **RECOMENDADO: VPS Simplificado**

### Por quê?
1. ✅ Configuração 100% visual
2. ✅ Sem dependência de variáveis de ambiente
3. ✅ Sem reiniciar n8n
4. ✅ Comunicação super humanizada
5. ✅ Fácil de duplicar e personalizar

### Como começar:
1. Importe `TEMPLATE_Bot_Universal_VPS_Simplificado.json`
2. Clique no node "⚙️ Configurações + Dados"
3. Edite os 5 valores de config
4. Salve (Ctrl+S)
5. Ative e teste! 🚀

---

## 📚 Documentação Relacionada

- `N8N_HUMANIZACAO_IA.md` - Como funciona a humanização
- `N8N_VPS_SETUP.md` - Setup com variáveis de ambiente
- `N8N_TEMPLATE_GUIDE.md` - Guia do template SaaS (com credenciais)
- `N8N_DYNAMIC_WORKFLOWS.md` - Por que dinâmico é melhor que estático

---

**Ficou com dúvida em qual usar?**

👉 **Use VPS Simplificado.** É o melhor para VPS! ⚡
