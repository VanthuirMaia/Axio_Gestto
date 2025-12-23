# -*- coding: utf-8 -*-
"""
Importar Serviços e Profissionais da Brandão Barbearia
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
import pandas as pd
from decimal import Decimal
from empresas.models import Empresa, Servico, Profissional


def importar_servicos_e_profissionais():
    """Importa serviços da planilha e cria profissionais"""

    # Buscar empresa
    empresa = Empresa.objects.filter(ativa=True).first()
    if not empresa:
        print("[ERRO] Nenhuma empresa ativa encontrada!")
        return False

    print(f"\n[OK] Empresa: {empresa.nome}\n")

    # ============================================
    # IMPORTAR SERVIÇOS
    # ============================================
    print("="*60)
    print("[IMPORTANDO SERVICOS]")
    print("="*60)

    # Usar a planilha (1) que tem os dados
    planilha_path = BASE_DIR / 'data' / 'Serviços Barbearia (1).xlsx'

    if not planilha_path.exists():
        print(f"[ERRO] Arquivo não encontrado: {planilha_path}")
        return False

    try:
        df = pd.read_excel(planilha_path, sheet_name='Serviços')
        print(f"[OK] Aba 'Serviços' encontrada: {len(df)} serviços\n")

        servicos_criados = 0
        servicos_atualizados = 0

        for idx, row in df.iterrows():
            if pd.isna(row.get('Serviço')):
                continue

            nome = str(row['Serviço']).strip()
            descricao = str(row.get('Descrição Curta', '')).strip() if not pd.isna(row.get('Descrição Curta')) else ''
            preco = Decimal(str(row.get('Preço (R$)', 0)))
            duracao = int(row.get('Duração (Min)', 30))

            # Criar ou atualizar
            servico, created = Servico.objects.update_or_create(
                empresa=empresa,
                nome=nome,
                defaults={
                    'descricao': descricao,
                    'preco': preco,
                    'duracao_minutos': duracao,
                    'ativo': True
                }
            )

            if created:
                servicos_criados += 1
                status = "[NOVO]"
            else:
                servicos_atualizados += 1
                status = "[ATU]"

            print(f"{status} {nome[:50]:50} | R$ {preco:6} | {duracao:3}min")

        print(f"\n[RESUMO SERVICOS]")
        print(f"  Criados: {servicos_criados}")
        print(f"  Atualizados: {servicos_atualizados}\n")

    except Exception as e:
        print(f"[ERRO] Ao importar serviços: {e}")
        import traceback
        traceback.print_exc()
        return False

    # ============================================
    # CRIAR PROFISSIONAIS
    # ============================================
    print("="*60)
    print("[CRIANDO PROFISSIONAIS]")
    print("="*60)

    profissionais_data = [
        {
            'nome': 'Pedro Brandão',
            'email': 'pedro@brandaobarbearia.com',
            'telefone': '87999998888',
            'cor_hex': '#1e3a8a',  # Azul escuro
            'comissao_percentual': Decimal('40.00')
        },
        {
            'nome': 'Juan Alves',
            'email': 'juan@brandaobarbearia.com',
            'telefone': '87999997777',
            'cor_hex': '#3b82f6',  # Azul médio
            'comissao_percentual': Decimal('40.00')
        }
    ]

    profissionais_criados = 0
    profissionais_atualizados = 0

    # Pegar todos os serviços para associar
    todos_servicos = list(Servico.objects.filter(empresa=empresa, ativo=True))

    for prof_data in profissionais_data:
        profissional, created = Profissional.objects.update_or_create(
            empresa=empresa,
            email=prof_data['email'],
            defaults={
                'nome': prof_data['nome'],
                'telefone': prof_data['telefone'],
                'cor_hex': prof_data['cor_hex'],
                'comissao_percentual': prof_data['comissao_percentual'],
                'ativo': True
            }
        )

        # Associar todos os serviços ao profissional
        profissional.servicos.set(todos_servicos)

        if created:
            profissionais_criados += 1
            status = "[NOVO]"
        else:
            profissionais_atualizados += 1
            status = "[ATU]"

        print(f"{status} {prof_data['nome']:20} | {prof_data['email']:35} | {len(todos_servicos)} serviços")

    print(f"\n[RESUMO PROFISSIONAIS]")
    print(f"  Criados: {profissionais_criados}")
    print(f"  Atualizados: {profissionais_atualizados}\n")

    # ============================================
    # RESUMO FINAL
    # ============================================
    print("="*60)
    print("[IMPORTACAO CONCLUIDA]")
    print("="*60)
    print(f"\nTotal no banco:")
    print(f"  Servicos: {Servico.objects.filter(empresa=empresa).count()}")
    print(f"  Profissionais: {Profissional.objects.filter(empresa=empresa).count()}")
    print(f"  Horarios: {empresa.horarios_funcionamento.count()}")
    print(f"  Datas Especiais: {empresa.datas_especiais.count()}")
    print("\n[PROXIMOS PASSOS]")
    print("  1. Testar API de servicos: http://127.0.0.1:8000/api/n8n/servicos/")
    print("  2. Testar API de profissionais: http://127.0.0.1:8000/api/n8n/profissionais/")
    print("  3. Adaptar workflows n8n\n")

    return True


if __name__ == '__main__':
    try:
        importar_servicos_e_profissionais()
    except Exception as e:
        print(f"\n[ERRO FATAL] {e}")
        import traceback
        traceback.print_exc()
