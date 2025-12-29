"""
Middleware para controle de limites por plano (SaaS)

Bloqueia ações quando limites são excedidos:
- Max profissionais
- Max agendamentos por mês
- Assinatura expirada/suspensa
"""

from django.shortcuts import redirect
from django.contrib import messages
from django.utils.timezone import now
from django.urls import reverse
from datetime import timedelta


class LimitesPlanoMiddleware:
    """
    Middleware que verifica os limites do plano antes de permitir ações

    Rotas protegidas:
    - /clientes/criar/
    - /agendamentos/criar/
    - /profissionais/criar/ (futura)
    - /configuracoes/profissionais/criar/
    """

    # URLs que serão verificadas
    ROTAS_PROTEGIDAS = [
        '/agendamentos/criar/',
        '/agendamentos/recorrencias/criar/',
        '/clientes/criar/',
        '/configuracoes/profissionais/criar/',
    ]

    # URLs que NUNCA serão bloqueadas (essenciais)
    ROTAS_EXCLUIDAS = [
        '/admin/',
        '/login/',
        '/logout/',
        '/dashboard/',
        '/health/',
        '/api/',
        '/configuracoes/assinatura/',  # Permitir acesso à página de upgrade
        '/password-reset/',
    ]

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Verificar limites antes de processar a requisição
        if request.user.is_authenticated and hasattr(request.user, 'empresa'):
            empresa = request.user.empresa

            # Pular verificação se não tem assinatura (admin, empresa sem assinatura, etc)
            try:
                assinatura = empresa.assinatura
            except Exception:
                # Empresa não tem assinatura - permitir acesso (admin pode estar criando)
                return self.get_response(request)

            plano = assinatura.plano

            # Verificar se a rota precisa de validação
            path = request.path

            # Pular rotas excluídas
            if any(path.startswith(rota) for rota in self.ROTAS_EXCLUIDAS):
                return self.get_response(request)

            # 1. VERIFICAR ASSINATURA ATIVA
            if assinatura.status not in ['ativa', 'trial']:
                if not path.startswith('/configuracoes/assinatura/'):
                    messages.error(
                        request,
                        f'Sua assinatura está {assinatura.status}. '
                        'Regularize o pagamento para continuar.'
                    )
                    return redirect('configuracoes_assinatura')

            # 2. VERIFICAR EXPIRAÇÃO
            if assinatura.data_expiracao and assinatura.data_expiracao < now():
                # Auto-suspender se expirou
                if assinatura.status in ['ativa', 'trial']:
                    assinatura.status = 'suspensa'
                    assinatura.save()

                messages.error(
                    request,
                    f'Sua assinatura expirou em {assinatura.data_expiracao.strftime("%d/%m/%Y")}. '
                    'Renove para continuar usando o sistema.'
                )
                return redirect('configuracoes_assinatura')

            # 3. VERIFICAR LIMITE DE PROFISSIONAIS
            if '/profissionais/criar/' in path or '/configuracoes/profissionais/criar/' in path:
                from empresas.models import Profissional

                total_profissionais = Profissional.objects.filter(
                    empresa=empresa,
                    ativo=True
                ).count()

                if total_profissionais >= plano.max_profissionais:
                    messages.warning(
                        request,
                        f'Você atingiu o limite de {plano.max_profissionais} profissionais do plano {plano.get_nome_display()}. '
                        f'Faça upgrade para adicionar mais profissionais.'
                    )
                    return redirect('configuracoes_assinatura')

            # 4. VERIFICAR LIMITE DE AGENDAMENTOS DO MÊS
            if any(rota in path for rota in ['/agendamentos/criar/', '/api/whatsapp-webhook/', '/api/bot/processar/']):
                from agendamentos.models import Agendamento

                # Contar agendamentos do mês atual
                inicio_mes = now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)

                agendamentos_mes = Agendamento.objects.filter(
                    empresa=empresa,
                    criado_em__gte=inicio_mes,
                    status__in=['pendente', 'confirmado', 'concluido']
                ).count()

                # Calcular porcentagem de uso
                percentual_uso = (agendamentos_mes / plano.max_agendamentos_mes) * 100

                # Avisar quando atingir 80%
                if percentual_uso >= 80 and percentual_uso < 100:
                    messages.warning(
                        request,
                        f'⚠️ Você já usou {agendamentos_mes} de {plano.max_agendamentos_mes} agendamentos este mês ({percentual_uso:.0f}%). '
                        f'Considere fazer upgrade do plano.'
                    )

                # Bloquear quando atingir 100%
                if agendamentos_mes >= plano.max_agendamentos_mes:
                    messages.error(
                        request,
                        f'❌ Limite de {plano.max_agendamentos_mes} agendamentos/mês atingido! '
                        f'Faça upgrade para o plano superior ou aguarde o próximo mês.'
                    )

                    # Se for criação manual, redirecionar
                    if '/agendamentos/criar/' in path:
                        return redirect('configuracoes_assinatura')

                    # Se for API/webhook, deixar o endpoint retornar erro 429

        # Continuar processamento normal
        response = self.get_response(request)
        return response


class AssinaturaExpiracaoMiddleware:
    """
    Middleware que mostra avisos quando a assinatura está próxima de expirar

    Avisos:
    - 7 dias antes: Warning
    - 3 dias antes: Error
    - No dia: Critical
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated and hasattr(request.user, 'empresa'):
            empresa = request.user.empresa

            try:
                assinatura = empresa.assinatura
            except Exception:
                # Empresa não tem assinatura - não mostrar avisos
                return self.get_response(request)

            if assinatura:

                # Apenas para assinaturas ativas
                if assinatura.status in ['ativa', 'trial'] and assinatura.data_expiracao:
                    dias_restantes = (assinatura.data_expiracao - now()).days

                    # Mostrar aviso apenas no dashboard (não em páginas públicas/landing)
                    # Excluir rotas da landing page e páginas públicas
                    is_landing_page = request.path.startswith('/landing/') or request.path in ['/', '/login/', '/cadastro/']

                    if request.path == '/dashboard/' and not is_landing_page:
                        if dias_restantes <= 0:
                            messages.error(
                                request,
                                '🚨 Sua assinatura expirou hoje! Renove agora para evitar interrupções.'
                            )
                        elif dias_restantes <= 3:
                            messages.error(
                                request,
                                f'⚠️ Sua assinatura expira em {dias_restantes} dia(s)! Renove para manter o acesso.'
                            )
                        elif dias_restantes <= 7:
                            messages.warning(
                                request,
                                f'📅 Sua assinatura expira em {dias_restantes} dias. Renove com antecedência!'
                            )

        response = self.get_response(request)
        return response


class UsageTrackingMiddleware:
    """
    Middleware que rastreia uso do sistema para métricas

    Rastreia:
    - Páginas acessadas
    - Features usadas
    - Tempo de resposta
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Registrar início da requisição
        import time
        start_time = time.time()

        # Processar requisição
        response = self.get_response(request)

        # Calcular tempo de resposta
        duration = time.time() - start_time

        # Log de uso (apenas para usuários autenticados)
        if request.user.is_authenticated and hasattr(request.user, 'empresa'):
            # Aqui você pode salvar métricas em um model futuro
            # Por enquanto, apenas adicionar header de debug
            try:
                response['X-Plan'] = request.user.empresa.assinatura.plano.nome
                response['X-Response-Time'] = f'{duration:.3f}s'
            except Exception:
                # Empresa sem assinatura - skip headers
                pass

        return response
