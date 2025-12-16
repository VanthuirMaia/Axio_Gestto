from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils.timezone import now
from agendamentos.models import Agendamento, StatusAgendamento
from .models import LancamentoFinanceiro, TipoLancamento, StatusLancamento, CategoriaFinanceira


@receiver(post_save, sender=Agendamento)
def criar_receita_agendamento_concluido(sender, instance, created, **kwargs):
    """
    Cria automaticamente uma receita quando um agendamento é marcado como concluído
    """
    # Só processa se o agendamento foi concluído e tem valor
    if instance.status == StatusAgendamento.CONCLUIDO and instance.valor_cobrado:
        
        # Verifica se já existe um lançamento para este agendamento
        if not instance.lancamentos.exists():
            
            # Busca ou cria categoria padrão "Serviços"
            categoria, _ = CategoriaFinanceira.objects.get_or_create(
                empresa=instance.empresa,
                nome='Serviços',
                tipo=TipoLancamento.RECEITA,
                defaults={
                    'descricao': 'Receitas de serviços prestados',
                    'cor': '#28a745'
                }
            )
            
            # Cria o lançamento financeiro
            LancamentoFinanceiro.objects.create(
                empresa=instance.empresa,
                tipo=TipoLancamento.RECEITA,
                categoria=categoria,
                agendamento=instance,
                descricao=f"{instance.servico.nome} - {instance.cliente.nome}",
                valor=instance.valor_cobrado,
                data_vencimento=instance.data_hora_inicio.date(),
                data_pagamento=now().date(),
                status=StatusLancamento.PAGO,
                criado_por=None  # Pode ser ajustado se tiver o usuário que marcou como concluído
            )


@receiver(pre_save, sender=Agendamento)
def cancelar_receita_agendamento_cancelado(sender, instance, **kwargs):
    """
    Cancela a receita quando um agendamento concluído é cancelado
    """
    if instance.pk:  # Só processa se o agendamento já existe
        try:
            agendamento_anterior = Agendamento.objects.get(pk=instance.pk)
            
            # Se estava concluído e agora foi cancelado
            if (agendamento_anterior.status == StatusAgendamento.CONCLUIDO and 
                instance.status == StatusAgendamento.CANCELADO):
                
                # Cancela os lançamentos vinculados
                instance.lancamentos.filter(
                    status__in=[StatusLancamento.PENDENTE, StatusLancamento.PAGO]
                ).update(status=StatusLancamento.CANCELADO)
                
        except Agendamento.DoesNotExist:
            pass