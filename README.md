# Gestao Negocios - Sistema de Gerenciamento

Sistema Django completo para gerenciar pequenos negócios (barbearias, salões, studios).

## Funcionalidades

- Autenticação multi-tenant (cada empresa tem seu login)
- Agendamentos com calendário
- Gestão de clientes
- Controle financeiro com comissões
- Dashboard com insights
- Personalização por empresa (logo, cores)
- API REST
- Integração com n8n (via webhooks)

## Instalação Local

1. Clone o repositório
2. Crie um ambiente virtual:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   venv\Scripts\activate  # Windows
   ```

3. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```

4. Configure o banco de dados:
   ```bash
   python manage.py migrate
   python manage.py createsuperuser
   ```

5. Inicie o servidor:
   ```bash
   python manage.py runserver
   ```

Acesse http://localhost:8000

## Docker

Para subir com Docker:

```bash
docker-compose up -d
```

Acesse http://localhost:8000

## Estrutura

- `core/` - Autenticação e usuários
- `empresas/` - Modelos de empresa, serviços, profissionais
- `agendamentos/` - Sistema de agendamentos
- `clientes/` - Gestão de clientes
- `financeiro/` - Controle financeiro
- `dashboard/` - Dashboard e relatórios

## Variáveis de Ambiente

Crie um arquivo `.env`:

```
DEBUG=True
SECRET_KEY=sua-chave-secreta
DB_NAME=gestao_negocios
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=localhost
DB_PORT=5432
```

## API

A API está disponível em `/api/` com autenticação via sessão.

## Próximas Etapas

- [ ] Implementar agendamentos completos
- [ ] Criar gestão de clientes
- [ ] Desenvolver controle financeiro
- [ ] Integração com n8n
- [ ] Webhooks para sincronização
- [ ] Relatórios avançados
