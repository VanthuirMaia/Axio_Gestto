#!/usr/bin/env python
"""
Script de Testes - Integração Gestto + n8n

Testa a integração completa:
- APIs Django (n8n endpoints)
- Webhook intermediário
- n8n workflow

Uso:
    python scripts/testar_integracao_n8n.py
"""

import os
import sys
import json
import requests
from datetime import datetime
from colorama import init, Fore, Style

# Inicializar colorama para Windows
init(autoreset=True)

# Adicionar o diretório raiz ao path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
import django
django.setup()

from django.conf import settings
from empresas.models import Empresa, ConfiguracaoWhatsApp


class TestadorIntegracaoN8N:
    """Classe para testar integração Gestto + n8n"""

    def __init__(self):
        self.base_url = settings.SITE_URL
        self.n8n_webhook_url = settings.N8N_WEBHOOK_URL
        self.n8n_api_key = settings.N8N_API_KEY
        self.empresa_id = None
        self.webhook_secret = None
        self.resultados = []

    def print_header(self, titulo):
        """Imprime cabeçalho de seção"""
        print(f"\n{Fore.CYAN}{'='*60}")
        print(f"{Fore.CYAN}{titulo}")
        print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}")

    def print_success(self, mensagem):
        """Imprime mensagem de sucesso"""
        print(f"{Fore.GREEN}✅ {mensagem}{Style.RESET_ALL}")
        self.resultados.append(("✅", mensagem))

    def print_error(self, mensagem):
        """Imprime mensagem de erro"""
        print(f"{Fore.RED}❌ {mensagem}{Style.RESET_ALL}")
        self.resultados.append(("❌", mensagem))

    def print_info(self, mensagem):
        """Imprime mensagem informativa"""
        print(f"{Fore.YELLOW}ℹ️  {mensagem}{Style.RESET_ALL}")

    def testar_configuracao_django(self):
        """Testa se configurações do Django estão corretas"""
        self.print_header("TESTE 1: Configuração Django")

        # Verificar N8N_WEBHOOK_URL
        if self.n8n_webhook_url:
            self.print_success(f"N8N_WEBHOOK_URL configurado: {self.n8n_webhook_url}")
        else:
            self.print_error("N8N_WEBHOOK_URL não configurado!")
            return False

        # Verificar N8N_API_KEY
        if self.n8n_api_key:
            self.print_success(f"N8N_API_KEY configurado: {self.n8n_api_key[:10]}...")
        else:
            self.print_error("N8N_API_KEY não configurado!")
            return False

        # Verificar EVOLUTION_API_URL
        if settings.EVOLUTION_API_URL:
            self.print_success(f"EVOLUTION_API_URL: {settings.EVOLUTION_API_URL}")
        else:
            self.print_error("EVOLUTION_API_URL não configurado!")
            return False

        return True

    def selecionar_empresa(self):
        """Seleciona empresa para testes"""
        self.print_header("TESTE 2: Seleção de Empresa")

        empresas = Empresa.objects.all()

        if not empresas.exists():
            self.print_error("Nenhuma empresa cadastrada!")
            return False

        print(f"\n{Fore.YELLOW}Empresas disponíveis:{Style.RESET_ALL}")
        for empresa in empresas:
            status_assinatura = "✅ Ativa" if empresa.assinatura_ativa else "❌ Inativa"
            print(f"  [{empresa.id}] {empresa.nome} - Assinatura: {status_assinatura}")

        # Usar primeira empresa com assinatura ativa
        empresa = empresas.filter(assinatura_ativa=True).first()

        if not empresa:
            self.print_error("Nenhuma empresa com assinatura ativa!")
            return False

        self.empresa_id = empresa.id
        self.print_success(f"Empresa selecionada: {empresa.nome} (ID: {empresa.id})")

        # Buscar configuração WhatsApp
        try:
            config = ConfiguracaoWhatsApp.objects.get(empresa=empresa)
            self.webhook_secret = config.webhook_secret
            self.print_info(f"Instância: {config.instance_name or 'Não criada'}")
            self.print_info(f"Status: {config.status}")
        except ConfiguracaoWhatsApp.DoesNotExist:
            self.print_info("Configuração WhatsApp não encontrada (use interface para criar)")
            self.webhook_secret = "teste-secret-123"

        return True

    def testar_api_profissionais(self):
        """Testa API de listagem de profissionais"""
        self.print_header("TESTE 3: API - Listar Profissionais")

        url = f"{self.base_url}/api/n8n/profissionais/"
        headers = {
            'apikey': self.n8n_api_key,
            'empresa_id': str(self.empresa_id)
        }
        params = {'empresa_id': self.empresa_id}

        try:
            response = requests.get(url, headers=headers, params=params, timeout=10)

            if response.status_code == 200:
                data = response.json()
                total = data.get('total', 0)
                self.print_success(f"API respondeu OK - {total} profissionais encontrados")

                if total > 0:
                    for prof in data['profissionais'][:3]:
                        print(f"    - {prof['nome']} (ID: {prof['id']})")
                return True
            else:
                self.print_error(f"Erro {response.status_code}: {response.text[:100]}")
                return False

        except requests.exceptions.RequestException as e:
            self.print_error(f"Erro de conexão: {str(e)}")
            return False

    def testar_api_servicos(self):
        """Testa API de listagem de serviços"""
        self.print_header("TESTE 4: API - Listar Serviços")

        url = f"{self.base_url}/api/n8n/servicos/"
        headers = {
            'apikey': self.n8n_api_key,
            'empresa_id': str(self.empresa_id)
        }
        params = {'empresa_id': self.empresa_id}

        try:
            response = requests.get(url, headers=headers, params=params, timeout=10)

            if response.status_code == 200:
                data = response.json()
                total = data.get('total', 0)
                self.print_success(f"API respondeu OK - {total} serviços encontrados")

                if total > 0:
                    for servico in data['servicos'][:3]:
                        print(f"    - {servico['nome']}: R$ {servico['preco']} ({servico['duracao_minutos']}min)")
                return True
            else:
                self.print_error(f"Erro {response.status_code}: {response.text[:100]}")
                return False

        except requests.exceptions.RequestException as e:
            self.print_error(f"Erro de conexão: {str(e)}")
            return False

    def testar_api_horarios(self):
        """Testa API de horários de funcionamento"""
        self.print_header("TESTE 5: API - Horários de Funcionamento")

        url = f"{self.base_url}/api/n8n/horarios-funcionamento/"
        headers = {
            'apikey': self.n8n_api_key,
            'empresa_id': str(self.empresa_id)
        }
        params = {'empresa_id': self.empresa_id}

        try:
            response = requests.get(url, headers=headers, params=params, timeout=10)

            if response.status_code == 200:
                data = response.json()
                total = data.get('total', 0)
                self.print_success(f"API respondeu OK - {total} horários configurados")

                if total > 0:
                    for horario in data['horarios'][:3]:
                        if horario['ativo']:
                            print(f"    - {horario['dia_semana_nome']}: {horario['hora_abertura']} às {horario['hora_fechamento']}")
                return True
            else:
                self.print_error(f"Erro {response.status_code}: {response.text[:100]}")
                return False

        except requests.exceptions.RequestException as e:
            self.print_error(f"Erro de conexão: {str(e)}")
            return False

    def testar_webhook_intermediario(self):
        """Testa webhook intermediário Django"""
        self.print_header("TESTE 6: Webhook Intermediário (Django)")

        if not self.webhook_secret:
            self.print_error("Webhook secret não disponível. Crie uma instância WhatsApp primeiro.")
            return False

        url = f"{self.base_url}/api/webhooks/whatsapp-n8n/{self.empresa_id}/{self.webhook_secret}/"

        payload = {
            "instance": "teste_integracao_script",
            "data": {
                "key": {
                    "remoteJid": "5511999999999@s.whatsapp.net",
                    "fromMe": False
                },
                "pushName": "Teste Script",
                "message": {
                    "conversation": "Teste de integração automático"
                },
                "messageTimestamp": str(int(datetime.now().timestamp()))
            }
        }

        self.print_info(f"Enviando para: {url}")

        try:
            response = requests.post(url, json=payload, timeout=15)

            if response.status_code == 200:
                data = response.json()
                if data.get('success') and data.get('forwarded_to_n8n'):
                    self.print_success(f"Webhook intermediário OK - Encaminhado para n8n")
                    self.print_info(f"Empresa: {data.get('empresa')}")
                    return True
                else:
                    self.print_error(f"Webhook não encaminhou para n8n: {data}")
                    return False
            elif response.status_code == 402:
                self.print_error("Assinatura inativa! Ative a assinatura da empresa.")
                return False
            elif response.status_code == 403:
                self.print_error("Secret inválido! Verifique o webhook_secret da empresa.")
                return False
            else:
                self.print_error(f"Erro {response.status_code}: {response.text[:200]}")
                return False

        except requests.exceptions.Timeout:
            self.print_error("Timeout ao encaminhar para n8n. Verifique se n8n está rodando.")
            return False
        except requests.exceptions.RequestException as e:
            self.print_error(f"Erro de conexão: {str(e)}")
            return False

    def testar_n8n_direto(self):
        """Testa webhook n8n diretamente"""
        self.print_header("TESTE 7: Webhook n8n (Direto)")

        if not self.n8n_webhook_url:
            self.print_error("N8N_WEBHOOK_URL não configurado!")
            return False

        payload = {
            "empresa_id": self.empresa_id,
            "empresa_nome": "Teste Script",
            "instance": "teste_integracao_script",
            "body": {
                "data": {
                    "key": {
                        "remoteJid": "5511999999999@s.whatsapp.net"
                    },
                    "pushName": "Teste Script",
                    "message": {
                        "conversation": "Oi, teste de integração"
                    }
                }
            }
        }

        self.print_info(f"Enviando para: {self.n8n_webhook_url}")

        try:
            response = requests.post(self.n8n_webhook_url, json=payload, timeout=15)

            if response.status_code == 200:
                self.print_success("n8n recebeu e processou o webhook!")
                self.print_info("Verifique execuções no n8n: Executions → Última execução")
                return True
            else:
                self.print_error(f"Erro {response.status_code}: {response.text[:200]}")
                return False

        except requests.exceptions.Timeout:
            self.print_error("Timeout - n8n demorou muito para responder")
            return False
        except requests.exceptions.RequestException as e:
            self.print_error(f"Erro de conexão: {str(e)}")
            self.print_info("Verifique se n8n está rodando e workflow está ativado")
            return False

    def exibir_resumo(self):
        """Exibe resumo dos testes"""
        self.print_header("RESUMO DOS TESTES")

        total = len(self.resultados)
        sucessos = len([r for r in self.resultados if r[0] == "✅"])
        falhas = len([r for r in self.resultados if r[0] == "❌"])

        print(f"\n{Fore.CYAN}Total de testes: {total}")
        print(f"{Fore.GREEN}Sucessos: {sucessos}")
        print(f"{Fore.RED}Falhas: {falhas}")

        if falhas == 0:
            print(f"\n{Fore.GREEN}{'='*60}")
            print(f"{Fore.GREEN}🎉 TODOS OS TESTES PASSARAM!")
            print(f"{Fore.GREEN}{'='*60}{Style.RESET_ALL}")
            print(f"\n{Fore.YELLOW}Próximos passos:")
            print(f"  1. Teste manualmente enviando mensagem no WhatsApp")
            print(f"  2. Verifique execuções no n8n")
            print(f"  3. Confira se agendamento foi criado no Gestto")
        else:
            print(f"\n{Fore.RED}{'='*60}")
            print(f"{Fore.RED}⚠️  ALGUNS TESTES FALHARAM")
            print(f"{Fore.RED}{'='*60}{Style.RESET_ALL}")
            print(f"\n{Fore.YELLOW}Revise os erros acima e:")
            print(f"  1. Verifique configurações do .env")
            print(f"  2. Certifique-se que n8n está rodando")
            print(f"  3. Valide que workflow n8n está ativado")
            print(f"  4. Consulte docs/TESTE_INTEGRACAO_N8N.md")

    def executar_todos(self):
        """Executa todos os testes"""
        print(f"\n{Fore.MAGENTA}{'='*60}")
        print(f"{Fore.MAGENTA}🧪 TESTADOR DE INTEGRAÇÃO GESTTO + N8N")
        print(f"{Fore.MAGENTA}{'='*60}{Style.RESET_ALL}")

        # Executar testes em sequência
        if not self.testar_configuracao_django():
            self.print_error("Configuração Django falhou. Abortando testes.")
            return

        if not self.selecionar_empresa():
            self.print_error("Seleção de empresa falhou. Abortando testes.")
            return

        # Testes de API (continuam mesmo se um falhar)
        self.testar_api_profissionais()
        self.testar_api_servicos()
        self.testar_api_horarios()

        # Testes de webhook
        self.testar_webhook_intermediario()
        self.testar_n8n_direto()

        # Resumo
        self.exibir_resumo()


def main():
    """Função principal"""
    testador = TestadorIntegracaoN8N()
    testador.executar_todos()


if __name__ == '__main__':
    main()
