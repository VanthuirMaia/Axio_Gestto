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

        # Pastas permitidas para virarem categorias (CASE INSENSITIVE)
        # APENAS documentação de usuário final
        pastas_permitidas = [
            'configuracao',
            'operacao',
            'integracao',
            'financeiro',
            'agendamentos',
            'relatorios',
        ]

        # Mapeamento de nomes amigáveis
        nomes_categorias = {
            'configuracao': 'Configurações',
            'operacao': 'Operação do Sistema',
            'integracao': 'Integrações',
            'financeiro': 'Financeiro',
            'agendamentos': 'Agendamentos',
            'relatorios': 'Relatórios',
        }

        # 1. Processar arquivos na raiz do docs (Categoria Geral)
        # DESATIVADO POR SEGURANÇA - Docs na raiz geralmente são técnicos (README, deploy, etc)
        # self.processar_pasta(docs_path, 'Geral', ordem=99)

        # 2. Processar APENAS subpastas permitidas (Recursivo 1 nível)
        ordem = 1
        for item in docs_path.iterdir():
            if item.is_dir():
                nome_lower = item.name.lower()
                
                # Se for uma pasta permitida (WHITELIST)
                # Não importa se tem MD, só importa se é permitida
                if nome_lower in pastas_permitidas:
                    
                    # Nome amigável
                    nome_cat = nomes_categorias.get(nome_lower, item.name.replace('_', ' ').title())
                    
                    self.processar_pasta(item, nome_cat, ordem=ordem)
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
        
        # Processar arquivos
        count = 0
        for arquivo in arquivos_md:
            # Ignorar arquivos de sistema
            if arquivo.name.upper() in ['README.MD', 'TODO.MD', 'REQUIREMENTS.TXT']:
                continue
                
            if self.importar_arquivo(arquivo, categoria):
                count += 1
        
        if count > 0:
            self.stdout.write(f'  - {nome_categoria}: {count} artigos importados')

    def importar_arquivo(self, arquivo_path, categoria):
        """Lê arquivo e cria artigo"""
        try:
            content = arquivo_path.read_text(encoding='utf-8')
            
            # Extrair título
            lines = content.split('\n')
            titulo = None
            
            for line in lines:
                if line.startswith('# '):
                    titulo = line.replace('# ', '').strip()
                    break
            
            if not titulo:
                titulo = arquivo_path.stem.replace('_', ' ').replace('-', ' ').title()
            
            # Limpar título do corpo
            if lines and lines[0].startswith('# '):
                content_body = '\n'.join(lines[1:]).strip()
            else:
                content_body = content

            artigo, created = Artigo.objects.update_or_create(
                slug=slugify(titulo),
                defaults={
                    'titulo': titulo,
                    'categoria': categoria,
                    'conteudo': content_body,
                    'publicado': True
                }
            )
            return True
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Erro ao importar {arquivo_path.name}: {str(e)}'))
            return False
