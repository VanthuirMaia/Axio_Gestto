"""
Comando Django para limpar logs antigos de analytics
Executar periodicamente via cron ou Celery Beat
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from landing.models import PageView, UserEvent


class Command(BaseCommand):
    help = 'Limpa logs de analytics antigos para evitar crescimento excessivo do banco'

    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=int,
            default=90,
            help='Manter logs dos últimos N dias (padrão: 90)'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Apenas mostrar o que seria deletado, sem deletar'
        )

    def handle(self, *args, **options):
        days = options['days']
        dry_run = options['dry_run']
        
        # Calcular data limite
        data_limite = timezone.now() - timedelta(days=days)
        
        # Contar registros a serem deletados
        pageviews_count = PageView.objects.filter(timestamp__lt=data_limite).count()
        events_count = UserEvent.objects.filter(timestamp__lt=data_limite).count()
        
        total = pageviews_count + events_count
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING(f'[DRY RUN] Seriam deletados:')
            )
            self.stdout.write(f'  - {pageviews_count} pageviews')
            self.stdout.write(f'  - {events_count} eventos')
            self.stdout.write(f'  - Total: {total} registros')
            self.stdout.write(f'  - Mais antigos que: {data_limite.strftime("%d/%m/%Y")}')
            return
        
        # Deletar registros antigos
        self.stdout.write(f'Deletando logs anteriores a {data_limite.strftime("%d/%m/%Y")}...')
        
        pageviews_deleted = PageView.objects.filter(timestamp__lt=data_limite).delete()
        events_deleted = UserEvent.objects.filter(timestamp__lt=data_limite).delete()
        
        self.stdout.write(
            self.style.SUCCESS(f'✓ Deletados {pageviews_deleted[0]} pageviews')
        )
        self.stdout.write(
            self.style.SUCCESS(f'✓ Deletados {events_deleted[0]} eventos')
        )
        self.stdout.write(
            self.style.SUCCESS(f'✓ Total: {pageviews_deleted[0] + events_deleted[0]} registros removidos')
        )
