"""
Testes de Segurança Abrangentes
Testa vulnerabilidades comuns: SQL Injection, XSS, CSRF, Headers HTTP, Rate Limiting
"""
import requests
import time
from urllib.parse import urljoin

class SecurityTester:
    def __init__(self, base_url="http://127.0.0.1:8000"):
        self.base_url = base_url
        self.session = requests.Session()
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

    def test_sql_injection(self):
        """Testa proteção contra SQL Injection"""
        print("\n[*] TESTANDO SQL INJECTION")
        print("=" * 60)

        payloads = [
            "' OR '1'='1",
            "1' OR '1' = '1",
            "admin'--",
            "1' UNION SELECT NULL--",
            "' OR 1=1--",
        ]

        for payload in payloads:
            try:
                # Testa injeção na URL
                response = self.session.get(
                    urljoin(self.base_url, f"/cadastro/?email={payload}"),
                    timeout=5
                )

                # Verifica se retornou erro HTTP (bom sinal)
                if response.status_code >= 400:
                    self.log(
                        f"SQL Injection (GET): {payload[:20]}...",
                        "PASS",
                        f"Servidor rejeitou payload suspeito (HTTP {response.status_code})"
                    )
                else:
                    # Verifica se não há indicação de SQL no response
                    dangerous_keywords = ['sql', 'syntax error', 'mysql', 'sqlite', 'postgresql']
                    has_sql_error = any(kw in response.text.lower() for kw in dangerous_keywords)

                    if not has_sql_error:
                        self.log(
                            f"SQL Injection (GET): {payload[:20]}...",
                            "PASS",
                            "Nenhum erro SQL exposto na resposta"
                        )
                    else:
                        self.log(
                            f"SQL Injection (GET): {payload[:20]}...",
                            "FAIL",
                            "Possível exposição de erro SQL detectada!"
                        )
            except Exception as e:
                self.log(
                    f"SQL Injection (GET): {payload[:20]}...",
                    "WARN",
                    f"Erro ao testar: {str(e)}"
                )

    def test_xss(self):
        """Testa proteção contra XSS"""
        print("\n[*] TESTANDO XSS (Cross-Site Scripting)")
        print("=" * 60)

        payloads = [
            "<script>alert('XSS')</script>",
            "<img src=x onerror=alert('XSS')>",
            "javascript:alert('XSS')",
            "<svg/onload=alert('XSS')>",
        ]

        for payload in payloads:
            try:
                response = self.session.get(
                    urljoin(self.base_url, f"/cadastro/?nome={payload}"),
                    timeout=5
                )

                # Verifica se o payload foi sanitizado (não aparece cru no HTML)
                if payload in response.text:
                    self.log(
                        f"XSS: {payload[:30]}...",
                        "FAIL",
                        "Payload XSS encontrado sem sanitização!"
                    )
                else:
                    self.log(
                        f"XSS: {payload[:30]}...",
                        "PASS",
                        "Payload foi sanitizado/escapado corretamente"
                    )
            except Exception as e:
                self.log(
                    f"XSS: {payload[:30]}...",
                    "WARN",
                    f"Erro ao testar: {str(e)}"
                )

    def test_csrf_protection(self):
        """Testa proteção CSRF"""
        print("\n[*] TESTANDO CSRF PROTECTION")
        print("=" * 60)

        try:
            # Tenta POST sem CSRF token
            response = self.session.post(
                urljoin(self.base_url, "/cadastro/"),
                data={"nome_empresa": "Test", "email_admin": "test@test.com"},
                timeout=5
            )

            if response.status_code == 403 or 'csrf' in response.text.lower():
                self.log(
                    "CSRF Protection",
                    "PASS",
                    "Servidor rejeitou POST sem token CSRF"
                )
            else:
                self.log(
                    "CSRF Protection",
                    "WARN",
                    f"POST sem CSRF retornou {response.status_code}"
                )
        except Exception as e:
            self.log("CSRF Protection", "WARN", f"Erro ao testar: {str(e)}")

    def test_security_headers(self):
        """Testa headers de segurança HTTP"""
        print("\n[*] TESTANDO SECURITY HEADERS")
        print("=" * 60)

        try:
            response = self.session.get(self.base_url, timeout=5)
            headers = response.headers

            # Headers esperados
            security_headers = {
                "X-Content-Type-Options": "nosniff",
                "X-Frame-Options": ["DENY", "SAMEORIGIN"],
                "Referrer-Policy": None,  # Qualquer valor é bom
                "Permissions-Policy": None,
            }

            for header, expected in security_headers.items():
                if header in headers:
                    value = headers[header]
                    if expected is None:
                        self.log(
                            f"Header: {header}",
                            "PASS",
                            f"Presente: {value}"
                        )
                    elif isinstance(expected, list):
                        if value in expected:
                            self.log(
                                f"Header: {header}",
                                "PASS",
                                f"Valor correto: {value}"
                            )
                        else:
                            self.log(
                                f"Header: {header}",
                                "WARN",
                                f"Valor inesperado: {value} (esperado: {expected})"
                            )
                    elif value == expected:
                        self.log(
                            f"Header: {header}",
                            "PASS",
                            f"Valor correto: {value}"
                        )
                    else:
                        self.log(
                            f"Header: {header}",
                            "WARN",
                            f"Valor incorreto: {value} (esperado: {expected})"
                        )
                else:
                    self.log(
                        f"Header: {header}",
                        "FAIL",
                        "Header de segurança ausente!"
                    )
        except Exception as e:
            self.log("Security Headers", "FAIL", f"Erro ao testar: {str(e)}")

    def test_rate_limiting(self):
        """Testa rate limiting"""
        print("\n[*] TESTANDO RATE LIMITING")
        print("=" * 60)

        try:
            url = urljoin(self.base_url, "/")

            # Faz 70 requisições rápidas (limite é 60/min)
            responses = []
            for i in range(70):
                try:
                    r = self.session.get(url, timeout=2)
                    responses.append(r.status_code)
                except:
                    pass

            # Verifica se alguma foi bloqueada (HTTP 429)
            blocked = [s for s in responses if s == 429]

            if blocked:
                self.log(
                    "Rate Limiting",
                    "PASS",
                    f"{len(blocked)} requisições bloqueadas após exceder limite"
                )
            else:
                self.log(
                    "Rate Limiting",
                    "WARN",
                    "Nenhuma requisição bloqueada (pode estar desabilitado em dev)"
                )
        except Exception as e:
            self.log("Rate Limiting", "WARN", f"Erro ao testar: {str(e)}")

    def test_authentication(self):
        """Testa bypass de autenticação"""
        print("\n[*] TESTANDO AUTENTICACAO")
        print("=" * 60)

        try:
            # Tenta acessar área protegida sem login
            protected_urls = [
                "/app/dashboard/",
                "/app/agendamentos/",
                "/app/financeiro/",
            ]

            for url in protected_urls:
                response = self.session.get(urljoin(self.base_url, url), timeout=5, allow_redirects=False)

                if response.status_code in [302, 303, 401, 403]:
                    self.log(
                        f"Auth Protection: {url}",
                        "PASS",
                        f"Redirecionado/bloqueado (HTTP {response.status_code})"
                    )
                elif response.status_code == 200:
                    self.log(
                        f"Auth Protection: {url}",
                        "FAIL",
                        "Acesso permitido sem autenticação!"
                    )
                else:
                    self.log(
                        f"Auth Protection: {url}",
                        "WARN",
                        f"Status inesperado: {response.status_code}"
                    )
        except Exception as e:
            self.log("Authentication", "WARN", f"Erro ao testar: {str(e)}")

    def print_summary(self):
        """Imprime resumo dos testes"""
        print("\n" + "=" * 60)
        print("[+] RESUMO DOS TESTES DE SEGURANCA")
        print("=" * 60)
        print(f"[OK] Passed:   {len(self.results['passed'])}")
        print(f"[WARN] Warnings: {len(self.results['warnings'])}")
        print(f"[FAIL] Failed:   {len(self.results['failed'])}")
        print("=" * 60)

        if self.results['failed']:
            print("\n[FAIL] TESTES FALHADOS:")
            for result in self.results['failed']:
                print(f"  - {result['test']}: {result['message']}")

        return len(self.results['failed']) == 0

    def run_all_tests(self):
        """Executa todos os testes"""
        print("\n[*] INICIANDO AUDITORIA DE SEGURANCA")
        print("=" * 60)
        print(f"Target: {self.base_url}")
        print("=" * 60)

        self.test_sql_injection()
        self.test_xss()
        self.test_csrf_protection()
        self.test_security_headers()
        self.test_rate_limiting()
        self.test_authentication()

        return self.print_summary()


if __name__ == "__main__":
    tester = SecurityTester()
    success = tester.run_all_tests()

    import sys
    sys.exit(0 if success else 1)
