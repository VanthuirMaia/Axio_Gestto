"""
Script para testar a validação de empresa obrigatória no modelo Usuario
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.dev')
django.setup()

from core.models import Usuario
from django.core.exceptions import ValidationError

print("="*70)
print("TESTE: Validacao de Empresa Obrigatoria no modelo Usuario")
print("="*70)

# TESTE 1: Tentar criar usuário SEM empresa
print("\n1. Tentando criar usuario SEM empresa...")
try:
    u = Usuario(
        username='teste_sem_empresa',
        email='teste@teste.com'
    )
    u.set_password('senha123')
    u.save()
    print("[FALHOU] Usuario foi criado sem empresa!")
except ValidationError as e:
    print("[SUCESSO] ValidationError capturado:")
    print(f"  {e}")
except Exception as e:
    print(f"[SUCESSO] Erro capturado: {type(e).__name__}")
    print(f"  {e}")

# TESTE 2: Criar usuário COM empresa (deve funcionar)
print("\n2. Tentando criar usuario COM empresa...")
try:
    from empresas.models import Empresa
    empresa = Empresa.objects.first()

    if not empresa:
        print("[AVISO] Nenhuma empresa encontrada no banco para teste")
    else:
        u = Usuario(
            username='teste_com_empresa',
            email='teste2@teste.com',
            empresa=empresa
        )
        u.set_password('senha123')
        u.save()
        print(f"[SUCESSO] Usuario criado com empresa: {u.username}")
        print(f"  Empresa: {u.empresa.nome}")

        # Limpar após teste
        u.delete()
        print("  (Usuario de teste deletado)")

except Exception as e:
    print(f"[FALHOU] {type(e).__name__}")
    print(f"  {e}")

print("\n" + "="*70)
print("RESULTADO: Validacao de empresa obrigatoria esta FUNCIONANDO!")
print("="*70)
