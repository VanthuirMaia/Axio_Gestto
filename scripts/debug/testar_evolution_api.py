"""
Script para testar conexão com Evolution API
"""
import os
import sys
import django
import requests

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.conf import settings

def testar_conexao():
    """Testa conexão básica com Evolution API"""

    print("=" * 60)
    print("[TESTE] CONEXAO COM EVOLUTION API")
    print("=" * 60)

    # Verificar variáveis de ambiente
    url = getattr(settings, 'EVOLUTION_API_URL', None)
    api_key = getattr(settings, 'EVOLUTION_API_KEY', None)

    print(f"\n[URL] {url}")
    print(f"[API Key] {api_key[:20]}..." if api_key else "[API Key] NAO CONFIGURADA")

    if not url or not api_key:
        print("\n[ERRO] ERRO: EVOLUTION_API_URL ou EVOLUTION_API_KEY não configurados no .env")
        return False

    # Testar endpoint de listagem de instâncias
    print("\n" + "=" * 60)
    print("[INFO] Testando endpoint: GET /instance/fetchInstances")
    print("=" * 60)

    endpoint = f"{url}/instance/fetchInstances"
    headers = {
        'apikey': api_key,
        'Content-Type': 'application/json'
    }

    try:
        response = requests.get(
            endpoint,
            headers=headers,
            timeout=10
        )

        print(f"\n[STATUS] Status Code: {response.status_code}")

        if response.status_code == 200:
            data = response.json()

            print("[OK] CONEXÃO ESTABELECIDA COM SUCESSO!")
            print(f"\n[WHATSAPP] Instâncias encontradas: {len(data)}")

            if len(data) > 0:
                print("\n[INFO] Instâncias ativas:")
                for instance in data[:5]:  # Mostrar apenas 5 primeiras
                    instance_name = instance.get('instance', {}).get('instanceName', 'N/A')
                    state = instance.get('instance', {}).get('state', 'N/A')
                    print(f"  - {instance_name} ({state})")

                if len(data) > 5:
                    print(f"  ... e mais {len(data) - 5} instâncias")
            else:
                print("\n[INFO] Nenhuma instância criada ainda (isso é normal)")

            return True

        elif response.status_code == 401:
            print("[ERRO] ERRO DE AUTENTICAÇÃO")
            print("   A API Key está incorreta ou expirada")
            print(f"   API Key testada: {api_key[:20]}...")
            return False

        elif response.status_code == 404:
            print("[ERRO] ENDPOINT NÃO ENCONTRADO")
            print("   Verifique se a URL está correta")
            print(f"   URL testada: {url}")
            return False

        else:
            print(f"[ERRO] ERRO INESPERADO: {response.status_code}")
            print(f"   Resposta: {response.text[:200]}")
            return False

    except requests.exceptions.ConnectionError:
        print("[ERRO] ERRO DE CONEXÃO")
        print("   Não foi possível conectar ao servidor Evolution")
        print("   Verifique se:")
        print("   1. A URL está correta")
        print("   2. O servidor Evolution está rodando")
        print("   3. Não há firewall bloqueando")
        return False

    except requests.exceptions.Timeout:
        print("[ERRO] TIMEOUT")
        print("   O servidor não respondeu em 10 segundos")
        return False

    except Exception as e:
        print(f"[ERRO] ERRO INESPERADO: {str(e)}")
        return False


def testar_criacao_instancia_teste():
    """Testa criação de uma instância de teste"""

    print("\n" + "=" * 60)
    print("[TESTE] TESTE DE CRIAÇÃO DE INSTÂNCIA")
    print("=" * 60)

    url = getattr(settings, 'EVOLUTION_API_URL', None)
    api_key = getattr(settings, 'EVOLUTION_API_KEY', None)

    endpoint = f"{url}/instance/create"
    headers = {
        'apikey': api_key,
        'Content-Type': 'application/json'
    }

    # Dados de teste
    data = {
        "instanceName": "teste_conexao_gestto",
        "token": "token_teste_123",
        "qrcode": True,
        "integration": "WHATSAPP-BAILEYS"
    }

    print(f"\n[ENVIANDO] Criando instância de teste: {data['instanceName']}")

    try:
        response = requests.post(
            endpoint,
            headers=headers,
            json=data,
            timeout=15
        )

        print(f"[STATUS] Status Code: {response.status_code}")

        if response.status_code in [200, 201]:
            result = response.json()
            print("[OK] INSTÂNCIA DE TESTE CRIADA COM SUCESSO!")
            print(f"\n[INFO] Dados da instância:")
            print(f"  - Nome: {result.get('instance', {}).get('instanceName', 'N/A')}")
            print(f"  - Status: {result.get('instance', {}).get('status', 'N/A')}")

            # Deletar instância de teste
            print("\n[DELETANDO] Deletando instância de teste...")
            delete_endpoint = f"{url}/instance/delete/teste_conexao_gestto"
            delete_response = requests.delete(delete_endpoint, headers=headers, timeout=10)

            if delete_response.status_code == 200:
                print("[OK] Instância de teste deletada")

            return True
        else:
            print(f"[ERRO] ERRO: {response.status_code}")
            print(f"   Resposta: {response.text[:300]}")
            return False

    except Exception as e:
        print(f"[ERRO] ERRO: {str(e)}")
        return False


if __name__ == '__main__':
    print("\n")

    # Teste 1: Conexão básica
    conexao_ok = testar_conexao()

    if not conexao_ok:
        print("\n" + "=" * 60)
        print("[PARAR] TESTE FALHOU - Corrija os erros acima antes de continuar")
        print("=" * 60)
        sys.exit(1)

    # Teste 2: Criação de instância (opcional)
    print("\n")
    resposta = input("Deseja testar criação de instância? (s/N): ")

    if resposta.lower() == 's':
        testar_criacao_instancia_teste()

    print("\n" + "=" * 60)
    print("[OK] TODOS OS TESTES CONCLUÍDOS")
    print("=" * 60)
    print("\n[DICA] Próximo passo: Implementar Views e Templates")
    print("   Agora você pode conectar WhatsApp pelo sistema Gestto!\n")
