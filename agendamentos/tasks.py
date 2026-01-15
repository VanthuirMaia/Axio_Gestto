"""
Tasks Celery para agendamentos
"""
from celery import shared_task
from django.utils import timezone
from datetime import timedelta
import logging

logger = logging.getLogger(__name__)


@shared_task
def enviar_lembretes_agendamentos():
    """
    Envia lembretes de agendamentos conforme configuração do plano.
    
    Executa a cada 10 minutos via Celery Beat.
    
    Lógica:
    - Lembrete 1 dia antes (24h): Todos os planos
    - Lembrete 1 hora antes: Apenas planos que permitem
    """
    from agendamentos.models import Agendamento
    from empresas.services.evolution_api import EvolutionAPIService
    
    agora = timezone.now()
    lembretes_enviados = {'1_dia': 0, '1_hora': 0, 'erros': 0}
    
    # ========== LEMBRETE 1 DIA ANTES (24h) ==========
    # Busca agendamentos entre 23h50min e 24h10min no futuro
    inicio_janela_1dia = agora + timedelta(hours=23, minutes=50)
    fim_janela_1dia = agora + timedelta(hours=24, minutes=10)
    
    agendamentos_1_dia = Agendamento.objects.filter(
        data_hora_inicio__gte=inicio_janela_1dia,
        data_hora_inicio__lte=fim_janela_1dia,
        status='confirmado',
        notificado_1dia=False
    ).select_related(
        'empresa__assinatura__plano',
        'empresa__configuracao_whatsapp',
        'cliente',
        'servico',
        'profissional'
    )
    
    logger.info(f"Encontrados {agendamentos_1_dia.count()} agendamentos para lembrete de 1 dia")
    
    for agendamento in agendamentos_1_dia:
        try:
            plano = agendamento.empresa.assinatura.plano
            
            # Verificar se plano permite lembrete de 1 dia
            if not plano.permite_lembrete_1_dia:
                logger.debug(f"Plano {plano.nome} não permite lembrete de 1 dia")
                continue
            
            # Enviar lembrete
            sucesso = _enviar_mensagem_lembrete(agendamento, tipo='1_dia')
            
            if sucesso:
                agendamento.notificado_1dia = True
                agendamento.save(update_fields=['notificado_1dia'])
                lembretes_enviados['1_dia'] += 1
                logger.info(f"Lembrete 1 dia enviado: Agendamento #{agendamento.id}")
            else:
                lembretes_enviados['erros'] += 1
                
        except Exception as e:
            logger.error(f"Erro ao enviar lembrete 1 dia para agendamento #{agendamento.id}: {e}")
            lembretes_enviados['erros'] += 1
    
    # ========== LEMBRETE 1 HORA ANTES ==========
    # Busca agendamentos entre 50min e 1h10min no futuro
    inicio_janela_1hora = agora + timedelta(minutes=50)
    fim_janela_1hora = agora + timedelta(hours=1, minutes=10)
    
    agendamentos_1_hora = Agendamento.objects.filter(
        data_hora_inicio__gte=inicio_janela_1hora,
        data_hora_inicio__lte=fim_janela_1hora,
        status='confirmado',
        notificado_1hora=False
    ).select_related(
        'empresa__assinatura__plano',
        'empresa__configuracao_whatsapp',
        'cliente',
        'servico',
        'profissional'
    )
    
    logger.info(f"Encontrados {agendamentos_1_hora.count()} agendamentos para lembrete de 1 hora")
    
    for agendamento in agendamentos_1_hora:
        try:
            plano = agendamento.empresa.assinatura.plano
            
            # Verificar se plano permite lembrete de 1 hora (apenas planos superiores)
            if not plano.permite_lembrete_1_hora:
                logger.debug(f"Plano {plano.nome} não permite lembrete de 1 hora")
                continue
            
            # Enviar lembrete
            sucesso = _enviar_mensagem_lembrete(agendamento, tipo='1_hora')
            
            if sucesso:
                agendamento.notificado_1hora = True
                agendamento.save(update_fields=['notificado_1hora'])
                lembretes_enviados['1_hora'] += 1
                logger.info(f"Lembrete 1 hora enviado: Agendamento #{agendamento.id}")
            else:
                lembretes_enviados['erros'] += 1
                
        except Exception as e:
            logger.error(f"Erro ao enviar lembrete 1 hora para agendamento #{agendamento.id}: {e}")
            lembretes_enviados['erros'] += 1
    
    # Log resumo
    logger.info(
        f"Lembretes enviados: {lembretes_enviados['1_dia']} (1 dia), "
        f"{lembretes_enviados['1_hora']} (1 hora), "
        f"{lembretes_enviados['erros']} erros"
    )
    
    return lembretes_enviados


def _enviar_mensagem_lembrete(agendamento, tipo='1_dia'):
    """
    Envia mensagem de lembrete via Evolution API (WhatsApp)
    
    Args:
        agendamento: Instância de Agendamento
        tipo: '1_dia' ou '1_hora'
    
    Returns:
        bool: True se enviou com sucesso
    """
    config_whatsapp = agendamento.empresa.configuracao_whatsapp
    
    # Verificar se WhatsApp está conectado
    if not config_whatsapp or config_whatsapp.status != 'conectado':
        logger.warning(
            f"WhatsApp não conectado para empresa {agendamento.empresa.nome} "
            f"(ID: {agendamento.empresa.id})"
        )
        return False
    
    # Montar mensagem conforme tipo
    if tipo == '1_dia':
        mensagem = f"""🔔 *Lembrete de Agendamento*

Olá {agendamento.cliente.nome}! 

Você tem um agendamento amanhã:

📅 Data: {agendamento.data_hora_inicio.strftime('%d/%m/%Y')}
🕐 Horário: {agendamento.data_hora_inicio.strftime('%H:%M')}
✂️ Serviço: {agendamento.servico.nome}
👤 Profissional: {agendamento.profissional.nome if agendamento.profissional else 'A definir'}

Nos vemos lá! 😊

_Para cancelar ou reagendar, responda esta mensagem._"""
    
    else:  # 1_hora
        mensagem = f"""⏰ *Lembrete: Seu horário é daqui a 1 hora!*

Olá {agendamento.cliente.nome}!

Seu agendamento é às *{agendamento.data_hora_inicio.strftime('%H:%M')}*

✂️ {agendamento.servico.nome}
👤 Com {agendamento.profissional.nome if agendamento.profissional else 'nosso profissional'}

Até já! 🚀"""
    
    # Enviar via Evolution API
    try:
        service = EvolutionAPIService(config_whatsapp)
        resultado = service.enviar_mensagem(
            numero=agendamento.cliente.telefone,
            mensagem=mensagem
        )
        
        return resultado.get('success', False)
        
    except Exception as e:
        logger.error(f"Erro ao enviar mensagem via Evolution API: {e}")
        return False
