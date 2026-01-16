"""
Lógica de Onboarding - Calcula progresso de configuração da empresa
"""
from django.urls import reverse


ONBOARDING_STEPS = [
    {
        'id': 'empresa_configurada',
        'label': 'Configurar Dados da Empresa',
        'icon': '🏢',
        'check': lambda empresa: bool(empresa.nome and empresa.telefone and empresa.endereco),
        'url_name': 'empresa_dados',
        'peso': 15
    },
    {
        'id': 'whatsapp_conectado',
        'label': 'Conectar WhatsApp',
        'icon': '💬',
        'check': lambda empresa: empresa.whatsapp_configurado,
        'url_name': 'whatsapp_dashboard',
        'peso': 30
    },
    {
        'id': 'servicos_cadastrados',
        'label': 'Cadastrar Serviços',
        'icon': '✂️',
        'check': lambda empresa: empresa.servicos.exists(),
        'url_name': 'servicos_lista',
        'peso': 20
    },
    {
        'id': 'profissionais_cadastrados',
        'label': 'Cadastrar Profissionais',
        'icon': '👤',
        'check': lambda empresa: empresa.profissionais.count() > 0,
        'url_name': 'profissionais_lista',
        'peso': 20
    },
    {
        'id': 'horarios_configurados',
        'label': 'Configurar Horários de Funcionamento',
        'icon': '🕐',
        'check': lambda empresa: empresa.horarios_funcionamento.exists(),
        'url_name': 'horarios_funcionamento',
        'peso': 15
    }
]


def calcular_progresso_onboarding(empresa):
    """
    Calcula o progresso de onboarding da empresa.
    
    Returns:
        dict: {
            'progresso': int (0-100),
            'steps_completos': int,
            'steps_total': int,
            'proximo_passo': dict ou None,
            'steps': list (todos os steps com status)
        }
    """
    steps_com_status = []
    peso_total = sum(step['peso'] for step in ONBOARDING_STEPS)
    peso_completo = 0
    proximo_passo = None
    
    for step in ONBOARDING_STEPS:
        try:
            completo = step['check'](empresa)
        except Exception:
            completo = False
        
        step_info = {
            **step,
            'completo': completo,
            'url': reverse(step['url_name'])
        }
        steps_com_status.append(step_info)
        
        if completo:
            peso_completo += step['peso']
        elif proximo_passo is None:
            # Primeiro step incompleto é o próximo
            proximo_passo = step_info
    
    progresso = int((peso_completo / peso_total) * 100)
    steps_completos = sum(1 for s in steps_com_status if s['completo'])
    
    return {
        'progresso': progresso,
        'steps_completos': steps_completos,
        'steps_total': len(ONBOARDING_STEPS),
        'proximo_passo': proximo_passo,
        'steps': steps_com_status,
        'completo': progresso == 100
    }
