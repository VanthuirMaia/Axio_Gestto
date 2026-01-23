from .models import PageView
import uuid


class AnalyticsMiddleware:
    """Middleware para rastrear automaticamente pageviews na landing"""
    
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Criar ou obter session_id
        if 'analytics_session' not in request.session:
            request.session['analytics_session'] = str(uuid.uuid4())
        
        # Registrar pageview apenas para páginas da landing (não admin, static, etc)
        if self._should_track(request):
            try:
                PageView.objects.create(
                    page_url=request.build_absolute_uri(),
                    referrer=request.META.get('HTTP_REFERER', ''),
                    user_agent=request.META.get('HTTP_USER_AGENT', '')[:500],  # Limita tamanho
                    ip_address=self._get_client_ip(request),
                    session_id=request.session.get('analytics_session', '')
                )
            except Exception as e:
                # Não quebrar a aplicação se houver erro no analytics
                print(f"Erro ao registrar pageview: {e}")
        
        response = self.get_response(request)
        return response
    
    def _should_track(self, request):
        """Determina se deve rastrear esta requisição"""
        path = request.path
        
        # Não rastrear admin, static, media, api
        excluded_paths = ['/admin/', '/static/', '/media/', '/api/', '/backoffice/']
        if any(path.startswith(excluded) for excluded in excluded_paths):
            return False
        
        # Não rastrear requisições AJAX
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return False
        
        # Apenas GET requests
        if request.method != 'GET':
            return False
        
        return True
    
    def _get_client_ip(self, request):
        """Obtém o IP real do cliente considerando proxies"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR', '127.0.0.1')
        return ip
