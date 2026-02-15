from django.contrib import admin
from .models import PageView, UserEvent, Waitlist


@admin.register(PageView)
class PageViewAdmin(admin.ModelAdmin):
    list_display = ['page_url', 'ip_address', 'timestamp', 'session_id']
    list_filter = ['timestamp', 'page_url']
    search_fields = ['page_url', 'ip_address', 'session_id']
    readonly_fields = ['page_url', 'referrer', 'user_agent', 'ip_address', 'timestamp', 'session_id']
    date_hierarchy = 'timestamp'
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False


@admin.register(UserEvent)
class UserEventAdmin(admin.ModelAdmin):
    list_display = ['event_type', 'page_url', 'timestamp', 'session_id', 'get_event_summary']
    list_filter = ['event_type', 'timestamp']
    search_fields = ['page_url', 'session_id', 'event_data']
    readonly_fields = ['event_type', 'event_data', 'page_url', 'timestamp', 'session_id', 'ip_address']
    date_hierarchy = 'timestamp'
    
    def get_event_summary(self, obj):
        """Mostra resumo dos dados do evento"""
        if obj.event_data:
            if 'section' in obj.event_data:
                return f"Seção: {obj.event_data['section']}"
            elif 'cta_name' in obj.event_data:
                return f"CTA: {obj.event_data['cta_name']}"
            elif 'depth' in obj.event_data:
                return f"Profundidade: {obj.event_data['depth']}%"
        return "-"
    get_event_summary.short_description = "Resumo"
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False


@admin.register(Waitlist)
class WaitlistAdmin(admin.ModelAdmin):
    list_display = ['id', 'nome', 'email']
    
    def has_add_permission(self, request):
        return False
