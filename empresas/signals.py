from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.utils.html import strip_tags
from .models import Empresa, ConfiguracaoWhatsApp


@receiver(post_save, sender=Empresa)
def enviar_email_empresa_criada(sender, instance, created, **kwargs):
    """
    Envia email de confirmação quando uma nova empresa é criada
    e cria automaticamente a configuração WhatsApp.
    """
    if created:
        # === 1️⃣ Cria Configuração WhatsApp automaticamente ===
        try:
            config, created_conf = ConfiguracaoWhatsApp.objects.get_or_create(
                empresa=instance,
                defaults={"status": "nao_configurado"}
            )
            if created_conf:
                print(f"⚙️ Configuração WhatsApp criada automaticamente para {instance.nome}")
            else:
                print(f"ℹ️ Configuração WhatsApp já existia para {instance.nome}")
        except Exception as e:
            print(f"❌ Erro ao criar configuração WhatsApp para {instance.nome}: {e}")

        # === 2️⃣ Envia e-mail de confirmação da empresa ===
        # IMPORTANTE: Não enviar email se a empresa foi criada via checkout
        # pois o usuário já recebe o email de ativação de conta
        if instance.origem_cadastro == 'checkout':
            print(f"ℹ️ Email não enviado - empresa criada via checkout (usuário recebe email de ativação)")
            return
        
        try:
            context = {
                'empresa': instance,
                'site_url': settings.SITE_URL,
            }

            html_message = render_to_string('emails/empresa_criada.html', context)
            plain_message = strip_tags(html_message)

            send_mail(
                subject=f'Empresa {instance.nome} cadastrada com sucesso!',
                message=plain_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[instance.email],
                html_message=html_message,
                fail_silently=True,
            )
        except Exception as e:
            print(f"Erro ao enviar email de empresa criada para {instance.email}: {e}")
