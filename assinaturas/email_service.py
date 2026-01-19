from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
import logging

logger = logging.getLogger(__name__)

def enviar_email_boas_vindas(usuario, empresa, activation_token, plano):
    """
    Envia email HTML com link de ativação de conta.
    Pode ser chamado pela view de cadastro (manual) ou pelo webhook (stripe/asaas).
    
    Args:
        usuario: Instância de Usuario
        empresa: Instância de Empresa
        activation_token: Token de ativação gerado
        plano: Instância de Plano
    """
    try:
        # Validar configurações de email antes de tentar enviar
        if not hasattr(settings, 'EMAIL_HOST') or not settings.EMAIL_HOST:
            logger.error('EMAIL_HOST não configurado. Não é possível enviar email.')
            raise ValueError('Configuração de email incompleta: EMAIL_HOST não definido')
        
        if not hasattr(settings, 'DEFAULT_FROM_EMAIL') or not settings.DEFAULT_FROM_EMAIL:
            logger.error('DEFAULT_FROM_EMAIL não configurado. Não é possível enviar email.')
            raise ValueError('Configuração de email incompleta: DEFAULT_FROM_EMAIL não definido')
        
        # Log antes de tentar enviar
        logger.info(f'Preparando email de boas-vindas para {usuario.email}')
        logger.info(f'  Empresa: {empresa.nome}')
        logger.info(f'  Plano: {plano.nome}')
        
        # Contexto para o template
        context = {
            'usuario': usuario,
            'empresa': empresa,
            'activation_token': activation_token,
            'plano': plano,
            'trial_expira_em': empresa.assinatura.data_expiracao if hasattr(empresa, 'assinatura') else None,
            'site_url': settings.SITE_URL if hasattr(settings, 'SITE_URL') else 'http://localhost:8000',
        }

        # Renderiza o template HTML
        logger.info('Renderizando template de email...')
        html_message = render_to_string('emails/boas_vindas_com_senha.html', context)
        # Versão texto puro (fallback)
        plain_message = strip_tags(html_message)

        # Configurações do email
        from_email = settings.DEFAULT_FROM_EMAIL
        subject = f'Ative sua conta - {empresa.nome} | Gestto 🎉'
        
        # Envia o email
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=from_email,
            recipient_list=[usuario.email],
            html_message=html_message,
            fail_silently=False,  # Lança exceção se falhar
        )

        logger.info(f'✓ Email de boas-vindas enviado com sucesso para {usuario.email}')

    except Exception as e:
        logger.error(f'Erro ao enviar email de boas-vindas para {usuario.email}: {str(e)}')
        raise
