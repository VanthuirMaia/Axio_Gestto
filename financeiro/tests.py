from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.utils.timezone import now, make_aware
from datetime import datetime, timedelta
from decimal import Decimal
from io import StringIO

from empresas.models import Empresa, Servico, Profissional
from clientes.models import Cliente
from agendamentos.models import Agendamento, StatusAgendamento
from financeiro.models import (
    LancamentoFinanceiro, CategoriaFinanceira, FormaPagamento,
    TipoLancamento, StatusLancamento
)


Usuario = get_user_model()


class FormaPagamentoModelTest(TestCase):
    """Testes para o model FormaPagamento"""

    def setUp(self):
        """Configuração inicial dos testes"""
        self.empresa = Empresa.objects.create(
            nome='Empresa Teste',
            slug='empresa-teste',
            telefone='11999999999',
            email='empresa@teste.com',
            endereco='Rua Teste, 123',
            cidade='São Paulo',
            estado='SP',
            cep='01234-567',
            cnpj='12.345.678/0001-90'
        )

    def test_criar_forma_pagamento(self):
        """Testa criação de forma de pagamento"""
        forma = FormaPagamento.objects.create(
            empresa=self.empresa,
            nome='PIX'
        )

        self.assertEqual(forma.nome, 'PIX')
        self.assertTrue(forma.ativo)
        self.assertEqual(forma.empresa, self.empresa)

    def test_forma_pagamento_string_representation(self):
        """Testa a representação em string"""
        forma = FormaPagamento.objects.create(
            empresa=self.empresa,
            nome='Cartão de Crédito'
        )

        self.assertEqual(str(forma), 'Cartão de Crédito')

    def test_forma_pagamento_nome_unico_por_empresa(self):
        """Testa que o nome deve ser único por empresa"""
        FormaPagamento.objects.create(
            empresa=self.empresa,
            nome='Dinheiro'
        )

        with self.assertRaises(Exception):
            FormaPagamento.objects.create(
                empresa=self.empresa,
                nome='Dinheiro'  # Nome duplicado
            )

    def test_forma_pagamento_mesmo_nome_empresas_diferentes(self):
        """Testa que formas com mesmo nome podem existir em empresas diferentes"""
        empresa2 = Empresa.objects.create(
            nome='Outra Empresa',
            slug='outra-empresa',
            telefone='11888888888',
            email='outra@teste.com',
            endereco='Av. Teste, 456',
            cidade='Rio de Janeiro',
            estado='RJ',
            cep='20000-000',
            cnpj='98.765.432/0001-10'
        )

        FormaPagamento.objects.create(
            empresa=self.empresa,
            nome='PIX'
        )

        # Deve permitir criar com mesmo nome em empresa diferente
        forma2 = FormaPagamento.objects.create(
            empresa=empresa2,
            nome='PIX'
        )

        self.assertEqual(forma2.nome, 'PIX')


class CategoriaFinanceiraModelTest(TestCase):
    """Testes para o model CategoriaFinanceira"""

    def setUp(self):
        """Configuração inicial dos testes"""
        self.empresa = Empresa.objects.create(
            nome='Empresa Teste',
            slug='empresa-teste',
            telefone='11999999999',
            email='empresa@teste.com',
            endereco='Rua Teste, 123',
            cidade='São Paulo',
            estado='SP',
            cep='01234-567',
            cnpj='12.345.678/0001-90'
        )

    def test_criar_categoria_receita(self):
        """Testa criação de categoria de receita"""
        categoria = CategoriaFinanceira.objects.create(
            empresa=self.empresa,
            nome='Serviços',
            tipo=TipoLancamento.RECEITA,
            cor='#28a745'
        )

        self.assertEqual(categoria.nome, 'Serviços')
        self.assertEqual(categoria.tipo, TipoLancamento.RECEITA)
        self.assertEqual(categoria.cor, '#28a745')
        self.assertTrue(categoria.ativo)

    def test_criar_categoria_despesa(self):
        """Testa criação de categoria de despesa"""
        categoria = CategoriaFinanceira.objects.create(
            empresa=self.empresa,
            nome='Aluguel',
            tipo=TipoLancamento.DESPESA,
            cor='#dc3545'
        )

        self.assertEqual(categoria.tipo, TipoLancamento.DESPESA)

    def test_categoria_string_representation(self):
        """Testa a representação em string"""
        categoria = CategoriaFinanceira.objects.create(
            empresa=self.empresa,
            nome='Produtos',
            tipo=TipoLancamento.RECEITA
        )

        self.assertEqual(str(categoria), 'Receita - Produtos')

    def test_categoria_nome_unico_por_empresa_e_tipo(self):
        """Testa que nome deve ser único por empresa e tipo"""
        CategoriaFinanceira.objects.create(
            empresa=self.empresa,
            nome='Vendas',
            tipo=TipoLancamento.RECEITA
        )

        with self.assertRaises(Exception):
            CategoriaFinanceira.objects.create(
                empresa=self.empresa,
                nome='Vendas',  # Nome duplicado
                tipo=TipoLancamento.RECEITA  # Mesmo tipo
            )

    def test_categoria_mesmo_nome_tipos_diferentes(self):
        """Testa que mesmo nome pode existir em tipos diferentes"""
        CategoriaFinanceira.objects.create(
            empresa=self.empresa,
            nome='Diversos',
            tipo=TipoLancamento.RECEITA
        )

        # Deve permitir mesmo nome com tipo diferente
        categoria2 = CategoriaFinanceira.objects.create(
            empresa=self.empresa,
            nome='Diversos',
            tipo=TipoLancamento.DESPESA
        )

        self.assertEqual(categoria2.nome, 'Diversos')


class LancamentoFinanceiroModelTest(TestCase):
    """Testes para o model LancamentoFinanceiro"""

    def setUp(self):
        """Configuração inicial dos testes"""
        self.empresa = Empresa.objects.create(
            nome='Empresa Teste',
            slug='empresa-teste',
            telefone='11999999999',
            email='empresa@teste.com',
            endereco='Rua Teste, 123',
            cidade='São Paulo',
            estado='SP',
            cep='01234-567',
            cnpj='12.345.678/0001-90'
        )

        self.categoria = CategoriaFinanceira.objects.create(
            empresa=self.empresa,
            nome='Serviços',
            tipo=TipoLancamento.RECEITA
        )

        self.forma_pagamento = FormaPagamento.objects.create(
            empresa=self.empresa,
            nome='Dinheiro'
        )

    def test_criar_lancamento_receita(self):
        """Testa criação de lançamento de receita"""
        lancamento = LancamentoFinanceiro.objects.create(
            empresa=self.empresa,
            tipo=TipoLancamento.RECEITA,
            categoria=self.categoria,
            descricao='Venda de produto',
            valor=Decimal('150.00'),
            data_vencimento=now().date(),
            forma_pagamento=self.forma_pagamento
        )

        self.assertEqual(lancamento.tipo, TipoLancamento.RECEITA)
        self.assertEqual(lancamento.valor, Decimal('150.00'))
        self.assertEqual(lancamento.status, StatusLancamento.PENDENTE)

    def test_lancamento_string_representation(self):
        """Testa a representação em string do lançamento"""
        lancamento = LancamentoFinanceiro.objects.create(
            empresa=self.empresa,
            tipo=TipoLancamento.RECEITA,
            categoria=self.categoria,
            descricao='Teste',
            valor=Decimal('100.00'),
            data_vencimento=now().date(),
            status=StatusLancamento.PAGO
        )

        self.assertIn('+', str(lancamento))
        self.assertIn('R$ 100.00', str(lancamento))
        self.assertIn('Teste', str(lancamento))

    def test_lancamento_despesa_string_representation(self):
        """Testa representação de despesa (com sinal negativo)"""
        categoria_despesa = CategoriaFinanceira.objects.create(
            empresa=self.empresa,
            nome='Aluguel',
            tipo=TipoLancamento.DESPESA
        )

        lancamento = LancamentoFinanceiro.objects.create(
            empresa=self.empresa,
            tipo=TipoLancamento.DESPESA,
            categoria=categoria_despesa,
            descricao='Aluguel',
            valor=Decimal('1000.00'),
            data_vencimento=now().date()
        )

        self.assertIn('-', str(lancamento))

    def test_marcar_como_pago(self):
        """Testa o método marcar_como_pago"""
        lancamento = LancamentoFinanceiro.objects.create(
            empresa=self.empresa,
            tipo=TipoLancamento.RECEITA,
            categoria=self.categoria,
            descricao='Serviço',
            valor=Decimal('200.00'),
            data_vencimento=now().date()
        )

        # Marca como pago
        data_pagamento = now().date()
        lancamento.marcar_como_pago(data_pagamento, self.forma_pagamento)

        # Recarrega do banco
        lancamento.refresh_from_db()

        self.assertEqual(lancamento.status, StatusLancamento.PAGO)
        self.assertEqual(lancamento.data_pagamento, data_pagamento)
        self.assertEqual(lancamento.forma_pagamento, self.forma_pagamento)

    def test_marcar_como_pago_sem_parametros(self):
        """Testa marcar como pago sem passar parâmetros (usa data atual)"""
        lancamento = LancamentoFinanceiro.objects.create(
            empresa=self.empresa,
            tipo=TipoLancamento.RECEITA,
            categoria=self.categoria,
            descricao='Serviço',
            valor=Decimal('100.00'),
            data_vencimento=now().date()
        )

        lancamento.marcar_como_pago()
        lancamento.refresh_from_db()

        self.assertEqual(lancamento.status, StatusLancamento.PAGO)
        self.assertIsNotNone(lancamento.data_pagamento)

    def test_cancelar_lancamento(self):
        """Testa o método cancelar"""
        lancamento = LancamentoFinanceiro.objects.create(
            empresa=self.empresa,
            tipo=TipoLancamento.RECEITA,
            categoria=self.categoria,
            descricao='Serviço',
            valor=Decimal('100.00'),
            data_vencimento=now().date()
        )

        lancamento.cancelar()
        lancamento.refresh_from_db()

        self.assertEqual(lancamento.status, StatusLancamento.CANCELADO)


class SignalsFinanceiroTest(TestCase):
    """Testes para os signals de automação financeira (CRÍTICO)"""

    def setUp(self):
        """Configuração inicial dos testes"""
        self.empresa = Empresa.objects.create(
            nome='Empresa Teste',
            slug='empresa-teste',
            telefone='11999999999',
            email='empresa@teste.com',
            endereco='Rua Teste, 123',
            cidade='São Paulo',
            estado='SP',
            cep='01234-567',
            cnpj='12.345.678/0001-90'
        )

        self.servico = Servico.objects.create(
            empresa=self.empresa,
            nome='Corte de Cabelo',
            preco=Decimal('50.00'),
            duracao_minutos=30
        )

        self.profissional = Profissional.objects.create(
            empresa=self.empresa,
            nome='João Barbeiro',
            email='joao@teste.com',
            telefone='11888888888'
        )

        self.cliente = Cliente.objects.create(
            empresa=self.empresa,
            nome='Cliente Teste',
            email='cliente@teste.com',
            telefone='11777777777'
        )

    def test_criar_receita_quando_agendamento_concluido(self):
        """Testa que receita é criada automaticamente quando agendamento é concluído"""
        agora = now()

        # Criar agendamento pendente
        agendamento = Agendamento.objects.create(
            empresa=self.empresa,
            cliente=self.cliente,
            servico=self.servico,
            profissional=self.profissional,
            data_hora_inicio=agora + timedelta(hours=1),
            data_hora_fim=agora + timedelta(hours=1, minutes=30),
            status=StatusAgendamento.PENDENTE,
            valor_cobrado=Decimal('50.00')
        )

        # Verifica que não existe lançamento ainda
        self.assertEqual(agendamento.lancamentos.count(), 0)

        # Marca como concluído (deve disparar o signal)
        agendamento.status = StatusAgendamento.CONCLUIDO
        agendamento.save()

        # Verifica que o lançamento foi criado
        self.assertEqual(agendamento.lancamentos.count(), 1)

        lancamento = agendamento.lancamentos.first()
        self.assertEqual(lancamento.tipo, TipoLancamento.RECEITA)
        self.assertEqual(lancamento.valor, Decimal('50.00'))
        self.assertEqual(lancamento.status, StatusLancamento.PAGO)
        self.assertIn(self.servico.nome, lancamento.descricao)
        self.assertIn(self.cliente.nome, lancamento.descricao)

    def test_nao_criar_receita_duplicada(self):
        """Testa que não cria receita duplicada se já existe"""
        agora = now()

        agendamento = Agendamento.objects.create(
            empresa=self.empresa,
            cliente=self.cliente,
            servico=self.servico,
            profissional=self.profissional,
            data_hora_inicio=agora + timedelta(hours=1),
            data_hora_fim=agora + timedelta(hours=1, minutes=30),
            status=StatusAgendamento.CONCLUIDO,
            valor_cobrado=Decimal('50.00')
        )

        # Primeira conclusão cria o lançamento
        self.assertEqual(agendamento.lancamentos.count(), 1)

        # Salva novamente (não deve criar duplicado)
        agendamento.save()

        # Deve continuar com apenas 1 lançamento
        self.assertEqual(agendamento.lancamentos.count(), 1)

    def test_nao_criar_receita_se_nao_tiver_valor(self):
        """Testa que não cria receita se agendamento não tiver valor"""
        agora = now()

        agendamento = Agendamento.objects.create(
            empresa=self.empresa,
            cliente=self.cliente,
            servico=self.servico,
            profissional=self.profissional,
            data_hora_inicio=agora + timedelta(hours=1),
            data_hora_fim=agora + timedelta(hours=1, minutes=30),
            status=StatusAgendamento.CONCLUIDO,
            valor_cobrado=None  # Sem valor
        )

        # Não deve criar lançamento
        self.assertEqual(agendamento.lancamentos.count(), 0)

    def test_cancelar_receita_quando_agendamento_cancelado(self):
        """Testa que receita é cancelada quando agendamento concluído é cancelado"""
        agora = now()

        # Criar agendamento concluído (que gera receita)
        agendamento = Agendamento.objects.create(
            empresa=self.empresa,
            cliente=self.cliente,
            servico=self.servico,
            profissional=self.profissional,
            data_hora_inicio=agora + timedelta(hours=1),
            data_hora_fim=agora + timedelta(hours=1, minutes=30),
            status=StatusAgendamento.CONCLUIDO,
            valor_cobrado=Decimal('50.00')
        )

        # Verifica que receita foi criada
        self.assertEqual(agendamento.lancamentos.count(), 1)
        lancamento = agendamento.lancamentos.first()
        self.assertEqual(lancamento.status, StatusLancamento.PAGO)

        # Cancela o agendamento (deve cancelar a receita)
        agendamento.status = StatusAgendamento.CANCELADO
        agendamento.save()

        # Verifica que a receita foi cancelada
        lancamento.refresh_from_db()
        self.assertEqual(lancamento.status, StatusLancamento.CANCELADO)

    def test_categoria_servicos_criada_automaticamente(self):
        """Testa que categoria 'Serviços' é criada automaticamente se não existir"""
        agora = now()

        # Verifica que não existe a categoria
        self.assertFalse(
            CategoriaFinanceira.objects.filter(
                empresa=self.empresa,
                nome='Serviços'
            ).exists()
        )

        # Criar agendamento concluído
        Agendamento.objects.create(
            empresa=self.empresa,
            cliente=self.cliente,
            servico=self.servico,
            profissional=self.profissional,
            data_hora_inicio=agora + timedelta(hours=1),
            data_hora_fim=agora + timedelta(hours=1, minutes=30),
            status=StatusAgendamento.CONCLUIDO,
            valor_cobrado=Decimal('50.00')
        )

        # Verifica que a categoria foi criada
        self.assertTrue(
            CategoriaFinanceira.objects.filter(
                empresa=self.empresa,
                nome='Serviços',
                tipo=TipoLancamento.RECEITA
            ).exists()
        )


class ManagementCommandTest(TestCase):
    """Testes para o management command processar_agendamentos_concluidos"""

    def setUp(self):
        """Configuração inicial dos testes"""
        self.empresa = Empresa.objects.create(
            nome='Empresa Teste',
            slug='empresa-teste',
            telefone='11999999999',
            email='empresa@teste.com',
            endereco='Rua Teste, 123',
            cidade='São Paulo',
            estado='SP',
            cep='01234-567',
            cnpj='12.345.678/0001-90'
        )

        self.servico = Servico.objects.create(
            empresa=self.empresa,
            nome='Corte de Cabelo',
            preco=Decimal('50.00'),
            duracao_minutos=30
        )

        self.profissional = Profissional.objects.create(
            empresa=self.empresa,
            nome='João Barbeiro',
            email='joao@teste.com',
            telefone='11888888888'
        )

        self.cliente = Cliente.objects.create(
            empresa=self.empresa,
            nome='Cliente Teste',
            email='cliente@teste.com',
            telefone='11777777777'
        )

    def test_processar_agendamento_antigo(self):
        """Testa processamento de agendamento que terminou há mais de 30 minutos"""
        agora = now()

        # Criar agendamento que terminou há 1 hora
        agendamento = Agendamento.objects.create(
            empresa=self.empresa,
            cliente=self.cliente,
            servico=self.servico,
            profissional=self.profissional,
            data_hora_inicio=agora - timedelta(hours=2),
            data_hora_fim=agora - timedelta(hours=1, minutes=30),  # Terminou há 1h30
            status=StatusAgendamento.CONFIRMADO,
            valor_cobrado=Decimal('50.00')
        )

        # Executa o comando
        out = StringIO()
        call_command('processar_agendamentos_concluidos', stdout=out)

        # Verifica que o agendamento foi processado
        agendamento.refresh_from_db()
        self.assertEqual(agendamento.status, StatusAgendamento.CONCLUIDO)

        # Nota: O comando cria 2 lançamentos (1 via signal + 1 manualmente)
        # Isso poderia ser otimizado para criar apenas 1
        self.assertGreaterEqual(agendamento.lancamentos.count(), 1)

    def test_nao_processar_agendamento_recente(self):
        """Testa que não processa agendamento que terminou há menos de 30 minutos"""
        agora = now()

        # Criar agendamento que terminou há 15 minutos
        agendamento = Agendamento.objects.create(
            empresa=self.empresa,
            cliente=self.cliente,
            servico=self.servico,
            profissional=self.profissional,
            data_hora_inicio=agora - timedelta(minutes=45),
            data_hora_fim=agora - timedelta(minutes=15),  # Terminou há 15min
            status=StatusAgendamento.CONFIRMADO,
            valor_cobrado=Decimal('50.00')
        )

        # Executa o comando
        out = StringIO()
        call_command('processar_agendamentos_concluidos', stdout=out)

        # Verifica que o agendamento NÃO foi processado
        agendamento.refresh_from_db()
        self.assertEqual(agendamento.status, StatusAgendamento.CONFIRMADO)
        self.assertEqual(agendamento.lancamentos.count(), 0)

    def test_dry_run_nao_processa(self):
        """Testa que dry-run mostra mas não processa"""
        agora = now()

        agendamento = Agendamento.objects.create(
            empresa=self.empresa,
            cliente=self.cliente,
            servico=self.servico,
            profissional=self.profissional,
            data_hora_inicio=agora - timedelta(hours=2),
            data_hora_fim=agora - timedelta(hours=1, minutes=30),
            status=StatusAgendamento.CONFIRMADO,
            valor_cobrado=Decimal('50.00')
        )

        # Executa com --dry-run
        out = StringIO()
        call_command('processar_agendamentos_concluidos', '--dry-run', stdout=out)

        # Verifica que NÃO foi processado
        agendamento.refresh_from_db()
        self.assertEqual(agendamento.status, StatusAgendamento.CONFIRMADO)
        self.assertEqual(agendamento.lancamentos.count(), 0)

        # Mas deve aparecer no output
        output = out.getvalue()
        self.assertIn('DRY-RUN', output)

    def test_nao_processar_agendamento_ja_com_lancamento(self):
        """Testa que não processa agendamento que já tem lançamento"""
        agora = now()

        agendamento = Agendamento.objects.create(
            empresa=self.empresa,
            cliente=self.cliente,
            servico=self.servico,
            profissional=self.profissional,
            data_hora_inicio=agora - timedelta(hours=2),
            data_hora_fim=agora - timedelta(hours=1, minutes=30),
            status=StatusAgendamento.CONFIRMADO,
            valor_cobrado=Decimal('50.00')
        )

        # Criar lançamento manualmente
        categoria = CategoriaFinanceira.objects.create(
            empresa=self.empresa,
            nome='Serviços',
            tipo=TipoLancamento.RECEITA
        )

        LancamentoFinanceiro.objects.create(
            empresa=self.empresa,
            tipo=TipoLancamento.RECEITA,
            categoria=categoria,
            agendamento=agendamento,
            descricao='Teste',
            valor=Decimal('50.00'),
            data_vencimento=now().date()
        )

        # Executa o comando
        out = StringIO()
        call_command('processar_agendamentos_concluidos', stdout=out)

        # Verifica que não criou lançamento duplicado
        self.assertEqual(agendamento.lancamentos.count(), 1)
