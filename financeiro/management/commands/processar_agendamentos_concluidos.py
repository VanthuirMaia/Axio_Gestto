from django.core.management.base import BaseCommand
from django.utils.timezone import now
from datetime import timedelta
from agendamentos.models import Agendamento, StatusAgendamento
from financeiro.models import LancamentoFinanceiro, TipoLancamento, StatusLancamento, CategoriaFinanceira


class Command(BaseCommand):
    help = 'Processa agendamentos que terminaram há mais de 30 minutos e gera receitas'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Mostra o que seria processado sem executar',
        )

    def handle(self, *args, **options):
        agora = now()
        limite = agora - timedelta(minutes=30)  # 30 minutos atrás
        dry_run = options['dry_run']
        
        # Busca agendamentos que terminaram há mais de 30min e não foram cancelados
        agendamentos_para_processar = Agendamento.objects.filter(
            data_hora_fim__lt=limite,  # Terminou há mais de 30min
            status__in=[StatusAgendamento.PENDENTE, StatusAgendamento.CONFIRMADO]
        ).exclude(
            lancamentos__isnull=False  # Ainda não tem lançamento
        ).select_related('empresa', 'cliente', 'servico')

        total = agendamentos_para_processar.count()
        
        if total == 0:
            self.stdout.write(self.style.SUCCESS('✅ Nenhum agendamento para processar'))
            return

        self.stdout.write(self.style.WARNING(f'📋 Encontrados {total} agendamentos para processar'))

        processados = 0
        sem_valor = 0
        erros = 0

        for agendamento in agendamentos_para_processar:
            try:
                tempo_passado = agora - agendamento.data_hora_fim
                
                if dry_run:
                    self.stdout.write(
                        f'  [DRY-RUN] ID: {agendamento.id} | '
                        f'Cliente: {agendamento.cliente.nome} | '
                        f'Terminou há: {int(tempo_passado.total_seconds() / 60)}min | '
                        f'Valor: R$ {agendamento.valor_cobrado or 0}'
                    )
                else:
                    # Marca como concluído
                    agendamento.status = StatusAgendamento.CONCLUIDO
                    agendamento.save()
                    
                    # Só gera receita se tiver valor
                    if agendamento.valor_cobrado and agendamento.valor_cobrado > 0:
                        # Busca ou cria categoria
                        categoria, _ = CategoriaFinanceira.objects.get_or_create(
                            empresa=agendamento.empresa,
                            nome='Serviços',
                            tipo=TipoLancamento.RECEITA,
                            defaults={
                                'descricao': 'Receitas de serviços prestados',
                                'cor': '#28a745'
                            }
                        )
                        
                        # Cria lançamento pendente
                        LancamentoFinanceiro.objects.create(
                            empresa=agendamento.empresa,
                            tipo=TipoLancamento.RECEITA,
                            categoria=categoria,
                            agendamento=agendamento,
                            descricao=f"{agendamento.servico.nome} - {agendamento.cliente.nome}",
                            valor=agendamento.valor_cobrado,
                            data_vencimento=agendamento.data_hora_inicio.date(),
                            status=StatusLancamento.PENDENTE,
                        )
                        
                        self.stdout.write(
                            self.style.SUCCESS(
                                f'  ✅ ID: {agendamento.id} | '
                                f'{agendamento.cliente.nome} | '
                                f'R$ {agendamento.valor_cobrado}'
                            )
                        )
                        processados += 1
                    else:
                        self.stdout.write(
                            self.style.WARNING(
                                f'  ⚠️  ID: {agendamento.id} | '
                                f'{agendamento.cliente.nome} | '
                                f'SEM VALOR DEFINIDO'
                            )
                        )
                        sem_valor += 1
                
            except Exception as e:
                erros += 1
                self.stdout.write(
                    self.style.ERROR(f'  ❌ Erro ID {agendamento.id}: {str(e)}')
                )

        # Resumo
        if dry_run:
            self.stdout.write(self.style.SUCCESS(f'\n✅ [DRY-RUN] {total} agendamentos seriam processados'))
        else:
            self.stdout.write(self.style.SUCCESS(f'\n📊 RESUMO:'))
            self.stdout.write(self.style.SUCCESS(f'  ✅ Processados: {processados}'))
            if sem_valor > 0:
                self.stdout.write(self.style.WARNING(f'  ⚠️  Sem valor: {sem_valor}'))
            if erros > 0:
                self.stdout.write(self.style.ERROR(f'  ❌ Erros: {erros}'))