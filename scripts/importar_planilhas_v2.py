# -*- coding: utf-8 -*-
"""
Script para importar dados das planilhas Excel da Brandão Barbearia

Estrutura das planilhas:
- Serviços: (vazia - cadastrar manualmente)
- horarios: Dia | Manhã | Fim Manhã | Tarde | Fim
- datas_especiais: Descrição | Data | Manhã | Fim Manhã | Tarde | Fim
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
from empresas.models import Empresa, HorarioFuncionamento, DataEspecial


def importar_dados():
    """Importa horários e datas especiais da planilha"""

    # Buscar empresa
    empresa = Empresa.objects.filter(ativa=True).first()
    if not empresa:
        print("[ERRO] Nenhuma empresa ativa encontrada!")
        return False

    print(f"\n[OK] Empresa: {empresa.nome}\n")

    planilha_path = BASE_DIR / 'data' / 'Serviços Barbearia.xlsx'

    if not planilha_path.exists():
        print(f"[ERRO] Arquivo não encontrado: {planilha_path}")
        return False

    # ============================================
    # HORÁRIOS DE FUNCIONAMENTO
    # ============================================
    print("="*60)
    print("[IMPORTANDO HORÁRIOS DE FUNCIONAMENTO]")
    print("="*60)

    try:
        df = pd.read_excel(planilha_path, sheet_name='horarios')

        # Mapeamento de dias
        dias_map = {
            'Segunda': 0, 'Terça': 1, 'Quarta': 2,
            'Quinta': 3, 'Sexta': 4, 'Sábado': 5, 'Domingo': 6
        }

        criados = 0
        atualizados = 0

        for idx, row in df.iterrows():
            dia_nome = str(row['Dia']).strip()
            dia_semana = dias_map.get(dia_nome)

            if dia_semana is None:
                continue

            # Horários: Manhã até Unnamed:2, depois Unnamed:2 até Tarde/Noite
            # Abertura: primeira coluna (Manhã)
            # Intervalo: Unnamed: 2 até Tarde/Noite
            # Fechamento: última coluna (Unnamed: 4)

            try:
                # Pegar valores - já são time objects do Excel
                val1 = row.iloc[1]  # Manhã
                val2 = row.iloc[2]  # Unnamed: 2
                val3 = row.iloc[3]  # Tarde/Noite
                val4 = row.iloc[4]  # Unnamed: 4

                # Converter para time se necessário
                if isinstance(val1, time):
                    hora_abertura = val1
                else:
                    hora_abertura = pd.to_datetime(val1).time()

                if isinstance(val2, time):
                    intervalo_inicio = val2
                else:
                    intervalo_inicio = pd.to_datetime(val2).time()

                if isinstance(val3, time):
                    intervalo_fim = val3
                else:
                    intervalo_fim = pd.to_datetime(val3).time()

                if isinstance(val4, time):
                    hora_fechamento = val4
                else:
                    hora_fechamento = pd.to_datetime(val4).time()

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
                    criados += 1
                    status = "[NOVO]"
                else:
                    atualizados += 1
                    status = "[ATU]"

                print(f"{status} {dia_nome:10} | {hora_abertura}-{intervalo_inicio} | {intervalo_fim}-{hora_fechamento}")

            except Exception as e:
                print(f"[ERRO] {dia_nome}: {e}")
                continue

        print(f"\n[RESUMO] Criados: {criados} | Atualizados: {atualizados}\n")

    except Exception as e:
        print(f"[ERRO] Ao importar horários: {e}")
        import traceback
        traceback.print_exc()

    # ============================================
    # DATAS ESPECIAIS
    # ============================================
    print("="*60)
    print("[IMPORTANDO DATAS ESPECIAIS]")
    print("="*60)

    try:
        df = pd.read_excel(planilha_path, sheet_name='datas_especiais')

        criados = 0
        atualizados = 0

        for idx, row in df.iterrows():
            if pd.isna(row['Data']):
                continue

            descricao = str(row['Descrição']).strip()
            data = pd.to_datetime(row['Data']).date()

            # Verificar se é feriado (marcado com "--")
            manha_val = str(row.iloc[2]).strip()

            if manha_val == '--' or manha_val == 'nan':
                # Feriado - fechado
                data_esp, created = DataEspecial.objects.update_or_create(
                    empresa=empresa,
                    data=data,
                    defaults={
                        'descricao': descricao,
                        'tipo': 'feriado',
                        'hora_abertura': None,
                        'hora_fechamento': None
                    }
                )

                if created:
                    criados += 1
                    status = "[NOVO]"
                else:
                    atualizados += 1
                    status = "[ATU]"

                print(f"{status} {data.strftime('%d/%m/%Y')} - {descricao:20} | FECHADO")

            else:
                # Horário especial
                try:
                    hora_abertura = pd.to_datetime(row.iloc[2]).time()
                    hora_fechamento = pd.to_datetime(row.iloc[5]).time()

                    data_esp, created = DataEspecial.objects.update_or_create(
                        empresa=empresa,
                        data=data,
                        defaults={
                            'descricao': descricao,
                            'tipo': 'especial',
                            'hora_abertura': hora_abertura,
                            'hora_fechamento': hora_fechamento
                        }
                    )

                    if created:
                        criados += 1
                        status = "[NOVO]"
                    else:
                        atualizados += 1
                        status = "[ATU]"

                    print(f"{status} {data.strftime('%d/%m/%Y')} - {descricao:20} | {hora_abertura}-{hora_fechamento}")

                except Exception as e:
                    print(f"[ERRO] {descricao}: {e}")

        print(f"\n[RESUMO] Criadas: {criados} | Atualizadas: {atualizados}\n")

    except Exception as e:
        print(f"[ERRO] Ao importar datas especiais: {e}")
        import traceback
        traceback.print_exc()

    print("="*60)
    print("[CONCLUÍDO]")
    print("="*60)
    print("\n[PRÓXIMOS PASSOS]")
    print("1. Cadastrar SERVIÇOS manualmente no Admin")
    print("2. Cadastrar PROFISSIONAIS no Admin")
    print("3. Testar API: http://127.0.0.1:8000/api/n8n/horarios-funcionamento/\n")

    return True


if __name__ == '__main__':
    try:
        importar_dados()
    except Exception as e:
        print(f"\n[ERRO FATAL] {e}")
        import traceback
        traceback.print_exc()
