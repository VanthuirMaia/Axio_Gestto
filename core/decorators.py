"""
Decorators customizados para controle de acesso baseado em planos
"""
from functools import wraps
from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse


def plano_required(feature_flag=None, feature_name=None, redirect_to='dashboard'):
    """
    Decorator para proteger views que requerem recursos específicos do plano.

    NOVA VERSÃO: Verifica feature flag específica (permite_financeiro, permite_dashboard_clientes, etc)

    Args:
        feature_flag: Nome do campo boolean no modelo Plano (ex: 'permite_financeiro')
        feature_name: Nome do recurso para exibir na mensagem (ex: 'Controle Financeiro')
        redirect_to: URL name para redirecionar caso bloqueado

    Uso:
        @login_required
        @plano_required(feature_flag='permite_financeiro', feature_name='Controle Financeiro')
        def financeiro_dashboard(request):
            ...

    Compatibilidade com código antigo:
        @plano_required(feature_name='Dashboard Financeiro')  # Usa permite_relatorios_avancados
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            # Verificar se usuário está autenticado
            if not request.user.is_authenticated:
                return redirect('login')

            # Verificar se tem empresa
            if not hasattr(request.user, 'empresa') or not request.user.empresa:
                messages.error(request, 'Você precisa estar vinculado a uma empresa.')
                return redirect('dashboard')

            empresa = request.user.empresa

            # Verificar se tem assinatura ativa
            assinatura = getattr(empresa, 'assinatura_ativa', None)
            if not assinatura:
                messages.error(request, 'Sua empresa não possui uma assinatura ativa.')
                return redirect('dashboard')

            plano = assinatura.plano

            # Determinar qual flag verificar
            flag_to_check = feature_flag if feature_flag else 'permite_relatorios_avancados'
            display_name = feature_name if feature_name else 'este recurso'

            # Verificar se o plano tem a feature flag
            if not getattr(plano, flag_to_check, False):
                messages.warning(
                    request,
                    f'🔒 <strong>{display_name}</strong> está disponível apenas no <strong>Plano Profissional</strong>. '
                    f'<a href="{reverse("configuracoes_assinatura")}" class="alert-link">Faça upgrade agora</a> '
                    f'para ter acesso completo.',
                    extra_tags='safe'
                )
                return redirect(redirect_to)

            # Plano OK, executar view normalmente
            return view_func(request, *args, **kwargs)

        return wrapper
    return decorator


def plano_profissional_required(view_func):
    """
    Atalho para @plano_required() com configurações padrão.

    Uso:
        @login_required
        @plano_profissional_required
        def minha_view(request):
            ...
    """
    return plano_required()(view_func)
