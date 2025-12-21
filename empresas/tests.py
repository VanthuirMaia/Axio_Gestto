from django.test import TestCase
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from empresas.models import Empresa, Servico, Profissional
from decimal import Decimal


class EmpresaModelTest(TestCase):
    """Testes para o model Empresa"""

    def test_criar_empresa(self):
        """Testa criação de empresa com todos os campos obrigatórios"""
        empresa = Empresa.objects.create(
            nome='Salão Teste',
            slug='salao-teste',
            telefone='11999999999',
            email='salao@teste.com',
            endereco='Rua Teste, 123',
            cidade='São Paulo',
            estado='SP',
            cep='01234-567',
            cnpj='12.345.678/0001-90'
        )

        self.assertEqual(empresa.nome, 'Salão Teste')
        self.assertEqual(empresa.slug, 'salao-teste')
        self.assertTrue(empresa.ativa)
        self.assertEqual(empresa.cor_primaria, '#1e3a8a')  # Valor padrão
        self.assertEqual(empresa.cor_secundaria, '#3b82f6')  # Valor padrão

    def test_empresa_string_representation(self):
        """Testa a representação em string da empresa"""
        empresa = Empresa.objects.create(
            nome='Barbearia XYZ',
            slug='barbearia-xyz',
            telefone='11888888888',
            email='barbearia@teste.com',
            endereco='Av. Teste, 456',
            cidade='Rio de Janeiro',
            estado='RJ',
            cep='20000-000',
            cnpj='98.765.432/0001-10'
        )

        self.assertEqual(str(empresa), 'Barbearia XYZ')

    def test_empresa_nome_unico(self):
        """Testa que o nome da empresa deve ser único"""
        Empresa.objects.create(
            nome='Empresa Única',
            slug='empresa-unica-1',
            telefone='11999999999',
            email='empresa1@teste.com',
            endereco='Rua Teste, 123',
            cidade='São Paulo',
            estado='SP',
            cep='01234-567',
            cnpj='11.111.111/0001-11'
        )

        with self.assertRaises(IntegrityError):
            Empresa.objects.create(
                nome='Empresa Única',  # Nome duplicado
                slug='empresa-unica-2',
                telefone='11888888888',
                email='empresa2@teste.com',
                endereco='Rua Teste, 456',
                cidade='São Paulo',
                estado='SP',
                cep='01234-567',
                cnpj='22.222.222/0001-22'
            )

    def test_empresa_cnpj_unico(self):
        """Testa que o CNPJ da empresa deve ser único"""
        Empresa.objects.create(
            nome='Empresa 1',
            slug='empresa-1',
            telefone='11999999999',
            email='empresa1@teste.com',
            endereco='Rua Teste, 123',
            cidade='São Paulo',
            estado='SP',
            cep='01234-567',
            cnpj='11.111.111/0001-11'
        )

        with self.assertRaises(IntegrityError):
            Empresa.objects.create(
                nome='Empresa 2',
                slug='empresa-2',
                telefone='11888888888',
                email='empresa2@teste.com',
                endereco='Rua Teste, 456',
                cidade='São Paulo',
                estado='SP',
                cep='01234-567',
                cnpj='11.111.111/0001-11'  # CNPJ duplicado
            )

    def test_empresa_cores_customizadas(self):
        """Testa definição de cores customizadas"""
        empresa = Empresa.objects.create(
            nome='Empresa Colorida',
            slug='empresa-colorida',
            cor_primaria='#FF5733',
            cor_secundaria='#C70039',
            telefone='11999999999',
            email='empresa@teste.com',
            endereco='Rua Teste, 123',
            cidade='São Paulo',
            estado='SP',
            cep='01234-567',
            cnpj='11.111.111/0001-11'
        )

        self.assertEqual(empresa.cor_primaria, '#FF5733')
        self.assertEqual(empresa.cor_secundaria, '#C70039')


class ServicoModelTest(TestCase):
    """Testes para o model Servico"""

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

    def test_criar_servico(self):
        """Testa criação de serviço"""
        servico = Servico.objects.create(
            empresa=self.empresa,
            nome='Corte de Cabelo',
            descricao='Corte masculino',
            preco=Decimal('50.00'),
            duracao_minutos=30
        )

        self.assertEqual(servico.nome, 'Corte de Cabelo')
        self.assertEqual(servico.preco, Decimal('50.00'))
        self.assertEqual(servico.duracao_minutos, 30)
        self.assertTrue(servico.ativo)

    def test_servico_string_representation(self):
        """Testa a representação em string do serviço"""
        servico = Servico.objects.create(
            empresa=self.empresa,
            nome='Barba',
            preco=Decimal('30.00'),
            duracao_minutos=20
        )

        self.assertEqual(str(servico), f"Barba - {self.empresa}")

    def test_servico_preco_minimo(self):
        """Testa validação de preço mínimo (não pode ser negativo)"""
        servico = Servico(
            empresa=self.empresa,
            nome='Serviço Inválido',
            preco=Decimal('-10.00'),  # Preço negativo
            duracao_minutos=30
        )

        with self.assertRaises(ValidationError):
            servico.full_clean()

    def test_servico_duracao_minima(self):
        """Testa validação de duração mínima (deve ser pelo menos 1)"""
        servico = Servico(
            empresa=self.empresa,
            nome='Serviço Inválido',
            preco=Decimal('50.00'),
            duracao_minutos=0  # Duração inválida
        )

        with self.assertRaises(ValidationError):
            servico.full_clean()

    def test_servico_nome_unico_por_empresa(self):
        """Testa que o nome do serviço deve ser único por empresa"""
        Servico.objects.create(
            empresa=self.empresa,
            nome='Corte Premium',
            preco=Decimal('80.00'),
            duracao_minutos=45
        )

        with self.assertRaises(IntegrityError):
            Servico.objects.create(
                empresa=self.empresa,
                nome='Corte Premium',  # Nome duplicado na mesma empresa
                preco=Decimal('90.00'),
                duracao_minutos=60
            )

    def test_servico_mesmo_nome_empresas_diferentes(self):
        """Testa que serviços podem ter o mesmo nome em empresas diferentes"""
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

        Servico.objects.create(
            empresa=self.empresa,
            nome='Corte',
            preco=Decimal('50.00'),
            duracao_minutos=30
        )

        # Deve permitir criar serviço com mesmo nome em empresa diferente
        servico2 = Servico.objects.create(
            empresa=empresa2,
            nome='Corte',
            preco=Decimal('60.00'),
            duracao_minutos=40
        )

        self.assertEqual(servico2.nome, 'Corte')


class ProfissionalModelTest(TestCase):
    """Testes para o model Profissional"""

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

        self.servico1 = Servico.objects.create(
            empresa=self.empresa,
            nome='Corte',
            preco=Decimal('50.00'),
            duracao_minutos=30
        )

        self.servico2 = Servico.objects.create(
            empresa=self.empresa,
            nome='Barba',
            preco=Decimal('30.00'),
            duracao_minutos=20
        )

    def test_criar_profissional(self):
        """Testa criação de profissional"""
        profissional = Profissional.objects.create(
            empresa=self.empresa,
            nome='João Silva',
            email='joao@teste.com',
            telefone='11777777777',
            comissao_percentual=Decimal('30.00')
        )

        self.assertEqual(profissional.nome, 'João Silva')
        self.assertEqual(profissional.email, 'joao@teste.com')
        self.assertEqual(profissional.comissao_percentual, Decimal('30.00'))
        self.assertTrue(profissional.ativo)
        self.assertEqual(profissional.cor_hex, '#1e3a8a')  # Cor padrão

    def test_profissional_string_representation(self):
        """Testa a representação em string do profissional"""
        profissional = Profissional.objects.create(
            empresa=self.empresa,
            nome='Maria Souza',
            email='maria@teste.com',
            telefone='11666666666'
        )

        self.assertEqual(str(profissional), f"Maria Souza - {self.empresa}")

    def test_profissional_com_servicos(self):
        """Testa associação de serviços ao profissional"""
        profissional = Profissional.objects.create(
            empresa=self.empresa,
            nome='Pedro Santos',
            email='pedro@teste.com',
            telefone='11555555555'
        )

        profissional.servicos.add(self.servico1, self.servico2)

        self.assertEqual(profissional.servicos.count(), 2)
        self.assertIn(self.servico1, profissional.servicos.all())
        self.assertIn(self.servico2, profissional.servicos.all())

    def test_profissional_email_unico_por_empresa(self):
        """Testa que o email do profissional deve ser único por empresa"""
        Profissional.objects.create(
            empresa=self.empresa,
            nome='João',
            email='joao@teste.com',
            telefone='11777777777'
        )

        with self.assertRaises(IntegrityError):
            Profissional.objects.create(
                empresa=self.empresa,
                nome='João Duplicado',
                email='joao@teste.com',  # Email duplicado na mesma empresa
                telefone='11888888888'
            )

    def test_profissional_mesmo_email_empresas_diferentes(self):
        """Testa que profissionais podem ter o mesmo email em empresas diferentes"""
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

        Profissional.objects.create(
            empresa=self.empresa,
            nome='João',
            email='profissional@teste.com',
            telefone='11777777777'
        )

        # Deve permitir criar profissional com mesmo email em empresa diferente
        profissional2 = Profissional.objects.create(
            empresa=empresa2,
            nome='João Outro',
            email='profissional@teste.com',
            telefone='11666666666'
        )

        self.assertEqual(profissional2.email, 'profissional@teste.com')

    def test_profissional_cor_customizada(self):
        """Testa definição de cor customizada para o calendário"""
        profissional = Profissional.objects.create(
            empresa=self.empresa,
            nome='Ana Costa',
            email='ana@teste.com',
            telefone='11444444444',
            cor_hex='#FF5733'
        )

        self.assertEqual(profissional.cor_hex, '#FF5733')

    def test_profissional_comissao_minima(self):
        """Testa validação de comissão mínima (não pode ser negativa)"""
        profissional = Profissional(
            empresa=self.empresa,
            nome='Carlos',
            email='carlos@teste.com',
            telefone='11333333333',
            comissao_percentual=Decimal('-10.00')  # Comissão negativa
        )

        with self.assertRaises(ValidationError):
            profissional.full_clean()
