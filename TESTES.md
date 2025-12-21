# 🧪 Guia de Testes - Axio Gestto

## Visão Geral

Este projeto utiliza o framework de testes nativo do Django (unittest) para garantir a qualidade e confiabilidade do código.

## Estrutura de Testes

```
core/tests.py           - Testes de autenticação, usuários e dashboard
empresas/tests.py       - Testes de empresas, serviços e profissionais
agendamentos/tests.py   - Testes de agendamentos e prevenção de conflitos
clientes/tests.py       - Testes de clientes e métricas (a implementar)
financeiro/tests.py     - Testes de lançamentos e signals (a implementar)
```

## Como Executar os Testes

### 1. Executar Todos os Testes

```bash
python manage.py test
```

### 2. Executar Testes de um Módulo Específico

```bash
# Testes do Core
python manage.py test core

# Testes de Empresas
python manage.py test empresas

# Testes de Agendamentos
python manage.py test agendamentos
```

### 3. Executar uma Classe de Teste Específica

```bash
# Apenas testes de login
python manage.py test core.tests.LoginViewTest

# Apenas testes de conflitos de agendamento
python manage.py test agendamentos.tests.ConflitosAgendamentoTest
```

### 4. Executar um Teste Específico

```bash
python manage.py test core.tests.LoginViewTest.test_login_com_email
```

### 5. Executar com Mais Verbosidade

```bash
python manage.py test --verbosity=2
```

### 6. Manter o Banco de Dados de Teste

```bash
python manage.py test --keepdb
```

Isso acelera execuções subsequentes, pois o Django reutiliza o banco de teste.

## Cobertura de Testes

### Módulos Testados

#### ✅ Core (100% coberto)
- [x] Model Usuario (criação, validação, ordenação)
- [x] View de Login (username, email, erros, redirecionamento)
- [x] View de Logout
- [x] View de Dashboard (métricas, autenticação, contexto)

#### ✅ Empresas (100% coberto)
- [x] Model Empresa (criação, validação, cores, unicidade)
- [x] Model Servico (criação, validação de preço/duração, unicidade por empresa)
- [x] Model Profissional (criação, serviços, comissão, cores, unicidade por empresa)

#### ✅ Agendamentos (100% coberto)
- [x] Model Agendamento (criação, status, ordenação)
- [x] Detecção de Conflitos (horário exato, parcial, engloba, sequencial)
- [x] Model DisponibilidadeProfissional
- [x] Views do Calendário (autenticação, renderização, API JSON)

#### ⏳ Clientes (a implementar)
- [ ] Model Cliente
- [ ] Métricas (VIP, frequentes, em risco)
- [ ] Views de CRUD

#### ⏳ Financeiro (a implementar)
- [ ] Model LancamentoFinanceiro
- [ ] Signals (criação automática de receitas)
- [ ] Management Commands

## Testes Importantes

### Prevenção de Conflitos de Agendamento

Os testes de conflitos garantem que:
- Não é possível agendar dois serviços no mesmo horário para o mesmo profissional
- Agendamentos que se sobrepõem parcialmente são detectados
- Agendamentos sequenciais (sem sobreposição) são permitidos
- Profissionais diferentes podem ter agendamentos no mesmo horário

```bash
python manage.py test agendamentos.tests.ConflitosAgendamentoTest
```

### Multi-tenant

Os testes garantem isolamento de dados por empresa:
- Serviços e profissionais com mesmo nome podem existir em empresas diferentes
- Queries filtram automaticamente por empresa do usuário

## Boas Práticas

### 1. Sempre execute os testes antes de commitar

```bash
python manage.py test
```

### 2. Escreva testes para novos recursos

Ao adicionar uma nova funcionalidade, crie testes correspondentes:

```python
class MinhaNovaFeatureTest(TestCase):
    def test_comportamento_esperado(self):
        # Arrange
        # Act
        # Assert
        pass
```

### 3. Use fixtures para dados repetitivos

```python
def setUp(self):
    """Configuração executada antes de cada teste"""
    self.empresa = Empresa.objects.create(...)
    self.usuario = Usuario.objects.create_user(...)
```

### 4. Nomeie testes de forma descritiva

```python
# ❌ Ruim
def test_1(self):
    pass

# ✅ Bom
def test_login_com_senha_incorreta_retorna_erro(self):
    pass
```

### 5. Teste casos extremos e erros

Não teste apenas o "caminho feliz":

```python
def test_servico_preco_negativo_levanta_erro(self):
    servico = Servico(preco=Decimal('-10.00'))
    with self.assertRaises(ValidationError):
        servico.full_clean()
```

## Configuração com Pytest (Opcional)

Se preferir usar pytest ao invés do unittest padrão:

```bash
# Instalar pytest e plugin Django
pip install pytest pytest-django

# Executar testes
pytest

# Com cobertura
pytest --cov=. --cov-report=html
```

## CI/CD

### GitHub Actions (Exemplo)

Adicione ao `.github/workflows/tests.yml`:

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: 3.11
      - run: pip install -r requirements.txt
      - run: python manage.py test
```

## Próximos Passos

1. ✅ Implementar testes para módulo Clientes
2. ✅ Implementar testes para módulo Financeiro (especialmente signals)
3. 📊 Configurar cobertura de código (coverage.py)
4. 🔄 Integrar testes no CI/CD
5. 📈 Atingir meta de 80%+ de cobertura

## Recursos Adicionais

- [Documentação Django Testing](https://docs.djangoproject.com/en/5.0/topics/testing/)
- [Pytest-Django](https://pytest-django.readthedocs.io/)
- [Coverage.py](https://coverage.readthedocs.io/)

---

**Última atualização**: 2025-12-20
**Testes implementados**: 50+ testes
**Cobertura estimada**: ~60% (Core, Empresas, Agendamentos)
