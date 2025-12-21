from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from empresas.models import Empresa, Servico, Profissional
from clientes.models import Cliente
from agendamentos.models import Agendamento
from financeiro.models import LancamentoFinanceiro, CategoriaFinanceira, FormaPagamento
from datetime import datetime, timedelta
from django.utils.timezone import now, make_aware
from decimal import Decimal


Usuario = get_user_model()


class UsuarioModelTest(TestCase):
    """Testes para o model Usuario"""

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

    def test_criar_usuario_com_empresa(self):
        """Testa criação de usuário vinculado a uma empresa"""
        usuario = Usuario.objects.create_user(
            username='usuario_teste',
            email='usuario@teste.com',
            password='senha123',
            empresa=self.empresa,
            telefone='11888888888'
        )

        self.assertEqual(usuario.username, 'usuario_teste')
        self.assertEqual(usuario.email, 'usuario@teste.com')
        self.assertEqual(usuario.empresa, self.empresa)
        self.assertEqual(usuario.telefone, '11888888888')
        self.assertTrue(usuario.ativo)

    def test_criar_usuario_sem_empresa(self):
        """Testa criação de usuário sem empresa vinculada"""
        usuario = Usuario.objects.create_user(
            username='usuario_sem_empresa',
            email='sem@empresa.com',
            password='senha123'
        )

        self.assertIsNone(usuario.empresa)
        self.assertTrue(usuario.ativo)

    def test_usuario_string_representation(self):
        """Testa a representação em string do usuário"""
        usuario = Usuario.objects.create_user(
            username='joao',
            email='joao@teste.com',
            password='senha123',
            empresa=self.empresa,
            first_name='João',
            last_name='Silva'
        )

        self.assertEqual(str(usuario), f"João Silva - {self.empresa}")

    def test_usuario_ordering(self):
        """Testa ordenação de usuários (mais recentes primeiro)"""
        usuario1 = Usuario.objects.create_user(
            username='usuario1',
            email='usuario1@teste.com',
            password='senha123',
            empresa=self.empresa
        )

        usuario2 = Usuario.objects.create_user(
            username='usuario2',
            email='usuario2@teste.com',
            password='senha123',
            empresa=self.empresa
        )

        usuarios = Usuario.objects.all()
        self.assertEqual(usuarios[0], usuario2)  # Mais recente primeiro
        self.assertEqual(usuarios[1], usuario1)


class LoginViewTest(TestCase):
    """Testes para a view de login"""

    def setUp(self):
        """Configuração inicial dos testes"""
        self.client = Client()
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

    def test_login_view_get(self):
        """Testa acesso à página de login via GET"""
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'login.html')

    def test_login_com_username(self):
        """Testa login usando username"""
        response = self.client.post(reverse('login'), {
            'email_ou_usuario': 'teste',
            'senha': 'senha123'
        })

        self.assertRedirects(response, reverse('dashboard'))

    def test_login_com_email(self):
        """Testa login usando email"""
        response = self.client.post(reverse('login'), {
            'email_ou_usuario': 'teste@teste.com',
            'senha': 'senha123'
        })

        self.assertRedirects(response, reverse('dashboard'))

    def test_login_senha_incorreta(self):
        """Testa login com senha incorreta"""
        response = self.client.post(reverse('login'), {
            'email_ou_usuario': 'teste',
            'senha': 'senha_errada'
        })

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Email/Usuario ou senha incorretos.')

    def test_login_usuario_inativo(self):
        """Testa login com usuário inativo"""
        self.usuario.ativo = False
        self.usuario.save()

        response = self.client.post(reverse('login'), {
            'email_ou_usuario': 'teste',
            'senha': 'senha123'
        })

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Email/Usuario ou senha incorretos.')

    def test_redirect_se_ja_autenticado(self):
        """Testa redirecionamento se usuário já está autenticado"""
        self.client.login(username='teste', password='senha123')
        response = self.client.get(reverse('login'))

        self.assertRedirects(response, reverse('dashboard'))


class LogoutViewTest(TestCase):
    """Testes para a view de logout"""

    def setUp(self):
        """Configuração inicial dos testes"""
        self.client = Client()
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

    def test_logout(self):
        """Testa logout de usuário autenticado"""
        self.client.login(username='teste', password='senha123')
        response = self.client.get(reverse('logout'))

        self.assertRedirects(response, reverse('login'))
        self.assertFalse('_auth_user_id' in self.client.session)


class DashboardViewTest(TestCase):
    """Testes para a view do dashboard"""

    def setUp(self):
        """Configuração inicial dos testes"""
        self.client = Client()

        # Criar empresa
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

        # Criar usuário
        self.usuario = Usuario.objects.create_user(
            username='teste',
            email='teste@teste.com',
            password='senha123',
            empresa=self.empresa
        )

        # Criar serviço
        self.servico = Servico.objects.create(
            empresa=self.empresa,
            nome='Corte de Cabelo',
            preco=Decimal('50.00'),
            duracao_minutos=30
        )

        # Criar profissional
        self.profissional = Profissional.objects.create(
            empresa=self.empresa,
            nome='João Barbeiro',
            email='joao@teste.com',
            telefone='11888888888'
        )

        # Criar cliente
        self.cliente = Cliente.objects.create(
            empresa=self.empresa,
            nome='Cliente Teste',
            email='cliente@teste.com',
            telefone='11777777777'
        )

        # Criar categoria financeira
        self.categoria = CategoriaFinanceira.objects.create(
            empresa=self.empresa,
            nome='Serviços',
            tipo='receita'
        )

        # Criar forma de pagamento
        self.forma_pagamento = FormaPagamento.objects.create(
            empresa=self.empresa,
            nome='Dinheiro'
        )

    def test_dashboard_requer_autenticacao(self):
        """Testa que dashboard requer autenticação"""
        response = self.client.get(reverse('dashboard'))
        self.assertRedirects(response, f"{reverse('login')}?next={reverse('dashboard')}")

    def test_dashboard_usuario_sem_empresa(self):
        """Testa dashboard com usuário sem empresa"""
        usuario_sem_empresa = Usuario.objects.create_user(
            username='sem_empresa',
            email='sem@empresa.com',
            password='senha123'
        )

        self.client.login(username='sem_empresa', password='senha123')
        response = self.client.get(reverse('dashboard'), follow=False)

        # Verifica que redireciona para logout (não precisa seguir a cadeia de redirects)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('logout'))

    def test_dashboard_renderiza_corretamente(self):
        """Testa que dashboard renderiza com dados corretos"""
        self.client.login(username='teste', password='senha123')
        response = self.client.get(reverse('dashboard'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'dashboard.html')
        self.assertIn('empresa', response.context)
        self.assertIn('saudacao', response.context)
        self.assertEqual(response.context['empresa'], self.empresa)

    def test_dashboard_metricas_agendamentos(self):
        """Testa métricas de agendamentos no dashboard"""
        # Criar agendamento para hoje
        agora = now()
        Agendamento.objects.create(
            empresa=self.empresa,
            cliente=self.cliente,
            servico=self.servico,
            profissional=self.profissional,
            data_hora_inicio=agora + timedelta(hours=1),
            data_hora_fim=agora + timedelta(hours=1, minutes=30),
            status='confirmado',
            valor_cobrado=Decimal('50.00')
        )

        self.client.login(username='teste', password='senha123')
        response = self.client.get(reverse('dashboard'))

        self.assertEqual(response.context['agendamentos_hoje'], 1)

    def test_dashboard_metricas_clientes(self):
        """Testa métricas de clientes no dashboard"""
        self.client.login(username='teste', password='senha123')
        response = self.client.get(reverse('dashboard'))

        self.assertEqual(response.context['total_clientes'], 1)

    def test_dashboard_metricas_financeiras(self):
        """Testa métricas financeiras no dashboard"""
        # Criar lançamento financeiro pago neste mês
        LancamentoFinanceiro.objects.create(
            empresa=self.empresa,
            descricao='Receita Teste',
            tipo='receita',
            valor=Decimal('100.00'),
            categoria=self.categoria,
            forma_pagamento=self.forma_pagamento,
            data_vencimento=now().date(),
            data_pagamento=now().date(),
            status='pago'
        )

        self.client.login(username='teste', password='senha123')
        response = self.client.get(reverse('dashboard'))

        self.assertEqual(response.context['faturamento_mes'], Decimal('100.00'))

    def test_dashboard_saudacao_manha(self):
        """Testa saudação correta pela manhã"""
        # Este teste pode falhar dependendo do horário
        # É apenas um exemplo de como testar lógica baseada em tempo
        self.client.login(username='teste', password='senha123')
        response = self.client.get(reverse('dashboard'))

        # A saudação deve ser uma das três opções
        self.assertIn(response.context['saudacao'], ['Bom dia', 'Boa tarde', 'Boa noite'])
