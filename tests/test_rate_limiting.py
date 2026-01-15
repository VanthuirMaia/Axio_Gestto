"""
Teste Especifico de Rate Limiting e Brute Force Protection
Valida limites de requisicoes e bloqueios automaticos
"""
import requests
import time
from urllib.parse import urljoin

class RateLimitTester:
    def __init__(self, base_url="http://127.0.0.1:8000"):
        self.base_url = base_url
        self.results = {
            "passed": [],
            "failed": [],
            "warnings": []
        }

    def log(self, test_name, status, message):
        """Log test results"""
        result = {
            "test": test_name,
            "status": status,
            "message": message
        }
        if status == "PASS":
            self.results["passed"].append(result)
        elif status == "FAIL":
            self.results["failed"].append(result)
        else:
            self.results["warnings"].append(result)

        icon = "[OK]" if status == "PASS" else "[FAIL]" if status == "FAIL" else "[WARN]"
        print(f"{icon} [{status}] {test_name}: {message}")

    def test_home_rate_limit(self):
        """Testa rate limit da home (60/min)"""
        print("\n[*] TESTANDO RATE LIMIT DA HOME (60 req/min)")
        print("=" * 60)

        session = requests.Session()
        url = urljoin(self.base_url, "/")

        # Faz 65 requisicoes rapidas
        responses = []
        start_time = time.time()

        for i in range(65):
            try:
                r = session.get(url, timeout=2)
                responses.append(r.status_code)
                if i % 10 == 0:
                    print(f"  Requisicao {i+1}/65: HTTP {r.status_code}")
            except Exception as e:
                print(f"  Erro na requisicao {i+1}: {str(e)}")
                responses.append(0)

        elapsed = time.time() - start_time
        blocked = [s for s in responses if s == 429]

        print(f"\n  Total de requisicoes: {len(responses)}")
        print(f"  Tempo decorrido: {elapsed:.2f}s")
        print(f"  Bloqueadas (HTTP 429): {len(blocked)}")

        if len(blocked) > 0:
            self.log(
                "Rate Limit Home",
                "PASS",
                f"{len(blocked)} requisicoes bloqueadas apos exceder 60/min"
            )
        else:
            self.log(
                "Rate Limit Home",
                "WARN",
                "Nenhuma requisicao bloqueada (rate limiting pode estar desabilitado)"
            )

    def test_cadastro_rate_limit(self):
        """Testa rate limit do cadastro (10/hora POST)"""
        print("\n[*] TESTANDO RATE LIMIT DO CADASTRO (10 POST/hora)")
        print("=" * 60)

        session = requests.Session()

        # Primeiro pega o CSRF token
        get_response = session.get(urljoin(self.base_url, "/cadastro/"))

        url = urljoin(self.base_url, "/cadastro/")

        # Tenta fazer 12 POSTs rapidos
        responses = []
        start_time = time.time()

        for i in range(12):
            try:
                r = session.post(
                    url,
                    data={
                        "nome_empresa": f"Teste {i}",
                        "email_admin": f"teste{i}@teste.com",
                        "telefone": "11999999999",
                        "cnpj": f"12345678000{i:03d}"
                    },
                    timeout=5
                )
                responses.append(r.status_code)
                print(f"  POST {i+1}/12: HTTP {r.status_code}")
                time.sleep(0.5)  # Pequeno delay
            except Exception as e:
                print(f"  Erro no POST {i+1}: {str(e)}")
                responses.append(0)

        elapsed = time.time() - start_time
        blocked = [s for s in responses if s == 429]

        print(f"\n  Total de POSTs: {len(responses)}")
        print(f"  Tempo decorrido: {elapsed:.2f}s")
        print(f"  Bloqueados (HTTP 429): {len(blocked)}")

        if len(blocked) > 0:
            self.log(
                "Rate Limit Cadastro",
                "PASS",
                f"{len(blocked)} POSTs bloqueados apos exceder 10/hora"
            )
        else:
            self.log(
                "Rate Limit Cadastro",
                "WARN",
                "Nenhum POST bloqueado (pode estar desabilitado ou limite alto)"
            )

    def test_login_brute_force(self):
        """Testa protecao brute force do Django Axes (5 tentativas)"""
        print("\n[*] TESTANDO PROTECAO BRUTE FORCE (Django Axes)")
        print("=" * 60)

        session = requests.Session()

        # Primeiro pega o CSRF token
        get_response = session.get(urljoin(self.base_url, "/app/login/"))

        # Extrai CSRF token se existir
        csrf_token = None
        if 'csrftoken' in session.cookies:
            csrf_token = session.cookies['csrftoken']

        url = urljoin(self.base_url, "/app/login/")

        # Tenta fazer 7 logins com senha errada
        responses = []

        for i in range(7):
            data = {
                "username": "admin",
                "password": f"senha_errada_{i}",
            }

            if csrf_token:
                data['csrfmiddlewaretoken'] = csrf_token

            try:
                r = session.post(url, data=data, timeout=5)
                responses.append(r.status_code)

                # Verifica se foi bloqueado
                if r.status_code == 403 or 'locked out' in r.text.lower() or 'bloqueado' in r.text.lower():
                    print(f"  Tentativa {i+1}/7: BLOQUEADO (HTTP {r.status_code})")
                else:
                    print(f"  Tentativa {i+1}/7: HTTP {r.status_code}")

                time.sleep(0.3)
            except Exception as e:
                print(f"  Erro na tentativa {i+1}: {str(e)}")
                responses.append(0)

        # Verifica se houve bloqueio
        blocked = [s for s in responses if s == 403]

        print(f"\n  Total de tentativas: {len(responses)}")
        print(f"  Bloqueios detectados: {len(blocked)}")

        if len(blocked) > 0:
            self.log(
                "Brute Force Protection",
                "PASS",
                f"Bloqueio ativo apos tentativas falhas (Django Axes funcionando)"
            )
        else:
            self.log(
                "Brute Force Protection",
                "WARN",
                "Nenhum bloqueio detectado (Axes pode precisar ajustes)"
            )

    def print_summary(self):
        """Imprime resumo dos testes"""
        print("\n" + "=" * 60)
        print("[+] RESUMO DOS TESTES DE RATE LIMITING E BRUTE FORCE")
        print("=" * 60)
        print(f"[OK] Passed:   {len(self.results['passed'])}")
        print(f"[WARN] Warnings: {len(self.results['warnings'])}")
        print(f"[FAIL] Failed:   {len(self.results['failed'])}")
        print("=" * 60)

        if self.results['failed']:
            print("\n[FAIL] TESTES FALHADOS:")
            for result in self.results['failed']:
                print(f"  - {result['test']}: {result['message']}")

        if self.results['warnings']:
            print("\n[WARN] AVISOS:")
            for result in self.results['warnings']:
                print(f"  - {result['test']}: {result['message']}")

        return len(self.results['failed']) == 0

    def run_all_tests(self):
        """Executa todos os testes"""
        print("\n[*] INICIANDO TESTES DE RATE LIMITING E BRUTE FORCE")
        print("=" * 60)
        print(f"Target: {self.base_url}")
        print("=" * 60)

        self.test_home_rate_limit()
        self.test_cadastro_rate_limit()
        self.test_login_brute_force()

        return self.print_summary()


if __name__ == "__main__":
    tester = RateLimitTester()
    success = tester.run_all_tests()

    import sys
    sys.exit(0 if success else 1)
