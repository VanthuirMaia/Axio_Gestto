from django import template
import locale

register = template.Library()

MESES_PT = {
    1: 'Janeiro', 2: 'Fevereiro', 3: 'Março', 4: 'Abril',
    5: 'Maio', 6: 'Junho', 7: 'Julho', 8: 'Agosto',
    9: 'Setembro', 10: 'Outubro', 11: 'Novembro', 12: 'Dezembro'
}

@register.filter
def mes_pt(data):
    """Retorna o mês em português"""
    if hasattr(data, 'month') and hasattr(data, 'year'):
        return f"{MESES_PT[data.month]}/{data.year}"
    return data