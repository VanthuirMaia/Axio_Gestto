import os
import django
import sys

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.base')
django.setup()

from core.models import Usuario
from empresas.models import Empresa, Profissional
from assinaturas.models import Assinatura
from django.conf import settings

def check_profissionais_view_logic():
    print("--- Diagnosticando Erro 500 em Profissionais ---")
    
    # 1. Pegar a última empresa criada (provavelmente a do usuário)
    empresa = Empresa.objects.last()
    if not empresa:
        print("ERRO: Nenhuma empresa encontrada.")
        return

    print(f"Empresa: {empresa.nome} (ID: {empresa.id})")
    
    # 2. Simular a lógica da view profissionais_lista
    try:
        profissionais = Profissional.objects.filter(empresa=empresa).order_by('nome')
        count = profissionais.count()
        print(f"Total Profissionais: {count}")
        
        # Iterar para ver se algum quebra
        for p in profissionais:
            print(f" - {p.nome} (Ativo: {p.ativo}) - ID: {p.id}")

        # 3. Lógica de Assinatura
        assinatura = getattr(empresa, 'assinatura', None)
        print(f"Assinatura: {assinatura}")
        
        if assinatura:
            print(f"Plano: {assinatura.plano}")
            if assinatura.plano:
                print(f"Max Pro: {assinatura.plano.max_profissionais}")
                
            # Testar acesso a campos usados no template
            print(f"Display Plano: {assinatura.plano.get_nome_display()}")
        
        # 4. Lógica de Limite
        max_profissionais = 1
        if assinatura and assinatura.plano:
            max_profissionais = assinatura.plano.max_profissionais
            profissionais_ativos = profissionais.filter(ativo=True).count()
            pode_criar = profissionais_ativos < max_profissionais
            print(f"Ativos: {profissionais_ativos}, Max: {max_profissionais}, Pode Criar: {pode_criar}")
        else:
            print("Sem plano/assinatura lógica fallback")

        print("--- Lógica da View OK (sem erros de exceção) ---")

    except Exception as e:
        print("\n!!! ERRO ENCONTRADO NA LÓGICA !!!")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    check_profissionais_view_logic()
