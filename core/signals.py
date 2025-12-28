from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.utils.html import strip_tags
from .models import Usuario


@receiver(post_save, sender=Usuario)
def enviar_email_boas_vindas(sender, instance, created, **kwargs):
    """
    Envia email de boas-vindas quando um novo usuário é criado

    NOTA: Este signal só dispara para usuários criados MANUALMENTE (sem empresa).
    Usuários criados via sistema de assinaturas recebem email com senha através
    da função _enviar_email_boas_vindas() em assinaturas/views.py
    """
    if created:
        # Se o usuário tem empresa, significa que foi criado via assinatura
        # Nesse caso, o email já foi/será enviado pela função de assinatura com a senha
        if instance.empresa:
            return

        # Usuário criado manualmente (sem empresa) - envia email padrão
        try:
            # Contexto para o template
            context = {
                'usuario': instance,
                'site_url': settings.SITE_URL,
            }

            # Renderiza o template HTML
            html_message = render_to_string('emails/usuario_boas_vindas.html', context)
            # Versão texto puro (fallback)
            plain_message = strip_tags(html_message)

            # Envia o email
            send_mail(
                subject='Bem-vindo ao Axio Gestto!',
                message=plain_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[instance.email],
                html_message=html_message,
                fail_silently=True,  # Não quebra a aplicação se o email falhar
            )
        except Exception as e:
            # Log do erro (opcional)
            print(f"Erro ao enviar email de boas-vindas para {instance.email}: {e}")
