from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.utils.html import strip_tags
from .models import Empresa


@receiver(post_save, sender=Empresa)
def enviar_email_empresa_criada(sender, instance, created, **kwargs):
    """
    Envia email de confirmação quando uma nova empresa é criada
    """
    if created:
        try:
            # Contexto para o template
            context = {
                'empresa': instance,
                'site_url': settings.SITE_URL,
            }

            # Renderiza o template HTML
            html_message = render_to_string('emails/empresa_criada.html', context)
            # Versão texto puro (fallback)
            plain_message = strip_tags(html_message)

            # Envia o email para o email da empresa
            send_mail(
                subject=f'Empresa {instance.nome} cadastrada com sucesso!',
                message=plain_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[instance.email],
                html_message=html_message,
                fail_silently=True,  # Não quebra a aplicação se o email falhar
            )
        except Exception as e:
            # Log do erro (opcional)
            print(f"Erro ao enviar email de empresa criada para {instance.email}: {e}")
