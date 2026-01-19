from django.shortcuts import render, get_object_or_404
from django.db.models import Prefetch
import markdown
from .models import Categoria, Artigo

def ajuda_home(request):
    """
    Página inicial da Central de Ajuda
    Lista categorias e artigos em destaque
    """
    categorias = Categoria.objects.prefetch_related(
        Prefetch('artigos', queryset=Artigo.objects.filter(publicado=True))
    ).order_by('ordem', 'nome')
    
    context = {
        'categorias': categorias,
    }
    return render(request, 'ajuda/home.html', context)

def ajuda_categoria(request, slug):
    """
    Lista artigos de uma categoria específica
    """
    categoria = get_object_or_404(Categoria, slug=slug)
    artigos = categoria.artigos.filter(publicado=True).order_by('titulo')
    
    # Breadcrumb
    breadcrumb_items = [
        {'label': 'Central de Ajuda', 'url': 'ajuda_home'},
        {'label': categoria.nome, 'url': '#'},
    ]
    
    context = {
        'categoria': categoria,
        'artigos': artigos,
        'breadcrumb_items': breadcrumb_items,
    }
    return render(request, 'ajuda/categoria.html', context)

def ajuda_artigo(request, slug):
    """
    Exibe um artigo específico
    """
    artigo = get_object_or_404(Artigo, slug=slug, publicado=True)
    
    # Converter Markdown para HTML
    conteudo_html = markdown.markdown(
        artigo.conteudo,
        extensions=['fenced_code', 'tables', 'nl2br', 'toc']
    )
    
    # Outros artigos da mesma categoria (sidebar)
    outros_artigos = Artigo.objects.filter(
        categoria=artigo.categoria, 
        publicado=True
    ).exclude(id=artigo.id).order_by('titulo')[:5]
    
    # Breadcrumb
    breadcrumb_items = [
        {'label': 'Central de Ajuda', 'url': 'ajuda_home'},
        {'label': artigo.categoria.nome, 'url': 'ajuda_categoria', 'args': [artigo.categoria.slug]},
        {'label': artigo.titulo[:30] + '...', 'url': '#'},
    ]
    
    context = {
        'artigo': artigo,
        'conteudo_html': conteudo_html,
        'outros_artigos': outros_artigos,
        'breadcrumb_items': breadcrumb_items,
    }
    return render(request, 'ajuda/artigo.html', context)
