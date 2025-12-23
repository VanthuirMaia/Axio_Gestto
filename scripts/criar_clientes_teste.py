# -*- coding: utf-8 -*-
"""
Criar clientes de teste para a Barbearia
"""

import os
import sys
import django
from pathlib import Path

# Forçar encoding UTF-8 no Windows
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# Configurar Django
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

# Imports após setup do Django
from datetime import date
from clientes.models import Cliente
from empresas.models import Empresa


def criar_clientes_teste():
    """Cria clientes de teste para a barbearia"""

    # Buscar empresa
    empresa = Empresa.objects.filter(ativa=True).first()
    if not empresa:
        print("[ERRO] Nenhuma empresa ativa encontrada!")
        return False

    print(f"\n[OK] Empresa: {empresa.nome}\n")

    # ============================================
    # CLIENTES DE TESTE
    # ============================================
    print("="*70)
    print("[CRIANDO CLIENTES DE TESTE]")
    print("="*70)

    clientes_data = [
        {
            'nome': 'João Silva Santos',
            'email': 'joao.silva@email.com',
            'telefone': '87999991234',
            'cpf': '123.456.789-01',
            'data_nascimento': date(1990, 5, 15),
            'endereco': 'Rua das Flores, 123',
            'cidade': 'Garanhuns',
            'estado': 'PE',
            'cep': '55290-000',
            'notas': 'Cliente desde 2023. Prefere corte baixo nas laterais.'
        },
        {
            'nome': 'Carlos Eduardo Oliveira',
            'email': 'carlos.oliveira@email.com',
            'telefone': '87999992345',
            'cpf': '234.567.890-12',
            'data_nascimento': date(1985, 8, 22),
            'endereco': 'Av. Santo Antônio, 456',
            'cidade': 'Garanhuns',
            'estado': 'PE',
            'cep': '55291-000',
            'notas': 'Alérgico a produtos com perfume forte.'
        },
        {
            'nome': 'Rafael Almeida Costa',
            'email': 'rafael.costa@email.com',
            'telefone': '87999993456',
            'cpf': '345.678.901-23',
            'data_nascimento': date(1995, 12, 10),
            'endereco': 'Rua Heliópolis, 789',
            'cidade': 'Garanhuns',
            'estado': 'PE',
            'cep': '55292-000',
            'notas': 'Gosta de conversar sobre futebol.'
        },
        {
            'nome': 'Pedro Henrique Souza',
            'email': 'pedro.souza@email.com',
            'telefone': '87999994567',
            'cpf': '456.789.012-34',
            'data_nascimento': date(1988, 3, 7),
            'endereco': 'Rua Boa Vista, 321',
            'cidade': 'Garanhuns',
            'estado': 'PE',
            'cep': '55293-000',
            'notas': 'Agendamento fixo toda sexta às 16h.'
        },
        {
            'nome': 'Lucas Ferreira Lima',
            'email': 'lucas.lima@email.com',
            'telefone': '87999995678',
            'cpf': '567.890.123-45',
            'data_nascimento': date(1992, 11, 30),
            'endereco': 'Av. Euclides Dourado, 654',
            'cidade': 'Garanhuns',
            'estado': 'PE',
            'cep': '55294-000',
            'notas': 'Sempre pede café. Cliente VIP.'
        },
        {
            'nome': 'Marcos Vinicius Rocha',
            'email': 'marcos.rocha@email.com',
            'telefone': '87999996789',
            'cpf': '678.901.234-56',
            'data_nascimento': date(1987, 6, 18),
            'endereco': 'Rua São José, 147',
            'cidade': 'Garanhuns',
            'estado': 'PE',
            'cep': '55295-000',
            'notas': 'Gosta de design na barba.'
        },
        {
            'nome': 'Thiago Martins Pereira',
            'email': 'thiago.pereira@email.com',
            'telefone': '87999997890',
            'cpf': '789.012.345-67',
            'data_nascimento': date(1993, 9, 25),
            'endereco': 'Rua Quintino Bocaiuva, 258',
            'cidade': 'Garanhuns',
            'estado': 'PE',
            'cep': '55296-000',
            'notas': 'Cliente novo. Veio por indicação do João Silva.'
        },
        {
            'nome': 'André Luiz Barbosa',
            'email': 'andre.barbosa@email.com',
            'telefone': '87999998901',
            'cpf': '890.123.456-78',
            'data_nascimento': date(1991, 2, 14),
            'endereco': 'Av. Rui Barbosa, 369',
            'cidade': 'Garanhuns',
            'estado': 'PE',
            'cep': '55297-000',
            'notas': 'Prefere atendimento com Pedro.'
        },
        {
            'nome': 'Felipe Augusto Mendes',
            'email': 'felipe.mendes@email.com',
            'telefone': '87999999012',
            'cpf': '901.234.567-89',
            'data_nascimento': date(1989, 7, 3),
            'endereco': 'Rua Dom Pedro II, 741',
            'cidade': 'Garanhuns',
            'estado': 'PE',
            'cep': '55298-000',
            'notas': 'Sempre agenda pelo WhatsApp.'
        },
        {
            'nome': 'Gabriel Santos Araújo',
            'email': 'gabriel.araujo@email.com',
            'telefone': '87988881234',
            'cpf': '012.345.678-90',
            'data_nascimento': date(1994, 4, 20),
            'endereco': 'Rua XV de Novembro, 852',
            'cidade': 'Garanhuns',
            'estado': 'PE',
            'cep': '55299-000',
            'notas': 'Gosta de conversar sobre tecnologia.'
        },
        {
            'nome': 'Rodrigo Alves Cardoso',
            'email': 'rodrigo.cardoso@email.com',
            'telefone': '87988882345',
            'cpf': '111.222.333-44',
            'data_nascimento': date(1986, 1, 12),
            'endereco': 'Av. Caruaru, 963',
            'cidade': 'Garanhuns',
            'estado': 'PE',
            'cep': '55300-000',
            'notas': 'Cliente desde a inauguração.'
        },
        {
            'nome': 'Bruno Henrique Dias',
            'email': 'bruno.dias@email.com',
            'telefone': '87988883456',
            'cpf': '222.333.444-55',
            'data_nascimento': date(1996, 10, 8),
            'endereco': 'Rua Dantas Barreto, 159',
            'cidade': 'Garanhuns',
            'estado': 'PE',
            'cep': '55301-000',
            'notas': 'Prefere horários pela manhã.'
        }
    ]

    criados = 0
    atualizados = 0

    for cliente_data in clientes_data:
        try:
            # Criar ou atualizar cliente (unique por telefone)
            cliente, created = Cliente.objects.update_or_create(
                empresa=empresa,
                telefone=cliente_data['telefone'],
                defaults={
                    'nome': cliente_data['nome'],
                    'email': cliente_data['email'],
                    'cpf': cliente_data['cpf'],
                    'data_nascimento': cliente_data['data_nascimento'],
                    'endereco': cliente_data['endereco'],
                    'cidade': cliente_data['cidade'],
                    'estado': cliente_data['estado'],
                    'cep': cliente_data['cep'],
                    'notas': cliente_data['notas'],
                    'ativo': True
                }
            )

            if created:
                criados += 1
                status = "[NOVO]"
            else:
                atualizados += 1
                status = "[ATU]"

            print(f"{status} {cliente_data['nome']:35} | {cliente_data['telefone']:15} | {cliente_data['email']}")

        except Exception as e:
            print(f"[ERRO] {cliente_data['nome']}: {e}")
            continue

    print(f"\n[RESUMO CLIENTES]")
    print(f"  Criados: {criados}")
    print(f"  Atualizados: {atualizados}")

    # ============================================
    # RESUMO FINAL
    # ============================================
    total_clientes = Cliente.objects.filter(empresa=empresa).count()

    print("\n" + "="*70)
    print("[CONCLUIDO]")
    print("="*70)
    print(f"\nTotal de clientes no banco: {total_clientes}")
    print("\n[DADOS DISPONIVEIS]")
    print(f"  Empresa: {empresa.nome}")
    print(f"  Servicos: {empresa.servicos.count()}")
    print(f"  Profissionais: {empresa.profissionais.count()}")
    print(f"  Clientes: {total_clientes}")
    print(f"  Horarios de Funcionamento: {empresa.horarios_funcionamento.count()}")
    print(f"  Datas Especiais: {empresa.datas_especiais.count()}")
    print("\n[PROXIMOS PASSOS]")
    print("  1. Criar agendamentos de teste (opcional)")
    print("  2. Testar fluxo completo de agendamento via n8n")
    print("  3. Testar APIs de horarios disponiveis\n")

    return True


if __name__ == '__main__':
    try:
        criar_clientes_teste()
    except Exception as e:
        print(f"\n[ERRO FATAL] {e}")
        import traceback
        traceback.print_exc()
