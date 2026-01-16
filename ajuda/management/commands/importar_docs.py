import os
import re
from pathlib import Path
from django.core.management.base import BaseCommand
from django.utils.text import slugify
from django.conf import settings
from ajuda.models import Categoria, Artigo

class Command(BaseCommand):
    help = 'Importa documentação da pasta docs/ para a Central de Ajuda'

    def handle(self, *args, **options):
        # Caminho base (raiz do projeto / docs)
        docs_path = Path(settings.BASE_DIR) / 'docs'
        
        if not docs_path.exists():
            self.stdout.write(self.style.ERROR(f'Pasta docs não encontrada em {docs_path}'))
            return

        # Pastas permitidas para virarem categorias
        pastas_permitidas = [
            'configuracao',
            'operacao',
            'integracao',
            'financeiro',
            'agendamentos',
            'relatorios'
        ]

        # Mapeamento de nomes amigáveis para categorias
        nomes_categorias = {
            'configuracao': 'Configurações',
            'operacao': 'Operação do Sistema',
            'integracao': 'Integrações',
            'financeiro': 'Financeiro',
            'agendamentos': 'Agendamentos',
            'relatorios': 'Relatórios',
        }
        
        # Ícones para cada categoria
        icones_categorias = {
            'configuracao': 'bi-gear',
            'operacao': 'bi-display',
            'integracao': 'bi-puzzle',
            'financeiro': 'bi-cash-coin',
            'agendamentos': 'bi-calendar-check',
            'relatorios': 'bi-bar-chart',
        }

        # 1. Processar arquivos na raiz do docs (Categoria Geral)
        self.processar_pasta(docs_path, 'Geral', ordem=99)

        # 2. Processar subpastas permitidas
        ordem = 1
        for item in docs_path.iterdir():
            if item.is_dir() and item.name in pastas_permitidas:
                nome_cat = nomes_categorias.get(item.name, item.name.title())
                icone_cat = icones_categorias.get(item.name, 'bi-folder')
                self.processar_pasta(item, nome_cat, ordem=ordem, icone=icone_cat)
                ordem += 1

        self.stdout.write(self.style.SUCCESS('Importação concluída com sucesso!'))

    def processar_pasta(self, path, nome_categoria, ordem=0, icone='bi-folder'):
        """Processa uma pasta criando categoria e importando arquivos"""
        
        # Filtrar apenas arquivos .md
        arquivos_md = list(path.glob('*.md'))
        if not arquivos_md:
            return

        # Criar ou atualizar categoria
        categoria, created = Categoria.objects.get_or_create(
            slug=slugify(nome_categoria),
            defaults={
                'nome': nome_categoria,
                'ordem': ordem,
                'icone': icone
            }
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS(f'Categoria criada: {nome_categoria}'))
        else:
            # Atualizar ordem se mudou
            if categoria.ordem != ordem:
                categoria.ordem = ordem
                categoria.save()

        # Processar arquivos
        for arquivo in arquivos_md:
            # Ignorar arquivos de sistema ou controle
            if arquivo.name.upper() in ['README.MD', 'TODO.MD']:
                continue
                
            self.importar_arquivo(arquivo, categoria)

    def importar_arquivo(self, arquivo_path, categoria):
        """Lê arquivo e cria artigo"""
        try:
            content = arquivo_path.read_text(encoding='utf-8')
            
            # Extrair título (Primeira linha com # ou nome do arquivo)
            lines = content.split('\n')
            titulo = None
            
            # Tentar pegar do primeiro H1
            for line in lines:
                if line.startswith('# '):
                    titulo = line.replace('# ', '').strip()
                    break
            
            # Se não achou, usa o nome do arquivo formatado
            if not titulo:
                titulo = arquivo_path.stem.replace('_', ' ').replace('-', ' ').title()
            
            # Remover o título do conteúdo se ele estiver na primeira linha (para não duplicar)
            if lines and lines[0].startswith('# '):
                content_body = '\n'.join(lines[1:]).strip()
            else:
                content_body = content

            # Criar ou atualizar artigo
            artigo, created = Artigo.objects.update_or_create(
                slug=slugify(titulo),
                defaults={
                    'titulo': titulo,
                    'categoria': categoria,
                    'conteudo': content_body,
                    'publicado': True
                }
            )
            
            action = 'Criado' if created else 'Atualizado'
            self.stdout.write(f'  - {action}: {titulo}')
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Erro ao importar {arquivo_path.name}: {str(e)}'))
