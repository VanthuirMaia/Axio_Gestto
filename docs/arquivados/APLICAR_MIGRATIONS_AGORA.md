# 🚀 Aplicar Migrations e Testar - PASSO A PASSO

## ⚠️ IMPORTANTE: Docker Desktop precisa estar RODANDO!

---

## 📋 Passo 1: Iniciar Docker Desktop

1. **Abrir Docker Desktop** (ícone na barra de tarefas ou menu iniciar)
2. **Aguardar** até aparecer "Docker Desktop is running" (canto inferior esquerdo verde)
3. **Continuar** para os próximos passos

---

## 🔧 Passo 2: Subir os Containers

Abra o **PowerShell** ou **CMD** na pasta do projeto:

```powershell
cd D:\Axio\axio_gestto

# Subir todos os serviços
docker-compose up -d

# Aguardar containers iniciarem (30-60 segundos)
# Verificar status
docker-compose ps
```

**Saída esperada:**
```
NAME                IMAGE                COMMAND              STATUS
gestao_db           postgres:15          "docker-entrypoint"  Up (healthy)
gestao_redis        redis:7-alpine       "docker-entrypoint"  Up (healthy)
gestao_web          axio_gestto-web      "sh -c python..."    Up (healthy)
gestao_celery       axio_gestto-celery   "celery -A config"   Up
gestao_nginx        axio_gestto-nginx    "nginx -g 'daemon"   Up
```

---

## 🗄️ Passo 3: Criar Migrations

```powershell
# Criar migration para o model AgendamentoRecorrente
docker exec -it gestao_web python manage.py makemigrations agendamentos
```

**Saída esperada:**
```
Migrations for 'agendamentos':
  agendamentos/migrations/000X_agendamentorecorrente.py
    - Create model AgendamentoRecorrente
```

---

## ✅ Passo 4: Aplicar Migrations

```powershell
# Aplicar migrations no banco de dados
docker exec -it gestao_web python manage.py migrate
```

**Saída esperada:**
```
Operations to perform:
  Apply all migrations: agendamentos, auth, clientes, ...
Running migrations:
  Applying agendamentos.000X_agendamentorecorrente... OK
```

---

## 🔄 Passo 5: Restart Serviços

```powershell
# Restart para garantir que tudo está atualizado
docker-compose restart web celery
```

**Aguardar 10-15 segundos**

---

## 🧪 Passo 6: Testar a Interface

### 6.1. Acessar a Interface de Recorrências

Abra no navegador:
```
http://localhost/agendamentos/recorrencias/
```

**Deve aparecer:**
- Página com título "Agendamentos Recorrentes"
- Botão "Nova Recorrência"
- Mensagem "Nenhum agendamento recorrente" (se for primeira vez)

---

### 6.2. Criar Primeira Recorrência

1. **Clicar em** "Nova Recorrência"

2. **Preencher o formulário:**
   - **Cliente:** Selecione um cliente existente (se não tiver, crie um em /clientes/criar/)
   - **Serviço:** Selecione um serviço existente (se não tiver, crie um em /admin/)
   - **Profissional:** Selecione ou deixe vazio
   - **Frequência:** Semanal
   - **Dias da Semana:** Marque Segunda e Quarta
   - **Horário:** 10:00
   - **Válido a partir de:** Hoje (data atual)
   - **Válido até:** 7 dias a partir de hoje (ou deixe vazio)

3. **Clicar em** "Criar Recorrência"

**Deve aparecer:**
- Mensagem verde: "Recorrência criada com sucesso! Toda Segunda-feira, Quarta-feira às 10:00"
- Redirecionado para lista de recorrências
- Recorrência aparece na tabela com status "Ativo"

---

## 🎯 Passo 7: Gerar Agendamentos Manualmente (Teste)

```powershell
# Entrar no shell Python do Django
docker exec -it gestao_web python manage.py shell
```

Dentro do shell Python, executar:

```python
# Importar a task
from agendamentos.tasks import gerar_agendamentos_recorrentes

# Executar a task
resultado = gerar_agendamentos_recorrentes()

# Ver resultado
print(resultado)

# Deve mostrar algo como:
# {'total_criados': 2, 'total_pulados': 0, 'data_execucao': '2025-12-21T...'}

# Sair do shell
exit()
```

---

## 📅 Passo 8: Verificar Agendamentos no Calendário

1. **Acessar:** http://localhost/agendamentos/calendario/

2. **Verificar:**
   - Devem aparecer 2 agendamentos (segunda e quarta da próxima semana)
   - Clicar em um agendamento

3. **Modal deve mostrar:**
   - Cliente
   - Serviço
   - Profissional
   - Horário
   - **Nas notas:** "📅 Agendamento recorrente gerado automaticamente"

---

## 🎉 Passo 9: Verificar no Admin

1. **Acessar:** http://localhost/admin/

2. **Login:**
   - User: `admin`
   - Pass: `Admin@2025Secure!` (ou a senha que você configurou)

3. **Menu lateral:** Agendamentos → Agendamentos Recorrentes

4. **Deve mostrar:**
   - Lista com a recorrência criada
   - Campos: Cliente, Serviço, Frequência, Horário, Status (Ativo)

---

## ✅ Checklist de Verificação

Marque conforme for testando:

- [ ] Docker Desktop está rodando
- [ ] Containers estão UP (docker-compose ps)
- [ ] Migration criada sem erro (makemigrations)
- [ ] Migration aplicada sem erro (migrate)
- [ ] Interface /recorrencias/ acessível
- [ ] Conseguiu criar uma recorrência
- [ ] Task manual executou sem erro
- [ ] Resultado mostrou "total_criados" > 0
- [ ] Agendamentos aparecem no calendário
- [ ] Agendamentos têm a nota "📅 recorrente..."
- [ ] Admin mostra a recorrência

---

## 🐛 Troubleshooting

### Erro: "Docker is not running"
**Solução:** Inicie o Docker Desktop e aguarde ficar verde

### Erro: "No module named agendamentos"
**Solução:**
```powershell
docker-compose restart web
docker exec -it gestao_web python manage.py check
```

### Erro: "No such file or directory: migrations"
**Solução:**
```powershell
# Criar diretório de migrations se não existir
docker exec -it gestao_web mkdir -p agendamentos/migrations
docker exec -it gestao_web touch agendamentos/migrations/__init__.py
```

### Erro: "total_criados: 0"
**Possíveis causas:**
1. Data de início é futura demais (gera apenas próximos 60 dias)
2. Dias da semana não batem com próximos 7 dias
3. Horário já tem conflito

**Solução:** Criar recorrência com dias incluindo hoje/amanhã

### Erro: "Page not found /agendamentos/recorrencias/"
**Solução:**
```powershell
docker-compose restart web
# Aguardar 10 segundos
# Tentar novamente
```

---

## 📊 Comandos Úteis

```powershell
# Ver logs em tempo real
docker-compose logs -f web

# Ver logs do Celery
docker-compose logs -f celery

# Restart de tudo
docker-compose restart

# Parar tudo
docker-compose down

# Subir tudo novamente
docker-compose up -d

# Entrar no container web (para debug)
docker exec -it gestao_web bash
```

---

## 🎯 Próximos Passos Após Teste

Se tudo funcionou:

1. **Pausar uma recorrência:**
   - Na lista, clicar no botão ⏸️
   - Verificar que status muda para "Pausado"

2. **Reativar:**
   - Clicar no botão ▶️
   - Status volta para "Ativo"

3. **Excluir:**
   - Clicar no botão 🗑️
   - Confirmar exclusão
   - Recorrência some da lista
   - Agendamentos já criados **permanecem** no calendário

4. **Aguardar geração automática:**
   - À meia-noite (00:00), Celery Beat executará automaticamente
   - Novos agendamentos serão criados para os próximos 60 dias

---

## 🚀 Pronto!

Eventos Recorrentes estão **funcionando perfeitamente!**

**Documentação completa:** `EVENTOS_RECORRENTES.md`

---

**Qualquer erro, consulte a seção Troubleshooting acima! ✅**
