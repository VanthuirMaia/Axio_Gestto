"""
Script para importar dados das planilhas Excel para o Django

Uso:
    python manage.py shell < scripts/importar_planilhas.py

Ou:
    python scripts/importar_planilhas.py (se configurar DJANGO_SETTINGS_MODULE)
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
from datetime import time, datetime
from empresas.models import Empresa, Servico, Profissional, HorarioFuncionamento, DataEspecial


def importar_planilha_principal():
    """
    Importa dados da planilha principal "Serviços Barbearia.xlsx"
    que contém 3 abas: Serviços, horarios, datas_especiais
    """

    # Buscar a empresa (primeira ativa)
    empresa = Empresa.objects.filter(ativa=True).first()
    if not empresa:
        print("[ERRO] Nenhuma empresa ativa encontrada. Crie uma empresa no admin primeiro!")
        return False

    print(f"\n[OK] Empresa encontrada: {empresa.nome}")

    # Caminho da planilha
    planilha_path = BASE_DIR / 'data' / 'Serviços Barbearia.xlsx'

    if not planilha_path.exists():
        print(f"[ERRO] ERRO: Arquivo não encontrado: {planilha_path}")
        return False

    print(f"\n📂 Lendo planilha: {planilha_path}")

    # ============================================
    # ABA 1: SERVIÇOS
    # ============================================
    print("\n" + "="*60)
    print("📋 IMPORTANDO SERVIÇOS")
    print("="*60)

    try:
        df_servicos = pd.read_excel(planilha_path, sheet_name='Serviços')
        print(f"[OK] Aba 'Serviços' encontrada: {len(df_servicos)} linhas")
        print(f"   Colunas: {list(df_servicos.columns)}")

        servicos_criados = 0
        servicos_atualizados = 0

        for idx, row in df_servicos.iterrows():
            # Pular linhas vazias
            if pd.isna(row.get('Serviço')) or pd.isna(row.get('Duração')):
                continue

            nome = str(row['Serviço']).strip()
            duracao = int(row['Duração'])  # em minutos
            preco = float(row.get('Preço', 0)) if not pd.isna(row.get('Preço')) else 0
            descricao = str(row.get('Descrição', '')).strip() if not pd.isna(row.get('Descrição')) else ''

            # Criar ou atualizar serviço
            servico, created = Servico.objects.update_or_create(
                empresa=empresa,
                nome=nome,
                defaults={
                    'duracao_minutos': duracao,
                    'preco': preco,
                    'descricao': descricao,
                    'ativo': True
                }
            )

            if created:
                servicos_criados += 1
                print(f"   [OK] Criado: {nome} ({duracao}min, R$ {preco})")
            else:
                servicos_atualizados += 1
                print(f"   🔄 Atualizado: {nome} ({duracao}min, R$ {preco})")

        print(f"\n📊 Resumo Serviços:")
        print(f"   • Criados: {servicos_criados}")
        print(f"   • Atualizados: {servicos_atualizados}")

    except Exception as e:
        print(f"[ERRO] Erro ao importar serviços: {e}")
        import traceback
        traceback.print_exc()

    # ============================================
    # ABA 2: HORÁRIOS DE FUNCIONAMENTO
    # ============================================
    print("\n" + "="*60)
    print("🕐 IMPORTANDO HORÁRIOS DE FUNCIONAMENTO")
    print("="*60)

    try:
        df_horarios = pd.read_excel(planilha_path, sheet_name='horarios')
        print(f"[OK] Aba 'horarios' encontrada: {len(df_horarios)} linhas")
        print(f"   Colunas: {list(df_horarios.columns)}")

        # Mapeamento de dias da semana
        dias_map = {
            'Segunda': 0,
            'Terça': 1,
            'Quarta': 2,
            'Quinta': 3,
            'Sexta': 4,
            'Sábado': 5,
            'Domingo': 6
        }

        horarios_criados = 0
        horarios_atualizados = 0

        for idx, row in df_horarios.iterrows():
            # Pular linhas vazias
            if pd.isna(row.get('Dia')) or pd.isna(row.get('Abertura')):
                continue

            dia_nome = str(row['Dia']).strip()
            dia_semana = dias_map.get(dia_nome)

            if dia_semana is None:
                print(f"   [WARN] Dia não reconhecido: {dia_nome}")
                continue

            # Processar horários
            abertura_str = str(row['Abertura']).strip()
            fechamento_str = str(row['Fechamento']).strip()

            # Converter para time
            try:
                # Pode vir como "09:00" ou timestamp
                if ':' in abertura_str:
                    hora, minuto = abertura_str.split(':')
                    hora_abertura = time(int(hora), int(minuto))
                else:
                    # Tentar parsear timestamp
                    hora_abertura = pd.to_datetime(row['Abertura']).time()

                if ':' in fechamento_str:
                    hora, minuto = fechamento_str.split(':')
                    hora_fechamento = time(int(hora), int(minuto))
                else:
                    hora_fechamento = pd.to_datetime(row['Fechamento']).time()

            except Exception as e:
                print(f"   [WARN] Erro ao processar horário do dia {dia_nome}: {e}")
                continue

            # Intervalo (se houver)
            intervalo_inicio = None
            intervalo_fim = None

            if not pd.isna(row.get('Intervalo Início')):
                try:
                    intervalo_str = str(row['Intervalo Início']).strip()
                    if ':' in intervalo_str:
                        hora, minuto = intervalo_str.split(':')
                        intervalo_inicio = time(int(hora), int(minuto))
                    else:
                        intervalo_inicio = pd.to_datetime(row['Intervalo Início']).time()
                except:
                    pass

            if not pd.isna(row.get('Intervalo Fim')):
                try:
                    intervalo_str = str(row['Intervalo Fim']).strip()
                    if ':' in intervalo_str:
                        hora, minuto = intervalo_str.split(':')
                        intervalo_fim = time(int(hora), int(minuto))
                    else:
                        intervalo_fim = pd.to_datetime(row['Intervalo Fim']).time()
                except:
                    pass

            # Criar ou atualizar
            horario, created = HorarioFuncionamento.objects.update_or_create(
                empresa=empresa,
                dia_semana=dia_semana,
                defaults={
                    'hora_abertura': hora_abertura,
                    'hora_fechamento': hora_fechamento,
                    'intervalo_inicio': intervalo_inicio,
                    'intervalo_fim': intervalo_fim,
                    'ativo': True
                }
            )

            if created:
                horarios_criados += 1
                print(f"   [OK] Criado: {dia_nome} - {hora_abertura.strftime('%H:%M')} às {hora_fechamento.strftime('%H:%M')}")
            else:
                horarios_atualizados += 1
                print(f"   🔄 Atualizado: {dia_nome} - {hora_abertura.strftime('%H:%M')} às {hora_fechamento.strftime('%H:%M')}")

        print(f"\n📊 Resumo Horários:")
        print(f"   • Criados: {horarios_criados}")
        print(f"   • Atualizados: {horarios_atualizados}")

    except Exception as e:
        print(f"[ERRO] Erro ao importar horários: {e}")
        import traceback
        traceback.print_exc()

    # ============================================
    # ABA 3: DATAS ESPECIAIS
    # ============================================
    print("\n" + "="*60)
    print("📅 IMPORTANDO DATAS ESPECIAIS")
    print("="*60)

    try:
        df_datas = pd.read_excel(planilha_path, sheet_name='datas_especiais')
        print(f"[OK] Aba 'datas_especiais' encontrada: {len(df_datas)} linhas")
        print(f"   Colunas: {list(df_datas.columns)}")

        datas_criadas = 0
        datas_atualizadas = 0

        for idx, row in df_datas.iterrows():
            # Pular linhas vazias
            if pd.isna(row.get('Data')) or pd.isna(row.get('Descrição')):
                continue

            # Processar data
            data_val = row['Data']
            if isinstance(data_val, str):
                # Tentar parsear string
                data = pd.to_datetime(data_val, dayfirst=True).date()
            else:
                # Já é datetime
                data = pd.to_datetime(data_val).date()

            descricao = str(row['Descrição']).strip()

            # Tipo (feriado ou especial)
            tipo_str = str(row.get('Tipo', 'feriado')).strip().lower()
            if tipo_str in ['feriado', 'fechado']:
                tipo = 'feriado'
            else:
                tipo = 'especial'

            # Horários especiais (se tipo = especial)
            hora_abertura = None
            hora_fechamento = None

            if tipo == 'especial' and not pd.isna(row.get('Abertura')):
                try:
                    abertura_str = str(row['Abertura']).strip()
                    if ':' in abertura_str:
                        hora, minuto = abertura_str.split(':')
                        hora_abertura = time(int(hora), int(minuto))
                    else:
                        hora_abertura = pd.to_datetime(row['Abertura']).time()
                except:
                    pass

            if tipo == 'especial' and not pd.isna(row.get('Fechamento')):
                try:
                    fechamento_str = str(row['Fechamento']).strip()
                    if ':' in fechamento_str:
                        hora, minuto = fechamento_str.split(':')
                        hora_fechamento = time(int(hora), int(minuto))
                    else:
                        hora_fechamento = pd.to_datetime(row['Fechamento']).time()
                except:
                    pass

            # Criar ou atualizar
            data_especial, created = DataEspecial.objects.update_or_create(
                empresa=empresa,
                data=data,
                defaults={
                    'descricao': descricao,
                    'tipo': tipo,
                    'hora_abertura': hora_abertura,
                    'hora_fechamento': hora_fechamento
                }
            )

            if created:
                datas_criadas += 1
                if tipo == 'feriado':
                    print(f"   [OK] Criado: {data.strftime('%d/%m/%Y')} - {descricao} (FECHADO)")
                else:
                    print(f"   [OK] Criado: {data.strftime('%d/%m/%Y')} - {descricao} ({hora_abertura.strftime('%H:%M')}-{hora_fechamento.strftime('%H:%M')})")
            else:
                datas_atualizadas += 1
                if tipo == 'feriado':
                    print(f"   🔄 Atualizado: {data.strftime('%d/%m/%Y')} - {descricao} (FECHADO)")
                else:
                    print(f"   🔄 Atualizado: {data.strftime('%d/%m/%Y')} - {descricao}")

        print(f"\n📊 Resumo Datas Especiais:")
        print(f"   • Criadas: {datas_criadas}")
        print(f"   • Atualizadas: {datas_atualizadas}")

    except Exception as e:
        print(f"[ERRO] Erro ao importar datas especiais: {e}")
        import traceback
        traceback.print_exc()

    print("\n" + "="*60)
    print("[OK] IMPORTAÇÃO CONCLUÍDA!")
    print("="*60)
    print("\n💡 Próximos passos:")
    print("   1. Cadastrar profissionais pelo Admin")
    print("   2. Testar as APIs: http://127.0.0.1:8000/api/n8n/servicos/")
    print("   3. Adaptar workflows n8n para usar as APIs\n")

    return True


if __name__ == '__main__':
    try:
        importar_planilha_principal()
    except Exception as e:
        print(f"\n[ERRO] ERRO FATAL: {e}")
        import traceback
        traceback.print_exc()
