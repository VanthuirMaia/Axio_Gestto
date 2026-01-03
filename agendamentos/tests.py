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


class BotAPITest(TestCase):
    """Testes para a API do Bot (bot_api.py)"""

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

    def test_buscar_ou_criar_cliente_cria_novo(self):
        """Testa que a função cria um novo cliente quando não existe"""
        from agendamentos.bot_api import buscar_ou_criar_cliente

        telefone = '5511999998888'
        dados = {'nome_cliente': 'João Silva'}

        # Não deve existir cliente com esse telefone
        self.assertEqual(Cliente.objects.filter(empresa=self.empresa).count(), 0)

        # Buscar ou criar
        cliente = buscar_ou_criar_cliente(self.empresa, telefone, dados)

        # Deve ter criado o cliente
        self.assertIsNotNone(cliente)
        self.assertEqual(cliente.nome, 'João Silva')
        self.assertEqual(cliente.telefone, '11999998888')
        self.assertEqual(cliente.origem, 'whatsapp')
        self.assertTrue(cliente.ativo)
        self.assertEqual(Cliente.objects.filter(empresa=self.empresa).count(), 1)

    def test_buscar_ou_criar_cliente_reutiliza_existente(self):
        """Testa que a função reutiliza cliente existente (sem duplicação)"""
        from agendamentos.bot_api import buscar_ou_criar_cliente

        telefone = '5511999998888'
        telefone_limpo = '11999998888'

        # Criar cliente manualmente
        cliente_original = Cliente.objects.create(
            empresa=self.empresa,
            nome='Maria Santos',
            telefone=telefone_limpo,
            origem='manual',
            ativo=True
        )

        # Tentar buscar ou criar com mesmo telefone
        dados = {'nome_cliente': 'João Silva'}
        cliente = buscar_ou_criar_cliente(self.empresa, telefone, dados)

        # Deve retornar o mesmo cliente (não duplicar)
        self.assertEqual(cliente.id, cliente_original.id)
        self.assertEqual(cliente.telefone, telefone_limpo)

        # Nome deve ter sido atualizado
        cliente.refresh_from_db()
        self.assertEqual(cliente.nome, 'João Silva')

        # Não deve ter criado novo registro
        self.assertEqual(Cliente.objects.filter(empresa=self.empresa).count(), 1)

    def test_buscar_ou_criar_cliente_multiplas_chamadas_simultaneas(self):
        """Testa que múltiplas chamadas simultâneas não causam duplicação"""
        from agendamentos.bot_api import buscar_ou_criar_cliente

        telefone = '5511999998888'
        dados = {'nome_cliente': 'Cliente WhatsApp'}

        # Simular múltiplas chamadas (como se fosse race condition)
        cliente1 = buscar_ou_criar_cliente(self.empresa, telefone, dados)
        cliente2 = buscar_ou_criar_cliente(self.empresa, telefone, dados)
        cliente3 = buscar_ou_criar_cliente(self.empresa, telefone, dados)

        # Todos devem retornar o mesmo cliente
        self.assertEqual(cliente1.id, cliente2.id)
        self.assertEqual(cliente2.id, cliente3.id)

        # Deve existir apenas 1 cliente
        self.assertEqual(Cliente.objects.filter(empresa=self.empresa).count(), 1)

    def test_buscar_ou_criar_cliente_empresas_diferentes(self):
        """Testa que clientes com mesmo telefone em empresas diferentes não conflitam"""
        from agendamentos.bot_api import buscar_ou_criar_cliente

        empresa2 = Empresa.objects.create(
            nome='Empresa 2',
            slug='empresa-2',
            telefone='11888888888',
            email='empresa2@teste.com',
            cnpj='98.765.432/0001-10'
        )

        telefone = '5511999998888'
        dados = {'nome_cliente': 'João Silva'}

        # Criar cliente na empresa 1
        cliente1 = buscar_ou_criar_cliente(self.empresa, telefone, dados)

        # Criar cliente na empresa 2 (mesmo telefone)
        cliente2 = buscar_ou_criar_cliente(empresa2, telefone, dados)

        # Devem ser clientes diferentes
        self.assertNotEqual(cliente1.id, cliente2.id)
        self.assertEqual(cliente1.telefone, cliente2.telefone)
        self.assertEqual(cliente1.empresa, self.empresa)
        self.assertEqual(cliente2.empresa, empresa2)

        # Deve ter 2 clientes no total (1 por empresa)
        self.assertEqual(Cliente.objects.count(), 2)

    def test_processar_consulta_endereco_completo(self):
        """Testa consulta de endereço quando todos os dados estão preenchidos"""
        from agendamentos.bot_api import processar_consulta_endereco
        from agendamentos.models import LogMensagemBot

        # Atualizar empresa com todos os dados
        self.empresa.endereco = 'Rua das Flores, 123'
        self.empresa.cidade = 'São Paulo'
        self.empresa.estado = 'SP'
        self.empresa.cep = '01234-567'
        self.empresa.google_maps_link = 'https://maps.google.com/?q=SaoPaulo'
        self.empresa.save()

        # Criar log
        log = LogMensagemBot.objects.create(
            empresa=self.empresa,
            telefone='5511999999999',
            mensagem_original='qual o endereço?',
            intencao_detectada='endereco',
            status='parcial'
        )

        # Processar
        resultado = processar_consulta_endereco(self.empresa, log)

        # Verificações
        self.assertTrue(resultado['sucesso'])
        self.assertIn(self.empresa.nome, resultado['mensagem'])
        self.assertIn('Rua das Flores, 123', resultado['mensagem'])
        self.assertIn('São Paulo - SP', resultado['mensagem'])
        self.assertIn('CEP: 01234-567', resultado['mensagem'])
        self.assertIn('https://maps.google.com/?q=SaoPaulo', resultado['mensagem'])
        self.assertEqual(resultado['dados']['endereco'], 'Rua das Flores, 123')
        self.assertEqual(resultado['dados']['google_maps_link'], 'https://maps.google.com/?q=SaoPaulo')

    def test_processar_consulta_endereco_parcial(self):
        """Testa consulta de endereço quando alguns dados estão vazios"""
        from agendamentos.bot_api import processar_consulta_endereco
        from agendamentos.models import LogMensagemBot

        # Empresa com dados mínimos
        self.empresa.endereco = 'Rua Teste, 456'
        self.empresa.cidade = ''
        self.empresa.estado = ''
        self.empresa.cep = ''
        self.empresa.google_maps_link = ''
        self.empresa.save()

        # Criar log
        log = LogMensagemBot.objects.create(
            empresa=self.empresa,
            telefone='5511999999999',
            mensagem_original='onde fica?',
            intencao_detectada='endereco',
            status='parcial'
        )

        # Processar
        resultado = processar_consulta_endereco(self.empresa, log)

        # Verificações
        self.assertTrue(resultado['sucesso'])
        self.assertIn(self.empresa.nome, resultado['mensagem'])
        self.assertIn('Rua Teste, 456', resultado['mensagem'])
        self.assertNotIn('Ver no mapa', resultado['mensagem'])

    def test_processar_consulta_endereco_vazio(self):
        """Testa consulta de endereço quando nenhum dado está preenchido"""
        from agendamentos.bot_api import processar_consulta_endereco
        from agendamentos.models import LogMensagemBot

        # Empresa sem endereço
        self.empresa.endereco = ''
        self.empresa.cidade = ''
        self.empresa.estado = ''
        self.empresa.cep = ''
        self.empresa.google_maps_link = ''
        self.empresa.save()

        # Criar log
        log = LogMensagemBot.objects.create(
            empresa=self.empresa,
            telefone='5511999999999',
            mensagem_original='endereço?',
            intencao_detectada='endereco',
            status='parcial'
        )

        # Processar
        resultado = processar_consulta_endereco(self.empresa, log)

        # Verificações
        self.assertTrue(resultado['sucesso'])
        self.assertIn('Endereço não cadastrado', resultado['mensagem'])

    def test_endpoint_consultar_informacoes_empresa(self):
        """Testa endpoint GET /api/bot/empresa/info/"""
        from rest_framework.test import APIClient
        from empresas.models import Servico, Profissional

        # Criar serviços e profissionais
        servico = Servico.objects.create(
            empresa=self.empresa,
            nome='Corte Masculino',
            descricao='Corte básico',
            preco=30.00,
            duracao_minutos=30,
            ativo=True
        )

        profissional = Profissional.objects.create(
            empresa=self.empresa,
            nome='João Barbeiro',
            email='joao@teste.com',
            telefone='11999999999',
            ativo=True
        )

        # Configurar empresa com endereço
        self.empresa.endereco = 'Rua Teste, 100'
        self.empresa.cidade = 'São Paulo'
        self.empresa.estado = 'SP'
        self.empresa.cep = '01234-567'
        self.empresa.google_maps_link = 'https://maps.google.com/test'
        self.empresa.save()

        # Fazer requisição
        from django.conf import settings
        client = APIClient()
        response = client.get(
            '/api/bot/empresa/info/',
            HTTP_X_API_KEY=settings.GESTTO_API_KEY,
            HTTP_X_EMPRESA_ID=str(self.empresa.id)
        )

        # Verificações
        self.assertEqual(response.status_code, 200)
        data = response.json()

        self.assertTrue(data['sucesso'])
        self.assertEqual(data['empresa']['nome'], 'Empresa Teste')
        self.assertEqual(data['empresa']['endereco'], 'Rua Teste, 100')
        self.assertEqual(data['empresa']['google_maps_link'], 'https://maps.google.com/test')

        # Verificar serviços
        self.assertEqual(len(data['servicos']), 1)
        self.assertEqual(data['servicos'][0]['nome'], 'Corte Masculino')

        # Verificar profissionais
        self.assertEqual(len(data['profissionais']), 1)
        self.assertEqual(data['profissionais'][0]['nome'], 'João Barbeiro')
