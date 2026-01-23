from django.db.models import Count, Avg, Q
from django.utils import timezone
from datetime import timedelta
from .models import PageView, UserEvent


def get_analytics_summary(days=7):
    """Retorna resumo de analytics dos últimos N dias"""
    start_date = timezone.now() - timedelta(days=days)
    
    # Total de visualizações
    total_views = PageView.objects.filter(timestamp__gte=start_date).count()
    
    # Sessões únicas
    unique_sessions = PageView.objects.filter(
        timestamp__gte=start_date
    ).values('session_id').distinct().count()
    
    # Páginas mais visitadas
    top_pages = list(PageView.objects.filter(
        timestamp__gte=start_date
    ).values('page_url').annotate(
        views=Count('id')
    ).order_by('-views')[:5])
    
    # Cliques em CTAs
    cta_clicks = UserEvent.objects.filter(
        event_type='click_cta',
        timestamp__gte=start_date
    ).count()
    
    # Profundidade média de scroll
    scroll_events = UserEvent.objects.filter(
        event_type='scroll_depth',
        timestamp__gte=start_date
    )
    avg_scroll = 0
    if scroll_events.exists():
        depths = [e.event_data.get('depth', 0) for e in scroll_events]
        avg_scroll = sum(depths) / len(depths) if depths else 0
    
    # FAQs mais abertos
    top_faqs = list(UserEvent.objects.filter(
        event_type='faq_open',
        timestamp__gte=start_date
    ).values('event_data__question').annotate(
        opens=Count('id')
    ).order_by('-opens')[:5])
    
    # Seções mais visualizadas
    top_sections = list(UserEvent.objects.filter(
        event_type='section_view',
        timestamp__gte=start_date
    ).values('event_data__section').annotate(
        views=Count('id')
    ).order_by('-views'))
    
    # Planos mais clicados
    plan_clicks = list(UserEvent.objects.filter(
        event_type='plan_click',
        timestamp__gte=start_date
    ).values('event_data__plan').annotate(
        clicks=Count('id')
    ).order_by('-clicks'))
    
    return {
        'period_days': days,
        'total_views': total_views,
        'unique_sessions': unique_sessions,
        'avg_views_per_session': round(total_views / unique_sessions, 2) if unique_sessions > 0 else 0,
        'top_pages': top_pages,
        'cta_clicks': cta_clicks,
        'avg_scroll_depth': round(avg_scroll, 2),
        'top_faqs': top_faqs,
        'top_sections': top_sections,
        'plan_clicks': plan_clicks,
        'whatsapp_clicks': UserEvent.objects.filter(
            event_type='whatsapp_click',
            timestamp__gte=start_date
        ).count(),
    }


def get_conversion_rate(days=7):
    """Calcula taxa de conversão (cliques em CTA / visualizações)"""
    start_date = timezone.now() - timedelta(days=days)
    
    total_views = PageView.objects.filter(timestamp__gte=start_date).count()
    cta_clicks = UserEvent.objects.filter(
        event_type='click_cta',
        timestamp__gte=start_date
    ).count()
    
    if total_views == 0:
        return 0
    
    return round((cta_clicks / total_views) * 100, 2)


def get_hourly_traffic(days=7):
    """Retorna distribuição de tráfego por hora do dia"""
    start_date = timezone.now() - timedelta(days=days)
    
    views = PageView.objects.filter(timestamp__gte=start_date)
    
    hourly_data = {}
    for hour in range(24):
        hourly_data[hour] = views.filter(timestamp__hour=hour).count()
    
    return hourly_data


def get_daily_traffic(days=30):
    """Retorna tráfego diário dos últimos N dias"""
    start_date = timezone.now() - timedelta(days=days)
    
    daily_data = {}
    for i in range(days):
        date = start_date + timedelta(days=i)
        count = PageView.objects.filter(
            timestamp__date=date.date()
        ).count()
        daily_data[date.strftime('%Y-%m-%d')] = count
    
    return daily_data
