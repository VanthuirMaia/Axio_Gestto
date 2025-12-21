# 🚀 Gestto — Sistema de Gestão para Pequenos Negócios

Aplicação Django moderna para gerenciamento completo de salões, barbearias, estúdios e microempresas que dependem de agendamentos.

O sistema já implementa:

✔ Multi-tenant real (cada empresa tem seu ambiente e seus dados)  
✔ Agendamentos com FullCalendar moderno  
✔ Controle de clientes  
✔ Serviços e profissionais  
✔ Comissões  
✔ Dashboard e relatórios  
✔ API integrada  
✔ Integração com n8n (agendamentos automáticos via IA / WhatsApp)

---

## 📌 Funcionalidades Principais

### 🗓 Agendamentos Inteligentes

- Calendário FullCalendar totalmente integrado
- Exibição por mês, semana e dia
- Modal profissional com edição e exclusão
- Prevenção de conflitos de horário
- Cores personalizadas por status e por profissional
- Suporte a múltiplos profissionais
- Zona de tempo corrigida (America/Recife)

### 👤 Gestão de Clientes

- Cadastro simples e rápido
- Histórico de agendamentos
- Telefones e dados estruturados

### 💈 Serviços e Profissionais

- Duração do serviço
- Preço
- Comissão por profissional
- Cores personalizadas por profissional no calendário

### 💰 Financeiro

- Valores por atendimento
- Cálculo automático de comissão
- Relatórios futuros

### ⚙️ Empresa / Multi-tenant

- Cada empresa com seus próprios:
  - clientes
  - agendamentos
  - serviços
  - profissionais
- Logos e personalização futura

### 🤖 Integração com IA e n8n

- Webhooks para criar agendamentos automaticamente
- Futuro: IA sugerindo horários e confirmando clientes via WhatsApp

---

## 🛠 Instalação Local

### 1. Clone o repositório

```
git clone https://github.com/seu-repo.git
cd gestto
```

### 2. Crie um ambiente virtual

```
python -m venv venv
venv\Scripts\activate  # Windows
# ou
source venv/bin/activate  # Linux/Mac
```

### 3. Instale as dependências

```
pip install -r requirements.txt
```

### 4. Configure o banco

```
python manage.py migrate
python manage.py createsuperuser
```

### 5. Inicie a aplicação

```
python manage.py runserver
```

Acesse:  
👉 http://localhost:8000

---

## 🐳 Rodando com Docker

```
docker-compose up -d
```

Acesse:  
👉 http://localhost:8000

---

## 📁 Estrutura do Projeto

```
core/           # Autenticação, usuários e multi-tenant
empresas/       # Dados da empresa, serviços e profissionais
agendamentos/   # Lógica completa de calendário e agendamentos
clientes/       # Gerenciamento de clientes
financeiro/     # Comissões e controle financeiro
dashboard/      # Gráficos e indicadores
static/         # Arquivos estáticos
templates/      # Templates HTML
```

---

## 🔐 Variáveis de Ambiente

### Configuração Inicial

1. Copie o arquivo de exemplo:
```bash
cp .env.example .env
```

2. Gere uma SECRET_KEY segura:
```bash
python -c "import secrets; print(''.join(secrets.choice('abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)') for i in range(50)))"
```

3. Edite o `.env` e substitua os valores:

```env
# Django Core
SECRET_KEY=sua-chave-secreta-gerada-aqui
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database (SQLite por padrão, descomente para PostgreSQL)
# DB_ENGINE=django.db.backends.postgresql
# DB_NAME=gestao_negocios
# DB_USER=postgres
# DB_PASSWORD=postgres
# DB_HOST=localhost
# DB_PORT=5432

# CORS
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

**IMPORTANTE**:
- Nunca commite o arquivo `.env` no Git
- Use `.env.example` como template para outros desenvolvedores
- Em produção, sempre use `DEBUG=False` e uma SECRET_KEY única

---

## 📡 API

Endpoints disponíveis em `/api/`.

A autenticação é baseada em sessão (por enquanto).  
Futuro: JWT ou Tokens para integração profunda com n8n.

---

## 🧭 Roadmap — Próximas Releases

### 📌 Versão Atual (Feita)

- ✔ Calendário com FullCalendar
- ✔ Edição e exclusão via modal
- ✔ Cores por profissional
- ✔ Verificação de conflito
- ✔ Manter valores em caso de erro no formulário
- ✔ Timezone corrigido

### 📌 Versão 1.1 — Próximas entregas

- [ ] Arrastar eventos para mover horário
- [ ] Criar agendamento clicando no calendário
- [ ] Bloqueio de horários por folga/ausência
- [ ] Dashboard financeiro avançado
- [ ] API pública para integração externa
