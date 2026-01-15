"""
Teste de Carga e Stress da Landing Page
Simula multiplos usuarios acessando simultaneamente
"""
from locust import HttpUser, task, between

class LandingPageUser(HttpUser):
    """Simula um usuario navegando na landing page"""

    # Tempo de espera entre acoes (1-3 segundos)
    wait_time = between(1, 3)

    @task(10)  # Peso 10 - tarefa mais comum
    def view_home(self):
        """Acessa a home page"""
        self.client.get("/")

    @task(5)  # Peso 5
    def view_precos(self):
        """Visualiza secao de precos"""
        self.client.get("/#precos")

    @task(3)  # Peso 3
    def view_sobre(self):
        """Visualiza secao sobre"""
        self.client.get("/#sobre")

    @task(3)  # Peso 3
    def view_contato(self):
        """Visualiza secao de contato"""
        self.client.get("/#contato")

    @task(2)  # Peso 2
    def view_cadastro(self):
        """Acessa pagina de cadastro"""
        self.client.get("/cadastro/")

    @task(1)  # Peso 1 - menos comum
    def view_static_resources(self):
        """Carrega recursos estaticos"""
        self.client.get("/static/css/landing.css", name="/static/css")


class CadastroStressUser(HttpUser):
    """Simula usuarios tentando se cadastrar (teste de stress)"""

    wait_time = between(2, 5)

    def on_start(self):
        """Executa antes de cada usuario comecar"""
        # Pega CSRF token
        response = self.client.get("/cadastro/")
        self.csrf_token = None
        if 'csrftoken' in self.client.cookies:
            self.csrf_token = self.client.cookies['csrftoken']

    @task
    def attempt_cadastro(self):
        """Tenta fazer um cadastro"""
        import random

        # Gera dados aleatorios
        empresa_id = random.randint(1000, 9999)
        data = {
            "nome_empresa": f"Empresa Teste {empresa_id}",
            "email_admin": f"teste{empresa_id}@exemplo.com",
            "telefone": f"11999{empresa_id:06d}",
            "cnpj": f"12345678000{empresa_id % 100:03d}"
        }

        if self.csrf_token:
            data['csrfmiddlewaretoken'] = self.csrf_token

        self.client.post("/cadastro/", data=data)
