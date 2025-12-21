from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils.timezone import now, make_aware, get_current_timezone
from datetime import datetime, timedelta
from decimal import Decimal
from empresas.models import Empresa, Servico, Profissional
from clientes.models import Cliente
from agendamentos.models import Agendamento, StatusAgendamento, DisponibilidadeProfissional


Usuario = get_user_model()


class AgendamentoModelTest(TestCase):
    """Testes para o model Agendamento"""

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

    def test_criar_agendamento(self):
        """Testa criação de agendamento básico"""
        agora = now()
        data_inicio = agora + timedelta(hours=1)
        data_fim = data_inicio + timedelta(minutes=30)

        agendamento = Agendamento.objects.create(
            empresa=self.empresa,
            cliente=self.cliente,
            servico=self.servico,
            profissional=self.profissional,
            data_hora_inicio=data_inicio,
            data_hora_fim=data_fim,
            valor_cobrado=Decimal('50.00')
        )

        self.assertEqual(agendamento.cliente, self.cliente)
        self.assertEqual(agendamento.servico, self.servico)
        self.assertEqual(agendamento.profissional, self.profissional)
        self.assertEqual(agendamento.status, StatusAgendamento.PENDENTE)
        self.assertEqual(agendamento.valor_cobrado, Decimal('50.00'))

    def test_agendamento_string_representation(self):
        """Testa a representação em string do agendamento"""
        agora = now()
        data_inicio = agora + timedelta(hours=1)
        data_fim = data_inicio + timedelta(minutes=30)

        agendamento = Agendamento.objects.create(
            empresa=self.empresa,
            cliente=self.cliente,
            servico=self.servico,
            profissional=self.profissional,
            data_hora_inicio=data_inicio,
            data_hora_fim=data_fim
        )

        expected = f"{self.cliente} - {self.servico} ({data_inicio})"
        self.assertEqual(str(agendamento), expected)

    def test_agendamento_status_choices(self):
        """Testa todos os status disponíveis"""
        agora = now()
        data_inicio = agora + timedelta(hours=1)
        data_fim = data_inicio + timedelta(minutes=30)

        agendamento = Agendamento.objects.create(
            empresa=self.empresa,
            cliente=self.cliente,
            servico=self.servico,
            profissional=self.profissional,
            data_hora_inicio=data_inicio,
            data_hora_fim=data_fim
        )

        # Testa todos os status
        for status in [StatusAgendamento.PENDENTE, StatusAgendamento.CONFIRMADO,
                       StatusAgendamento.CANCELADO, StatusAgendamento.CONCLUIDO,
                       StatusAgendamento.NAO_COMPARECEU]:
            agendamento.status = status
            agendamento.save()
            agendamento.refresh_from_db()
            self.assertEqual(agendamento.status, status)

    def test_agendamento_ordering(self):
        """Testa ordenação de agendamentos (mais recentes primeiro)"""
        agora = now()

        agendamento1 = Agendamento.objects.create(
            empresa=self.empresa,
            cliente=self.cliente,
            servico=self.servico,
            profissional=self.profissional,
            data_hora_inicio=agora + timedelta(hours=1),
            data_hora_fim=agora + timedelta(hours=1, minutes=30)
        )

        agendamento2 = Agendamento.objects.create(
            empresa=self.empresa,
            cliente=self.cliente,
            servico=self.servico,
            profissional=self.profissional,
            data_hora_inicio=agora + timedelta(hours=2),
            data_hora_fim=agora + timedelta(hours=2, minutes=30)
        )

        agendamentos = Agendamento.objects.all()
        self.assertEqual(agendamentos[0], agendamento2)  # Mais recente primeiro
        self.assertEqual(agendamentos[1], agendamento1)


class ConflitosAgendamentoTest(TestCase):
    """Testes para verificação de conflitos de horários"""

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

    def test_detectar_conflito_horario_exato(self):
        """Testa detecção de conflito com horário exatamente igual"""
        agora = now()
        data_inicio = agora + timedelta(hours=1)
        data_fim = data_inicio + timedelta(minutes=30)

        # Criar primeiro agendamento
        Agendamento.objects.create(
            empresa=self.empresa,
            cliente=self.cliente,
            servico=self.servico,
            profissional=self.profissional,
            data_hora_inicio=data_inicio,
            data_hora_fim=data_fim
        )

        # Verificar conflito
        conflito = Agendamento.objects.filter(
            empresa=self.empresa,
            profissional=self.profissional,
            data_hora_inicio__lt=data_fim,
            data_hora_fim__gt=data_inicio
        ).exists()

        self.assertTrue(conflito)

    def test_detectar_conflito_parcial_inicio(self):
        """Testa detecção de conflito quando novo agendamento inicia durante outro"""
        agora = now()

        # Agendamento existente: 10:00 - 10:30
        agendamento1_inicio = agora + timedelta(hours=1)
        agendamento1_fim = agendamento1_inicio + timedelta(minutes=30)

        Agendamento.objects.create(
            empresa=self.empresa,
            cliente=self.cliente,
            servico=self.servico,
            profissional=self.profissional,
            data_hora_inicio=agendamento1_inicio,
            data_hora_fim=agendamento1_fim
        )

        # Novo agendamento: 10:15 - 10:45 (conflita)
        novo_inicio = agendamento1_inicio + timedelta(minutes=15)
        novo_fim = novo_inicio + timedelta(minutes=30)

        conflito = Agendamento.objects.filter(
            empresa=self.empresa,
            profissional=self.profissional,
            data_hora_inicio__lt=novo_fim,
            data_hora_fim__gt=novo_inicio
        ).exists()

        self.assertTrue(conflito)

    def test_detectar_conflito_engloba_outro(self):
        """Testa detecção de conflito quando novo agendamento engloba outro"""
        agora = now()

        # Agendamento existente: 10:15 - 10:45
        agendamento1_inicio = agora + timedelta(hours=1, minutes=15)
        agendamento1_fim = agendamento1_inicio + timedelta(minutes=30)

        Agendamento.objects.create(
            empresa=self.empresa,
            cliente=self.cliente,
            servico=self.servico,
            profissional=self.profissional,
            data_hora_inicio=agendamento1_inicio,
            data_hora_fim=agendamento1_fim
        )

        # Novo agendamento: 10:00 - 11:00 (engloba o existente)
        novo_inicio = agora + timedelta(hours=1)
        novo_fim = novo_inicio + timedelta(hours=1)

        conflito = Agendamento.objects.filter(
            empresa=self.empresa,
            profissional=self.profissional,
            data_hora_inicio__lt=novo_fim,
            data_hora_fim__gt=novo_inicio
        ).exists()

        self.assertTrue(conflito)

    def test_nao_conflito_sequencial(self):
        """Testa que agendamentos sequenciais não conflitam"""
        agora = now()

        # Agendamento 1: 10:00 - 10:30
        agendamento1_inicio = agora + timedelta(hours=1)
        agendamento1_fim = agendamento1_inicio + timedelta(minutes=30)

        Agendamento.objects.create(
            empresa=self.empresa,
            cliente=self.cliente,
            servico=self.servico,
            profissional=self.profissional,
            data_hora_inicio=agendamento1_inicio,
            data_hora_fim=agendamento1_fim
        )

        # Agendamento 2: 10:30 - 11:00 (sequencial, sem conflito)
        novo_inicio = agendamento1_fim
        novo_fim = novo_inicio + timedelta(minutes=30)

        conflito = Agendamento.objects.filter(
            empresa=self.empresa,
            profissional=self.profissional,
            data_hora_inicio__lt=novo_fim,
            data_hora_fim__gt=novo_inicio
        ).exclude(data_hora_fim=novo_inicio).exists()

        self.assertFalse(conflito)

    def test_nao_conflito_profissionais_diferentes(self):
        """Testa que profissionais diferentes podem ter mesmo horário"""
        profissional2 = Profissional.objects.create(
            empresa=self.empresa,
            nome='Maria Cabeleireira',
            email='maria@teste.com',
            telefone='11666666666'
        )

        agora = now()
        data_inicio = agora + timedelta(hours=1)
        data_fim = data_inicio + timedelta(minutes=30)

        # Agendamento profissional 1
        Agendamento.objects.create(
            empresa=self.empresa,
            cliente=self.cliente,
            servico=self.servico,
            profissional=self.profissional,
            data_hora_inicio=data_inicio,
            data_hora_fim=data_fim
        )

        # Mesmo horário, profissional diferente
        conflito = Agendamento.objects.filter(
            empresa=self.empresa,
            profissional=profissional2,  # Profissional diferente
            data_hora_inicio__lt=data_fim,
            data_hora_fim__gt=data_inicio
        ).exists()

        self.assertFalse(conflito)


class DisponibilidadeProfissionalTest(TestCase):
    """Testes para o model DisponibilidadeProfissional"""

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

        self.profissional = Profissional.objects.create(
            empresa=self.empresa,
            nome='João Barbeiro',
            email='joao@teste.com',
            telefone='11888888888'
        )

    def test_criar_disponibilidade(self):
        """Testa criação de disponibilidade"""
        disponibilidade = DisponibilidadeProfissional.objects.create(
            profissional=self.profissional,
            dia_semana=0,  # Segunda
            hora_inicio=datetime.strptime('09:00', '%H:%M').time(),
            hora_fim=datetime.strptime('18:00', '%H:%M').time()
        )

        self.assertEqual(disponibilidade.profissional, self.profissional)
        self.assertEqual(disponibilidade.dia_semana, 0)
        self.assertTrue(disponibilidade.ativo)

    def test_disponibilidade_string_representation(self):
        """Testa a representação em string da disponibilidade"""
        disponibilidade = DisponibilidadeProfissional.objects.create(
            profissional=self.profissional,
            dia_semana=0,  # Segunda
            hora_inicio=datetime.strptime('09:00', '%H:%M').time(),
            hora_fim=datetime.strptime('18:00', '%H:%M').time()
        )

        self.assertIn('Segunda', str(disponibilidade))
        self.assertIn('09:00', str(disponibilidade))
        self.assertIn('18:00', str(disponibilidade))


class AgendamentoViewTest(TestCase):
    """Testes para as views de agendamento"""

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

    def test_calendario_requer_autenticacao(self):
        """Testa que o calendário requer autenticação"""
        response = self.client.get(reverse('agendamentos:calendario'))
        self.assertRedirects(response, f"{reverse('login')}?next={reverse('agendamentos:calendario')}")

    def test_calendario_renderiza_corretamente(self):
        """Testa que o calendário renderiza corretamente"""
        self.client.login(username='teste', password='senha123')
        response = self.client.get(reverse('agendamentos:calendario'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'agendamentos/calendario.html')
        self.assertIn('empresa', response.context)

    def test_api_agendamentos_retorna_json(self):
        """Testa que a API de agendamentos retorna JSON válido"""
        self.client.login(username='teste', password='senha123')

        # Criar agendamento
        agora = now()
        data_agendamento = agora + timedelta(hours=1)

        Agendamento.objects.create(
            empresa=self.empresa,
            cliente=self.cliente,
            servico=self.servico,
            profissional=self.profissional,
            data_hora_inicio=data_agendamento,
            data_hora_fim=data_agendamento + timedelta(minutes=30),
            status='confirmado',
            valor_cobrado=Decimal('50.00')
        )

        # A API requer parâmetros de mês e ano
        mes = data_agendamento.month
        ano = data_agendamento.year

        response = self.client.get(
            reverse('agendamentos:api_agendamentos'),
            {'mes': mes, 'ano': ano}
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')

        # Verificar estrutura do JSON
        import json
        data = json.loads(response.content)
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 1)
        self.assertIn('title', data[0])
        self.assertIn('start', data[0])
        self.assertIn('end', data[0])
