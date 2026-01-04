"""
Middleware de segurança e monitoramento para a Landing Page
"""
import logging
import time
from django.utils.deprecation import MiddlewareMixin
from django.http import HttpResponseForbidden

logger = logging.getLogger('landing')


class LandingSecurityMonitoringMiddleware(MiddlewareMixin):
    """
    Middleware para monitorar e registrar atividades suspeitas na landing page
    """

    SUSPICIOUS_PATHS = [
        '/admin',
        '/.env',
        '/config',
        '/wp-admin',
        '/phpmyadmin',
        '/.git',
        '/backup',
        '/.aws',
    ]

    SUSPICIOUS_USER_AGENTS = [
        'sqlmap',
        'nikto',
        'nessus',
        'nmap',
        'masscan',
        'curl',  # Pode ser legítimo, mas vale monitorar
        'wget',
    ]

    def process_request(self, request):
        """Monitora requests suspeitos"""

        # Captura tempo de início para métricas
        request.start_time = time.time()

        # Verifica path suspeito
        if any(suspicious in request.path.lower() for suspicious in self.SUSPICIOUS_PATHS):
            logger.warning(
                f"[SUSPEITO] Acesso a path suspeito: {request.path} | "
                f"IP: {self.get_client_ip(request)} | "
                f"User-Agent: {request.META.get('HTTP_USER_AGENT', 'N/A')}"
            )
            # Pode bloquear ou apenas logar
            # return HttpResponseForbidden("Acesso negado")

        # Verifica User-Agent suspeito
        user_agent = request.META.get('HTTP_USER_AGENT', '').lower()
        if any(suspicious in user_agent for suspicious in self.SUSPICIOUS_USER_AGENTS):
            logger.warning(
                f"[SUSPEITO] User-Agent suspeito: {user_agent} | "
                f"IP: {self.get_client_ip(request)} | "
                f"Path: {request.path}"
            )

        # Detecta possível SQL Injection
        query_string = request.META.get('QUERY_STRING', '').lower()
        if any(keyword in query_string for keyword in ['union', 'select', 'drop', 'insert', 'update', 'delete', '--', "'"]):
            logger.critical(
                f"[ATAQUE] Possível SQL Injection detectado! | "
                f"Query: {query_string} | "
                f"IP: {self.get_client_ip(request)} | "
                f"Path: {request.path}"
            )
            return HttpResponseForbidden("Requisição inválida")

        # Detecta possível XSS
        if '<script' in query_string or 'javascript:' in query_string:
            logger.critical(
                f"[ATAQUE] Possível XSS detectado! | "
                f"Query: {query_string} | "
                f"IP: {self.get_client_ip(request)} | "
                f"Path: {request.path}"
            )
            return HttpResponseForbidden("Requisição inválida")

        return None

    def process_response(self, request, response):
        """Loga tempo de resposta e adiciona headers de segurança"""

        # Calcula tempo de resposta
        if hasattr(request, 'start_time'):
            duration = time.time() - request.start_time

            # Loga requests lentos (> 2 segundos)
            if duration > 2:
                logger.warning(
                    f"[PERFORMANCE] Request lento: {duration:.2f}s | "
                    f"Path: {request.path} | "
                    f"IP: {self.get_client_ip(request)}"
                )

        # Adiciona headers de segurança extras
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-Frame-Options'] = 'DENY'
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        response['Permissions-Policy'] = 'geolocation=(), microphone=(), camera=()'

        return response

    @staticmethod
    def get_client_ip(request):
        """Obtém o IP real do cliente, considerando proxies"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
