from django.test import TestCase, Client as TestClient
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils.timezone import now, make_aware
from datetime import datetime, timedelta
from decimal import Decimal

from empresas.models import Empresa, Servico, Profissional
from clientes.models import Cliente
from agendamentos.models import Agendamento, StatusAgendamento
from clientes.services.metricas_clientes import listar_clientes_com_metricas


Usuario = get_user_model()


class ClienteModelTest(TestCase):
    """Testes para o model Cliente"""

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

    def test_criar_cliente(self):
        """Testa criação de cliente com campos obrigatórios"""
        cliente = Cliente.objects.create(
            empresa=self.empresa,
            nome='João Silva',
            telefone='11888888888'
        )

        self.assertEqual(cliente.nome, 'João Silva')
        self.assertEqual(cliente.telefone, '11888888888')
        self.assertEqual(cliente.empresa, self.empresa)
        self.assertTrue(cliente.ativo)

    def test_criar_cliente_completo(self):
        """Testa criação de cliente com todos os campos"""
        data_nascimento = datetime(1990, 5, 15).date()

        cliente = Cliente.objects.create(
            empresa=self.empresa,
            nome='Maria Santos',
            email='maria@teste.com',
            telefone='11777777777',
            cpf='123.456.789-00',
            data_nascimento=data_nascimento,
            endereco='Rua Teste, 456',
            cidade='São Paulo',
            estado='SP',
            cep='01234-567',
            notas='Cliente VIP'
        )

        self.assertEqual(cliente.email, 'maria@teste.com')
        self.assertEqual(cliente.cpf, '123.456.789-00')
        self.assertEqual(cliente.data_nascimento, data_nascimento)
        self.assertEqual(cliente.endereco, 'Rua Teste, 456')
        self.assertEqual(cliente.notas, 'Cliente VIP')

    def test_cliente_string_representation(self):
        """Testa a representação em string do cliente"""
        cliente = Cliente.objects.create(
            empresa=self.empresa,
            nome='Pedro Costa',
            telefone='11666666666'
        )

        self.assertEqual(str(cliente), 'Pedro Costa (11666666666)')

    def test_cliente_ordering(self):
        """Testa ordenação de clientes (por nome)"""
        Cliente.objects.create(
            empresa=self.empresa,
            nome='Zé Silva',
            telefone='11111111111'
        )

        Cliente.objects.create(
            empresa=self.empresa,
            nome='Ana Costa',
            telefone='11222222222'
        )

        clientes = Cliente.objects.all()
        self.assertEqual(clientes[0].nome, 'Ana Costa')  # Ordem alfabética
        self.assertEqual(clientes[1].nome, 'Zé Silva')

    def test_telefone_unico_por_empresa(self):
        """Testa que telefone deve ser único por empresa"""
        Cliente.objects.create(
            empresa=self.empresa,
            nome='Cliente 1',
            telefone='11999999999'
        )

        with self.assertRaises(Exception):
            Cliente.objects.create(
                empresa=self.empresa,
                nome='Cliente 2',
                telefone='11999999999'  # Telefone duplicado
            )

    def test_mesmo_telefone_empresas_diferentes(self):
        """Testa que mesmo telefone pode existir em empresas diferentes"""
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

        Cliente.objects.create(
            empresa=self.empresa,
            nome='Cliente 1',
            telefone='11999999999'
        )

        # Deve permitir mesmo telefone em empresa diferente
        cliente2 = Cliente.objects.create(
            empresa=empresa2,
            nome='Cliente 2',
            telefone='11999999999'
        )

        self.assertEqual(cliente2.telefone, '11999999999')

    def test_cliente_inativo(self):
        """Testa marcação de cliente como inativo"""
        cliente = Cliente.objects.create(
            empresa=self.empresa,
            nome='Cliente Inativo',
            telefone='11555555555',
            ativo=False
        )

        self.assertFalse(cliente.ativo)


class MetricasClientesTest(TestCase):
    """Testes para métricas de clientes"""

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
            telefone='11777777777'
        )

    def test_metricas_cliente_sem_agendamentos(self):
        """Testa métricas de cliente sem agendamentos"""
        clientes = listar_clientes_com_metricas()
        cliente = clientes.filter(id=self.cliente.id).first()

        self.assertEqual(cliente.total_visitas, 0)
        self.assertIsNone(cliente.total_gasto)
        self.assertIsNone(cliente.ticket_medio)
        self.assertIsNone(cliente.ultima_visita)

    def test_metricas_cliente_com_agendamentos_concluidos(self):
        """Testa métricas de cliente com agendamentos concluídos"""
        agora = now()

        # Criar 3 agendamentos concluídos
        for i in range(3):
            Agendamento.objects.create(
                empresa=self.empresa,
                cliente=self.cliente,
                servico=self.servico,
                profissional=self.profissional,
                data_hora_inicio=agora - timedelta(days=i*7),
                data_hora_fim=agora - timedelta(days=i*7, minutes=-30),
                status=StatusAgendamento.CONCLUIDO,
                valor_cobrado=Decimal('50.00')
            )

        clientes = listar_clientes_com_metricas()
        cliente = clientes.filter(id=self.cliente.id).first()

        self.assertEqual(cliente.total_visitas, 3)
        self.assertEqual(cliente.total_gasto, Decimal('150.00'))
        self.assertEqual(cliente.ticket_medio, Decimal('50.00'))
        self.assertIsNotNone(cliente.ultima_visita)

    def test_metricas_ignora_agendamentos_nao_concluidos(self):
        """Testa que métricas ignoram agendamentos não concluídos"""
        agora = now()

        # Agendamento concluído
        Agendamento.objects.create(
            empresa=self.empresa,
            cliente=self.cliente,
            servico=self.servico,
            profissional=self.profissional,
            data_hora_inicio=agora - timedelta(days=7),
            data_hora_fim=agora - timedelta(days=7, minutes=-30),
            status=StatusAgendamento.CONCLUIDO,
            valor_cobrado=Decimal('50.00')
        )

        # Agendamentos que não devem contar
        Agendamento.objects.create(
            empresa=self.empresa,
            cliente=self.cliente,
            servico=self.servico,
            profissional=self.profissional,
            data_hora_inicio=agora + timedelta(days=1),
            data_hora_fim=agora + timedelta(days=1, minutes=30),
            status=StatusAgendamento.PENDENTE,
            valor_cobrado=Decimal('50.00')
        )

        Agendamento.objects.create(
            empresa=self.empresa,
            cliente=self.cliente,
            servico=self.servico,
            profissional=self.profissional,
            data_hora_inicio=agora - timedelta(days=14),
            data_hora_fim=agora - timedelta(days=14, minutes=-30),
            status=StatusAgendamento.CANCELADO,
            valor_cobrado=Decimal('50.00')
        )

        clientes = listar_clientes_com_metricas()
        cliente = clientes.filter(id=self.cliente.id).first()

        # Deve contar apenas o agendamento concluído
        self.assertEqual(cliente.total_visitas, 1)
        self.assertEqual(cliente.total_gasto, Decimal('50.00'))


class DashboardClientesViewTest(TestCase):
    """Testes para a view do dashboard de clientes"""

    def setUp(self):
        """Configuração inicial dos testes"""
        self.client_test = TestClient()

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

        self.usuario = Usuario.objects.create_user(
            username='teste',
            email='teste@teste.com',
            password='senha123',
            empresa=self.empresa
        )

        self.servico = Servico.objects.create(
            empresa=self.empresa,
            nome='Corte',
            preco=Decimal('50.00'),
            duracao_minutos=30
        )

        self.profissional = Profissional.objects.create(
            empresa=self.empresa,
            nome='João',
            email='joao@teste.com',
            telefone='11888888888'
        )

    def test_dashboard_requer_autenticacao(self):
        """Testa que dashboard requer autenticação"""
        response = self.client_test.get(reverse('dashboard_clientes'))
        self.assertRedirects(
            response,
            f"{reverse('login')}?next={reverse('dashboard_clientes')}"
        )

    def test_dashboard_renderiza_corretamente(self):
        """Testa que dashboard renderiza com dados corretos"""
        self.client_test.login(username='teste', password='senha123')
        response = self.client_test.get(reverse('dashboard_clientes'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'clientes/dashboard.html')
        self.assertIn('empresa', response.context)
        self.assertIn('total_clientes', response.context)

    def test_dashboard_metricas_gerais(self):
        """Testa métricas gerais do dashboard"""
        # Criar 3 clientes ativos
        for i in range(3):
            Cliente.objects.create(
                empresa=self.empresa,
                nome=f'Cliente {i}',
                telefone=f'1100000000{i}'
            )

        # Criar 1 cliente inativo
        Cliente.objects.create(
            empresa=self.empresa,
            nome='Cliente Inativo',
            telefone='11999999999',
            ativo=False
        )

        self.client_test.login(username='teste', password='senha123')
        response = self.client_test.get(reverse('dashboard_clientes'))

        self.assertEqual(response.context['total_clientes'], 3)
        self.assertEqual(response.context['total_inativos'], 1)

    def test_dashboard_top_clientes_vip(self):
        """Testa ranking de clientes VIP (maior gasto)"""
        agora = now()

        # Cliente VIP (gasta R$ 200)
        cliente_vip = Cliente.objects.create(
            empresa=self.empresa,
            nome='Cliente VIP',
            telefone='11111111111'
        )

        for i in range(4):
            Agendamento.objects.create(
                empresa=self.empresa,
                cliente=cliente_vip,
                servico=self.servico,
                profissional=self.profissional,
                data_hora_inicio=agora - timedelta(days=i*7),
                data_hora_fim=agora - timedelta(days=i*7, minutes=-30),
                status=StatusAgendamento.CONCLUIDO,
                valor_cobrado=Decimal('50.00')
            )

        # Cliente normal (gasta R$ 50)
        cliente_normal = Cliente.objects.create(
            empresa=self.empresa,
            nome='Cliente Normal',
            telefone='11222222222'
        )

        Agendamento.objects.create(
            empresa=self.empresa,
            cliente=cliente_normal,
            servico=self.servico,
            profissional=self.profissional,
            data_hora_inicio=agora - timedelta(days=7),
            data_hora_fim=agora - timedelta(days=7, minutes=-30),
            status=StatusAgendamento.CONCLUIDO,
            valor_cobrado=Decimal('50.00')
        )

        self.client_test.login(username='teste', password='senha123')
        response = self.client_test.get(reverse('dashboard_clientes'))

        top_vip = response.context['top_clientes_vip']

        # Cliente VIP deve estar primeiro
        self.assertEqual(top_vip[0].id, cliente_vip.id)
        self.assertEqual(top_vip[0].total_gasto, Decimal('200.00'))

    def test_dashboard_clientes_em_risco(self):
        """Testa identificação de clientes em risco (sem agendar há +30 dias)"""
        agora = now()

        # Cliente em risco (último agendamento há 40 dias)
        cliente_risco = Cliente.objects.create(
            empresa=self.empresa,
            nome='Cliente em Risco',
            telefone='11333333333'
        )

        Agendamento.objects.create(
            empresa=self.empresa,
            cliente=cliente_risco,
            servico=self.servico,
            profissional=self.profissional,
            data_hora_inicio=agora - timedelta(days=40),
            data_hora_fim=agora - timedelta(days=40, minutes=-30),
            status=StatusAgendamento.CONCLUIDO,
            valor_cobrado=Decimal('50.00')
        )

        # Cliente ativo (agendou há 10 dias)
        cliente_ativo = Cliente.objects.create(
            empresa=self.empresa,
            nome='Cliente Ativo',
            telefone='11444444444'
        )

        Agendamento.objects.create(
            empresa=self.empresa,
            cliente=cliente_ativo,
            servico=self.servico,
            profissional=self.profissional,
            data_hora_inicio=agora - timedelta(days=10),
            data_hora_fim=agora - timedelta(days=10, minutes=-30),
            status=StatusAgendamento.CONCLUIDO,
            valor_cobrado=Decimal('50.00')
        )

        self.client_test.login(username='teste', password='senha123')
        response = self.client_test.get(reverse('dashboard_clientes'))

        clientes_risco = response.context['clientes_risco']

        # Apenas cliente em risco deve aparecer
        self.assertGreaterEqual(len(clientes_risco), 1)
        self.assertEqual(clientes_risco[0].id, cliente_risco.id)

    def test_dashboard_aniversariantes_mes(self):
        """Testa listagem de aniversariantes do mês"""
        hoje = now().date()

        # Cliente aniversariante este mês
        Cliente.objects.create(
            empresa=self.empresa,
            nome='Aniversariante',
            telefone='11555555555',
            data_nascimento=datetime(1990, hoje.month, 15).date()
        )

        # Cliente com aniversário em outro mês
        Cliente.objects.create(
            empresa=self.empresa,
            nome='Não Aniversariante',
            telefone='11666666666',
            data_nascimento=datetime(1990, (hoje.month % 12) + 1, 15).date()
        )

        self.client_test.login(username='teste', password='senha123')
        response = self.client_test.get(reverse('dashboard_clientes'))

        aniversariantes = response.context['aniversariantes']

        self.assertEqual(len(aniversariantes), 1)
        self.assertEqual(aniversariantes[0].nome, 'Aniversariante')


class ClienteCRUDViewTest(TestCase):
    """Testes para as views de CRUD de clientes"""

    def setUp(self):
        """Configuração inicial dos testes"""
        self.client_test = TestClient()

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

        self.usuario = Usuario.objects.create_user(
            username='teste',
            email='teste@teste.com',
            password='senha123',
            empresa=self.empresa
        )

    def test_listar_clientes_requer_autenticacao(self):
        """Testa que listagem requer autenticação"""
        response = self.client_test.get(reverse('listar_clientes'))
        self.assertRedirects(
            response,
            f"{reverse('login')}?next={reverse('listar_clientes')}"
        )

    def test_listar_clientes(self):
        """Testa listagem de clientes"""
        # Criar alguns clientes
        Cliente.objects.create(
            empresa=self.empresa,
            nome='Cliente 1',
            telefone='11111111111'
        )

        Cliente.objects.create(
            empresa=self.empresa,
            nome='Cliente 2',
            telefone='11222222222'
        )

        self.client_test.login(username='teste', password='senha123')
        response = self.client_test.get(reverse('listar_clientes'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'clientes/listar.html')
        self.assertEqual(len(response.context['clientes']), 2)

    def test_buscar_cliente_por_nome(self):
        """Testa busca de cliente por nome"""
        Cliente.objects.create(
            empresa=self.empresa,
            nome='João Silva',
            telefone='11111111111'
        )

        Cliente.objects.create(
            empresa=self.empresa,
            nome='Maria Santos',
            telefone='11222222222'
        )

        self.client_test.login(username='teste', password='senha123')
        response = self.client_test.get(reverse('listar_clientes'), {'busca': 'João'})

        self.assertEqual(len(response.context['clientes']), 1)
        self.assertEqual(response.context['clientes'][0].nome, 'João Silva')

    def test_criar_cliente(self):
        """Testa criação de novo cliente"""
        self.client_test.login(username='teste', password='senha123')

        dados = {
            'nome': 'Novo Cliente',
            'telefone': '11999999999',
            'email': 'novo@teste.com',
            'cpf': '123.456.789-00'
        }

        response = self.client_test.post(reverse('criar_cliente'), dados)

        # Verifica que foi criado
        self.assertEqual(Cliente.objects.count(), 1)
        cliente = Cliente.objects.first()
        self.assertEqual(cliente.nome, 'Novo Cliente')
        self.assertEqual(cliente.telefone, '11999999999')

    def test_editar_cliente(self):
        """Testa edição de cliente existente"""
        cliente = Cliente.objects.create(
            empresa=self.empresa,
            nome='Cliente Original',
            telefone='11111111111'
        )

        self.client_test.login(username='teste', password='senha123')

        dados = {
            'nome': 'Cliente Editado',
            'telefone': '11111111111',
            'email': 'editado@teste.com'
        }

        response = self.client_test.post(
            reverse('editar_cliente', args=[cliente.id]),
            dados
        )

        # Verifica que foi editado
        cliente.refresh_from_db()
        self.assertEqual(cliente.nome, 'Cliente Editado')
        self.assertEqual(cliente.email, 'editado@teste.com')

    def test_deletar_cliente(self):
        """Testa exclusão de cliente"""
        cliente = Cliente.objects.create(
            empresa=self.empresa,
            nome='Cliente a Deletar',
            telefone='11111111111'
        )

        self.client_test.login(username='teste', password='senha123')

        response = self.client_test.post(
            reverse('deletar_cliente', args=[cliente.id])
        )

        # Verifica que foi deletado
        self.assertEqual(Cliente.objects.count(), 0)
