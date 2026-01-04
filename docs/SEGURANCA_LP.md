# 🔒 Melhorias de Segurança na Landing Page

## Implementações Realizadas (Janeiro 2026)

### 1. **Rate Limiting**

Limites de requisições implementados para prevenir abuso e ataques DDoS:

#### Views Protegidas:
- **Home** (`/`): 60 requisições/minuto por IP
- **Cadastro GET** (`/cadastro`): 30 requisições/minuto por IP
- **Cadastro POST** (`/cadastro`): 10 cadastros/hora por IP ⚠️

**Biblioteca:** `django-ratelimit 4.1.0`

**Como funciona:**
```python
@ratelimit(key='ip', rate='10/h', method='POST', block=True)
def cadastro(request):
    # Se exceder limite, retorna HTTP 429 (Too Many Requests)
```

**Benefícios:**
- ✅ Previne cadastros em massa (spam)
- ✅ Protege contra scraping agressivo
- ✅ Reduz carga no servidor

---

### 2. **Logging Separado e Estruturado**

Sistema de logs dedicado para monitoramento da landing page:

#### Arquivos de Log:
- `data/logs/landing.log` - Logs específicos da LP (acessos, cadastros, erros)
- `data/logs/security.log` - Eventos de segurança (ataques, bloqueios)
- `data/logs/app.log` - Logs gerais da aplicação

#### Tipos de Eventos Logados:

**Landing Page:**
```
[INFO] Acesso à home - IP: 200.123.45.67
[WARNING] Tentativa de cadastro - IP: 200.123.45.67, Email: teste@teste.com
[ERROR] Erro na API de cadastro - Email: teste@teste.com, Erro: CNPJ inválido
```

**Segurança:**
```
[WARNING] [SUSPEITO] Acesso a path suspeito: /admin | IP: 1.2.3.4
[CRITICAL] [ATAQUE] Possível SQL Injection detectado! Query: ?id=1' OR '1'='1
```

**Configuração:**
- Rotação automática a cada 10MB
- Mantém 5 backups de cada arquivo
- Formato: `[LEVEL] YYYY-MM-DD HH:MM:SS modulo - mensagem`

---

### 3. **Django Axes - Proteção contra Brute Force**

Monitoramento e bloqueio automático de tentativas de login maliciosas:

**Biblioteca:** `django-axes 8.1.0`

**Configurações:**
- Bloqueia após **5 tentativas falhas**
- Tempo de bloqueio: **1 hora**
- Bloqueio por **combinação de username + IP** (mais seguro)
- Logs detalhados de todas as tentativas

**Funcionalidades:**
- ✅ Detecta e bloqueia ataques de força bruta
- ✅ Rastreia tentativas de acesso ao admin
- ✅ Integração com sistema de logging
- ✅ Dashboard no admin Django (`/admin/axes/`)

---

### 4. **Middleware de Monitoramento Personalizado**

**Arquivo:** `landing/middleware.py`

#### Detecção de Ameaças:

**a) Paths Suspeitos:**
```python
SUSPICIOUS_PATHS = ['/admin', '/.env', '/.git', '/wp-admin', '/phpmyadmin']
```

**b) User-Agents Suspeitos:**
```python
SUSPICIOUS_USER_AGENTS = ['sqlmap', 'nikto', 'nmap', 'curl', 'wget']
```

**c) SQL Injection:**
- Detecta: `union`, `select`, `drop`, `--`, `'`
- **Ação:** Bloqueia e loga como CRITICAL

**d) XSS (Cross-Site Scripting):**
- Detecta: `<script`, `javascript:`
- **Ação:** Bloqueia e loga como CRITICAL

#### Monitoramento de Performance:
- Detecta requisições > 2 segundos
- Loga requests lentos para otimização

#### Headers de Segurança Adicionados:
```http
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
Referrer-Policy: strict-origin-when-cross-origin
Permissions-Policy: geolocation=(), microphone=(), camera=()
```

---

## 📊 Como Monitorar

### 1. **Visualizar Logs em Tempo Real:**

```bash
# Landing page
tail -f data/logs/landing.log

# Segurança
tail -f data/logs/security.log

# Geral
tail -f data/logs/app.log
```

### 2. **Buscar Eventos Específicos:**

```bash
# Tentativas de cadastro
grep "Tentativa de cadastro" data/logs/landing.log

# Ataques bloqueados
grep "ATAQUE" data/logs/security.log

# IPs bloqueados
grep "rate limit" data/logs/landing.log
```

### 3. **Django Admin:**

Acesse: `http://localhost:8000/admin/axes/`

- **AccessAttempt:** Tentativas de login falhadas
- **AccessLog:** Histórico de acessos
- **AccessFailureLog:** Bloqueios ativos

---

## 🚨 Alertas e Respostas

### Rate Limit Atingido:
```
Response: HTTP 429 Too Many Requests
Mensagem: "Muitas requisições. Tente novamente mais tarde."
```

### Ataque Detectado:
```
Response: HTTP 403 Forbidden
Mensagem: "Requisição inválida"
Log: [CRITICAL] [ATAQUE] Possível SQL Injection detectado!
```

### Brute Force Bloqueado:
```
Response: HTTP 403 Forbidden (Axes)
Log: [WARNING] Usuário bloqueado por tentativas excessivas
Duração: 1 hora
```

---

## 🔧 Manutenção

### Limpar Bloqueios Antigos:

```bash
# Django Axes
python manage.py axes_reset

# Por IP específico
python manage.py axes_reset_ip 1.2.3.4

# Por username
python manage.py axes_reset_username admin
```

### Limpar Logs Antigos:

```bash
# Manter apenas últimos 30 dias
find data/logs -name "*.log.*" -mtime +30 -delete
```

---

## 📈 Próximos Passos (Médio Prazo)

1. **WAF (Web Application Firewall)**
   - Cloudflare ou AWS WAF
   - Proteção adicional contra DDoS

2. **Desacoplamento Total**
   - Landing page estática (Vercel/Netlify)
   - API Django isolada
   - Zero acesso ao banco principal

3. **Monitoramento Proativo**
   - Sentry para erro tracking
   - Grafana + Prometheus para métricas
   - Alertas via Telegram/Slack

4. **Honeypots**
   - Campos invisíveis para detectar bots
   - Endpoints fake para rastrear scanners

---

## 🎯 Resumo

**Status:** ✅ **Produção-Ready com Medidas de Curto Prazo**

| Proteção | Status | Nível |
|----------|--------|-------|
| Rate Limiting | ✅ Ativo | Médio |
| Logs Separados | ✅ Ativo | Alto |
| Brute Force Protection | ✅ Ativo | Alto |
| SQL Injection Detection | ✅ Ativo | Alto |
| XSS Detection | ✅ Ativo | Alto |
| Headers de Segurança | ✅ Ativo | Médio |
| Performance Monitoring | ✅ Ativo | Baixo |

**Recomendação:** Sistema seguro para produção. Para maior robustez, implementar desacoplamento (médio prazo).

---

**Última atualização:** 04/01/2026
**Responsável:** Claude Code + Equipe Axio
