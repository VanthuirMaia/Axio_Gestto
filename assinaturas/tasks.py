"""
Tasks Celery para sistema de assinaturas.
"""
from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.utils.timezone import now
from datetime import timedelta
import logging

logger = logging.getLogger(__name__)


@shared_task
def notificar_trials_expirando():
    """
    Task que notifica empresas cujos trials estão prestes a expirar.

    Executa diariamente e envia notificações:
    - 3 dias antes da expiração
    - 1 dia antes da expiração
    - No dia da expiração

    Utiliza campo metadados da Assinatura para evitar duplicatas.
    """
    from assinaturas.models import Assinatura
    from empresas.models import ConfiguracaoWhatsApp
    from empresas.services import EvolutionAPIService

    hoje = now().date()

    # Buscar assinaturas em trial
    assinaturas_trial = Assinatura.objects.filter(
        status='trial',
        trial_ativo=True
    ).select_related('empresa', 'plano')

    notificacoes_enviadas = 0
    erros = 0

    for assinatura in assinaturas_trial:
        try:
            data_expiracao = assinatura.data_expiracao.date()
            dias_restantes = (data_expiracao - hoje).days

            # Determinar qual notificação enviar
            tipo_notificacao = None

            if dias_restantes == 3:
                tipo_notificacao = '3_dias'
            elif dias_restantes == 1:
                tipo_notificacao = '1_dia'
            elif dias_restantes == 0:
                tipo_notificacao = 'hoje'

            if not tipo_notificacao:
                continue

            # Verificar se já foi notificado
            metadados = assinatura.metadados or {}
            notificacoes = metadados.get('notificacoes_trial', {})

            chave_notificacao = f'trial_expirando_{tipo_notificacao}'
            if notificacoes.get(chave_notificacao):
                logger.debug(
                    f"Empresa {assinatura.empresa.nome} já notificada para {tipo_notificacao}"
                )
                continue

            # Buscar dados necessários
            empresa = assinatura.empresa
            usuario_admin = empresa.usuarios.filter(is_staff=True).first()

            if not usuario_admin:
                usuario_admin = empresa.usuarios.first()

            if not usuario_admin:
                logger.warning(f"Empresa {empresa.nome} sem usuário para notificar")
                continue

            # Enviar email
            email_enviado = _enviar_email_trial_expirando(
                usuario=usuario_admin,
                empresa=empresa,
                assinatura=assinatura,
                dias_restantes=dias_restantes,
                tipo_notificacao=tipo_notificacao
            )

            # Tentar enviar WhatsApp (opcional)
            whatsapp_enviado = False
            try:
                config_whatsapp = ConfiguracaoWhatsApp.objects.get(empresa=empresa)
                if config_whatsapp.esta_conectado() and usuario_admin.telefone:
                    whatsapp_enviado = _enviar_whatsapp_trial_expirando(
                        config_whatsapp=config_whatsapp,
                        telefone=usuario_admin.telefone,
                        empresa=empresa,
                        dias_restantes=dias_restantes,
                        tipo_notificacao=tipo_notificacao
                    )
            except ConfiguracaoWhatsApp.DoesNotExist:
                pass
            except Exception as e:
                logger.warning(f"Erro ao enviar WhatsApp para {empresa.nome}: {e}")

            # Marcar como notificado
            if email_enviado or whatsapp_enviado:
                notificacoes[chave_notificacao] = now().isoformat()
                metadados['notificacoes_trial'] = notificacoes
                assinatura.metadados = metadados
                assinatura.save(update_fields=['metadados'])

                notificacoes_enviadas += 1
                logger.info(
                    f"Notificação {tipo_notificacao} enviada para {empresa.nome} "
                    f"(email={email_enviado}, whatsapp={whatsapp_enviado})"
                )

        except Exception as e:
            erros += 1
            logger.error(f"Erro ao processar notificação para {assinatura.empresa.nome}: {e}")

    logger.info(
        f"Task notificar_trials_expirando finalizada: "
        f"{notificacoes_enviadas} enviadas, {erros} erros"
    )

    return {
        'notificacoes_enviadas': notificacoes_enviadas,
        'erros': erros
    }


def _enviar_email_trial_expirando(usuario, empresa, assinatura, dias_restantes, tipo_notificacao):
    """
    Envia email de notificação de trial expirando.

    Args:
        usuario: Usuário admin da empresa
        empresa: Empresa
        assinatura: Assinatura
        dias_restantes: Dias restantes do trial
        tipo_notificacao: '3_dias', '1_dia' ou 'hoje'

    Returns:
        bool: True se enviou com sucesso
    """
    try:
        # Selecionar template baseado no tipo
        template_name = f'emails/trial_expirando_{tipo_notificacao}.html'

        # Contexto para o template
        context = {
            'usuario': usuario,
            'empresa': empresa,
            'assinatura': assinatura,
            'plano': assinatura.plano,
            'dias_restantes': dias_restantes,
            'data_expiracao': assinatura.data_expiracao,
            'site_url': getattr(settings, 'SITE_URL', 'https://gestto.com.br'),
            'checkout_url': f"{getattr(settings, 'SITE_URL', 'https://gestto.com.br')}/app/configuracoes/assinatura/",
        }

        # Renderizar template
        html_message = render_to_string(template_name, context)
        plain_message = strip_tags(html_message)

        # Assuntos personalizados
        assuntos = {
            '3_dias': f'Seu trial termina em 3 dias - {empresa.nome} | Gestto',
            '1_dia': f'URGENTE: Seu trial termina amanhã - {empresa.nome} | Gestto',
            'hoje': f'ÚLTIMO DIA: Seu trial expira hoje - {empresa.nome} | Gestto',
        }

        subject = assuntos.get(tipo_notificacao, f'Seu trial está expirando - {empresa.nome}')

        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[usuario.email],
            html_message=html_message,
            fail_silently=False,
        )

        return True

    except Exception as e:
        logger.error(f"Erro ao enviar email trial expirando para {usuario.email}: {e}")
        return False


def _enviar_whatsapp_trial_expirando(config_whatsapp, telefone, empresa, dias_restantes, tipo_notificacao):
    """
    Envia mensagem WhatsApp de notificação de trial expirando.

    Args:
        config_whatsapp: ConfiguracaoWhatsApp da empresa GESTTO (não da empresa cliente)
        telefone: Telefone do usuário
        empresa: Empresa do cliente
        dias_restantes: Dias restantes
        tipo_notificacao: '3_dias', '1_dia' ou 'hoje'

    Returns:
        bool: True se enviou com sucesso
    """
    try:
        from empresas.services import EvolutionAPIService

        # Formatar número
        numero = telefone.replace(' ', '').replace('-', '').replace('(', '').replace(')', '')
        if not numero.startswith('55'):
            numero = f'55{numero}'

        # Mensagens personalizadas
        checkout_url = f"{getattr(settings, 'SITE_URL', 'https://gestto.com.br')}/app/configuracoes/assinatura/"

        mensagens = {
            '3_dias': (
                f"Olá! Seu período de teste do Gestto termina em *3 dias*.\n\n"
                f"Você está aproveitando todas as funcionalidades?\n\n"
                f"Para continuar usando sem interrupção, assine agora:\n"
                f"{checkout_url}\n\n"
                f"Qualquer dúvida, estamos à disposição!"
            ),
            '1_dia': (
                f"Atenção! Seu trial do Gestto *expira amanhã*.\n\n"
                f"Não perca seus dados e configurações!\n\n"
                f"Assine agora e continue usando:\n"
                f"{checkout_url}\n\n"
                f"Precisa de ajuda? Responda esta mensagem!"
            ),
            'hoje': (
                f"*ÚLTIMO DIA!* Seu trial do Gestto expira *hoje*.\n\n"
                f"Após a expiração, você perderá acesso às funcionalidades.\n\n"
                f"Assine agora para não perder nada:\n"
                f"{checkout_url}\n\n"
                f"Seus dados serão mantidos por mais 30 dias."
            ),
        }

        mensagem = mensagens.get(tipo_notificacao, mensagens['3_dias'])

        # Usar o WhatsApp do Gestto para enviar (não o WhatsApp da empresa cliente)
        # Buscar configuração do WhatsApp master
        from empresas.models import ConfiguracaoWhatsApp as ConfigWpp

        # Buscar uma empresa admin/sistema ou usar variável de ambiente
        master_instance = getattr(settings, 'GESTTO_WHATSAPP_INSTANCE', None)

        if master_instance:
            # Usar instância master para enviar notificações
            config_master = ConfigWpp.objects.filter(instance_name=master_instance).first()
            if config_master and config_master.esta_conectado():
                service = EvolutionAPIService(config_master)
                result = service.enviar_mensagem_texto(numero, mensagem)
                return result.get('success', False)

        # Se não tem instância master configurada, não envia WhatsApp
        logger.info("GESTTO_WHATSAPP_INSTANCE não configurada, WhatsApp não enviado")
        return False

    except Exception as e:
        logger.error(f"Erro ao enviar WhatsApp trial expirando: {e}")
        return False
