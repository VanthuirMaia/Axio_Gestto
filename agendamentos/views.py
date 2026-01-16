from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from django.utils import timezone
from django.db import transaction
from django.conf import settings
from dateutil import parser
from datetime import datetime, timedelta
from .models import Agendamento, DisponibilidadeProfissional
from empresas.models import Servico, Profissional, HorarioFuncionamento, DataEspecial, Empresa
from clientes.models import Cliente
from core.decorators import plano_required
import logging

logger = logging.getLogger(__name__)


# Decorator para autenticação via API key (para n8n e integrações externas)
def api_key_required(view_func):
    """
    Decorator que verifica se a requisição tem uma API key válida
    Uso: Para APIs que serão consumidas por n8n ou outras integrações
    """
    def wrapper(request, *args, **kwargs):
        api_key = request.GET.get('api_key') or request.headers.get('X-API-Key')
        gestto_api_key = getattr(settings, 'GESTTO_API_KEY', None)
        
        if not api_key or api_key != gestto_api_key:
            return JsonResponse({
                "error": "API key inválida ou não fornecida",
                "hint": "Adicione ?api_key=SUA_CHAVE ou header X-API-Key"
            }, status=401)
        
        return view_func(request, *args, **kwargs)
    
    return wrapper

STATUS_COLORS = {
    "pendente": "#facc15",       # amarelo
    "confirmado": "#3b82f6",     # azul
    "cancelado": "#ef4444",      # vermelho
    "concluido": "#22c55e",      # verde
    "nao_compareceu": "#6b7280"  # cinza
}

@login_required
def calendario_view(request):
    empresa = request.user.empresa
    if not empresa:
        return redirect('logout')
    
    mes = request.GET.get('mes', datetime.now().month)
    ano = request.GET.get('ano', datetime.now().year)
    
    agendamentos = Agendamento.objects.filter(
        empresa=empresa,
        data_hora_inicio__month=mes,
        data_hora_inicio__year=ano
    ).select_related('cliente', 'profissional', 'servico')
    
    context = {
        'empresa': empresa,
        'agendamentos': agendamentos,
        'mes': int(mes),
        'ano': int(ano),
        'servicos': empresa.servicos.filter(ativo=True),
        'profissionais': empresa.profissionais.filter(ativo=True),
    }
    return render(request, 'agendamentos/calendario.html', context)

@login_required
@require_http_methods(["GET", "POST"])
def criar_agendamento(request):

    empresa = request.user.empresa
    if not empresa:
        return redirect('logout')

    # se for GET, renderiza vazio
    clientes = empresa.clientes.filter(ativo=True)
    servicos = empresa.servicos.filter(ativo=True)
    profissionais = empresa.profissionais.filter(ativo=True)

    if request.method == 'POST':

        cliente_id = request.POST.get('cliente_id')
        servico_id = request.POST.get('servico_id')
        profissional_id = request.POST.get('profissional_id')
        raw_datetime = request.POST.get('data_hora_inicio')
        notas = request.POST.get('notas')

        try:
            cliente = Cliente.objects.get(id=cliente_id, empresa=empresa)
            servico = Servico.objects.get(id=servico_id, empresa=empresa)
            profissional = Profissional.objects.get(id=profissional_id, empresa=empresa) if profissional_id else None

            # parser e timezone
            data_hora = parser.parse(raw_datetime)
            data_hora = timezone.make_aware(data_hora, timezone.get_current_timezone())
            data_fim = data_hora + timedelta(minutes=servico.duracao_minutos)

            # 🔥 VERIFICAÇÃO DE CONFLITO COM PROTEÇÃO CONTRA RACE CONDITION
            with transaction.atomic():
                # Lock pessimista: bloqueia outros agendamentos durante a verificação
                conflito = Agendamento.objects.select_for_update().filter(
                    empresa=empresa,
                    profissional=profissional,
                    data_hora_inicio__lt=data_fim,
                    data_hora_fim__gt=data_hora,
                    status__in=['pendente', 'confirmado']
                ).exists()

                if conflito:
                    messages.error(request, "Este horário já está ocupado para este profissional.")

                    # retorna a mesma página COM TODOS OS VALORES MANTIDOS
                    return render(request, 'agendamentos/criar.html', {
                        'empresa': empresa,
                        'clientes': clientes,
                        'servicos': servicos,
                        'profissionais': profissionais,
                        'form_values': request.POST  # 🔥 magic
                    })

                # cria agendamento (dentro da transação, lock ainda ativo)
                Agendamento.objects.create(
                    empresa=empresa,
                    cliente=cliente,
                    servico=servico,
                    profissional=profissional,
                    data_hora_inicio=data_hora,
                    data_hora_fim=data_fim,
                    notas=notas,
                    valor_cobrado=servico.preco,
                    status='confirmado'
                )

            messages.success(request, "Agendamento criado com sucesso!")
            return redirect('agendamentos:calendario')

        except Exception as e:
            messages.error(request, f"Erro ao criar agendamento: {e}")

            return render(request, 'agendamentos/criar.html', {
                'empresa': empresa,
                'clientes': clientes,
                'servicos': servicos,
                'profissionais': profissionais,
                'form_values': request.POST
            })

    # GET normal
    return render(request, 'agendamentos/criar.html', {
        'empresa': empresa,
        'clientes': clientes,
        'servicos': servicos,
        'profissionais': profissionais,
        'form_values': {}
    })


def api_agendamentos(request):
    empresa = request.user.empresa
    if not empresa:
        return JsonResponse({"error": "Não autorizado"}, status=403)

    # Pegar range de datas do FullCalendar
    start_str = request.GET.get("start")
    end_str = request.GET.get("end")

    # Fallback para o método antigo (mes/ano) se não vier start/end
    if start_str and end_str:
        try:
            start_date = parser.parse(start_str).date()
            end_date = parser.parse(end_str).date()

            # Buscar agendamentos no intervalo (excluir cancelados)
            ags = Agendamento.objects.filter(
                empresa=empresa,
                data_hora_inicio__date__gte=start_date,
                data_hora_inicio__date__lt=end_date
            ).exclude(status='cancelado').select_related("cliente", "servico", "profissional")
        except:
            # Se der erro no parse, usar método antigo
            mes = request.GET.get("mes")
            ano = request.GET.get("ano")
            ags = Agendamento.objects.filter(
                empresa=empresa,
                data_hora_inicio__month=mes,
                data_hora_inicio__year=ano
            ).exclude(status='cancelado').select_related("cliente", "servico", "profissional")
    else:
        # Método antigo para compatibilidade
        mes = request.GET.get("mes")
        ano = request.GET.get("ano")
        ags = Agendamento.objects.filter(
            empresa=empresa,
            data_hora_inicio__month=mes,
            data_hora_inicio__year=ano
        ).exclude(status='cancelado').select_related("cliente", "servico", "profissional")

    # Filtro de profissionais (NOVO)
    profissionais_ids = request.GET.get("profissionais", "")
    if profissionais_ids:
        try:
            ids_list = [int(id.strip()) for id in profissionais_ids.split(',') if id.strip()]
            if ids_list:
                ags = ags.filter(profissional_id__in=ids_list)
        except ValueError:
            # Se houver erro ao converter IDs, ignora o filtro
            pass

    eventos = []

    # ------------------------------
    # 2. Montagem profissional do JSON
    # ------------------------------
    for a in ags:

        # Convertendo corretamente para America/Recife
        inicio = timezone.localtime(a.data_hora_inicio)
        fim = timezone.localtime(a.data_hora_fim)

        # Cor do status
        status_color = STATUS_COLORS.get(a.status, "#3b82f6")

        # Cor do profissional (caso você adicione no model)
        profissional_color = getattr(a.profissional, "cor_hex", None)

        # Cor final (profissional tem prioridade)
        cor_final = profissional_color if profissional_color else "#6b7280"

        eventos.append({
            "id": a.id,
            "title": f"{a.cliente.nome} – {a.servico.nome}",
            "start": inicio.isoformat(),
            "end": fim.isoformat(),

            # CORREÇÃO DEFINITIVA – sempre enviar todas as cores
            "backgroundColor": cor_final,
            "borderColor": cor_final,
            "textColor": "#ffffff",

            "status": a.status,
            "cliente": a.cliente.nome,
            "servico": a.servico.nome,
            "profissional": a.profissional.nome if a.profissional else None,
            "valor": float(a.valor_cobrado or 0),
        })


    return JsonResponse(eventos, safe=False)


@login_required
def verificar_disponibilidade(request):
    """
    Verifica se um horário está disponível para agendamento
    
    Query Parameters:
        - data: Data no formato YYYY-MM-DD
        - hora: Hora no formato HH:MM
        - servico_id: ID do serviço (obrigatório para calcular duração)
        - profissional_id: ID do profissional (opcional)
        
    Returns:
        {
            "disponivel": true/false,
            "motivo": "string explicando por que não está disponível",
            "profissionais_disponiveis": [lista de profissionais se não especificado],
            "sugestoes": [horários próximos disponíveis]
        }
    """
    empresa = request.user.empresa
    if not empresa:
        return JsonResponse({"error": "Não autorizado"}, status=403)
    
    # Parâmetros
    data_str = request.GET.get('data')  # YYYY-MM-DD
    hora_str = request.GET.get('hora')  # HH:MM
    servico_id = request.GET.get('servico_id')
    profissional_id = request.GET.get('profissional_id', None)
    
    # Validações
    if not all([data_str, hora_str, servico_id]):
        return JsonResponse({
            "error": "Parâmetros obrigatórios: data, hora, servico_id"
        }, status=400)
    
    try:
        # Parse data e hora
        data = datetime.strptime(data_str, '%Y-%m-%d').date()
        hora = datetime.strptime(hora_str, '%H:%M').time()
        
        # Buscar serviço
        servico = Servico.objects.get(id=servico_id, empresa=empresa)
        
        # Criar datetime completo
        data_hora_inicio = timezone.make_aware(
            datetime.combine(data, hora),
            timezone.get_current_timezone()
        )
        data_hora_fim = data_hora_inicio + timedelta(minutes=servico.duracao_minutos)
        
        # Verificar disponibilidade
        resultado = _verificar_disponibilidade_horario(
            empresa=empresa,
            data_hora_inicio=data_hora_inicio,
            data_hora_fim=data_hora_fim,
            servico=servico,
            profissional_id=profissional_id
        )
        
        return JsonResponse(resultado)
        
    except Servico.DoesNotExist:
        return JsonResponse({"error": "Serviço não encontrado"}, status=404)
    except ValueError as e:
        return JsonResponse({"error": f"Formato inválido: {str(e)}"}, status=400)
    except Exception as e:
        logger.error(f"Erro ao verificar disponibilidade: {e}")
        return JsonResponse({"error": "Erro interno"}, status=500)


@login_required
def listar_horarios_disponiveis(request):
    """
    Lista todos os horários disponíveis para um dia específico
    
    Query Parameters:
        - data: Data no formato YYYY-MM-DD
        - servico_id: ID do serviço (obrigatório)
        - profissional_id: ID do profissional (opcional)
        - intervalo: Intervalo entre horários em minutos (padrão: 30)
        
    Returns:
        {
            "data": "2026-01-17",
            "horarios_disponiveis": [
                {
                    "hora": "09:00",
                    "disponivel": true,
                    "profissionais": [{"id": 1, "nome": "João"}]
                },
                ...
            ],
            "total_disponiveis": 10
        }
    """
    empresa = request.user.empresa
    if not empresa:
        return JsonResponse({"error": "Não autorizado"}, status=403)
    
    # Parâmetros
    data_str = request.GET.get('data')  # YYYY-MM-DD
    servico_id = request.GET.get('servico_id')
    profissional_id = request.GET.get('profissional_id', None)
    intervalo = int(request.GET.get('intervalo', 30))  # minutos
    
    # Validações
    if not all([data_str, servico_id]):
        return JsonResponse({
            "error": "Parâmetros obrigatórios: data, servico_id"
        }, status=400)


@csrf_exempt
@api_key_required
def listar_horarios_disponiveis(request):
    """
    Lista todos os horários disponíveis para um dia específico
    
    Query Parameters:
        - instance: Nome da instância WhatsApp (identifica a empresa)
        - data: Data no formato YYYY-MM-DD
        - servico_id: ID do serviço (opcional - se não informado, usa duração padrão de 60min)
        - profissional_id: ID do profissional (opcional)
        - intervalo: Intervalo entre horários em minutos (padrão: 30)
        - api_key: Chave de API (obrigatório)
        
    Returns:
        {
            "data": "2026-01-17",
            "empresa": "Nome da Empresa",
            "horarios_disponiveis": [
                {
                    "hora": "09:00",
                    "disponivel": true,
                    "profissionais": [{"id": 1, "nome": "João"}]
                },
                ...
            ],
            "total_disponiveis": 10
        }
    """
    # Parâmetros (aceita tanto em query string quanto em headers)
    instance_name = request.GET.get('instance') or request.headers.get('instance') or request.headers.get('Instance')
    data_str = request.GET.get('data') or request.headers.get('data') or request.headers.get('Data')
    servico_id = request.GET.get('servico_id') or request.headers.get('servico_id')
    profissional_id = request.GET.get('profissional_id') or request.headers.get('profissional_id')
    
    try:
        intervalo = int(request.GET.get('intervalo', 30) or request.headers.get('intervalo', 30))
    except (ValueError, TypeError):
        intervalo = 30
    
    # Validações
    if not all([instance_name, data_str]):
        return JsonResponse({
            "error": "Parâmetros obrigatórios: instance, data",
            "hint": "Envie via query string (?instance=X&data=Y) ou headers (Instance: X, Data: Y)",
            "recebido": {
                "instance": instance_name,
                "data": data_str
            }
        }, status=400)
    
    try:
        # Parse data
        data = datetime.strptime(data_str, '%Y-%m-%d').date()
        
        # Buscar empresa pelo instance_name
        from empresas.models import ConfiguracaoWhatsApp
        config = ConfiguracaoWhatsApp.objects.select_related('empresa').get(instance_name=instance_name)
        empresa = config.empresa
        
        # Buscar serviço (se fornecido) ou usar duração padrão
        duracao_minutos = 60  # Padrão
        if servico_id:
            servico = Servico.objects.get(id=servico_id, empresa=empresa)
            duracao_minutos = servico.duracao_minutos
        else:
            # Usar primeiro serviço ativo como referência ou duração padrão
            servico_padrao = empresa.servicos.filter(ativo=True).first()
            if servico_padrao:
                duracao_minutos = servico_padrao.duracao_minutos
        
        # Buscar horário de funcionamento
        dia_semana = data.weekday()
        horario_func = HorarioFuncionamento.objects.filter(
            empresa=empresa,
            dia_semana=dia_semana,
            ativo=True
        ).first()
        
        if not horario_func:
            return JsonResponse({
                "data": data_str,
                "horarios_disponiveis": [],
                "total_disponiveis": 0,
                "motivo": "Empresa fechada neste dia"
            })
        
        # Verificar se é feriado
        data_especial = DataEspecial.objects.filter(
            empresa=empresa,
            data=data,
            tipo='feriado'
        ).first()
        
        if data_especial:
            return JsonResponse({
                "data": data_str,
                "horarios_disponiveis": [],
                "total_disponiveis": 0,
                "motivo": f"Fechado - {data_especial.descricao}"
            })
        
        # Gerar lista de horários
        horarios_disponiveis = []
        hora_atual = datetime.combine(data, horario_func.hora_abertura)
        hora_fim_expediente = datetime.combine(data, horario_func.hora_fechamento)
        
        while hora_atual < hora_fim_expediente:
            # Verificar se o serviço cabe neste horário
            hora_fim_servico = hora_atual + timedelta(minutes=duracao_minutos)
            
            if hora_fim_servico.time() <= horario_func.hora_fechamento:
                # Converter para timezone aware
                data_hora_inicio = timezone.make_aware(hora_atual, timezone.get_current_timezone())
                data_hora_fim = timezone.make_aware(hora_fim_servico, timezone.get_current_timezone())
                
                # Verificar disponibilidade
                resultado = _verificar_disponibilidade_horario(
                    empresa=empresa,
                    data_hora_inicio=data_hora_inicio,
                    data_hora_fim=data_hora_fim,
                    servico=None,  # Não precisa do objeto servico completo
                    profissional_id=profissional_id
                )
                
                horarios_disponiveis.append({
                    "hora": hora_atual.strftime("%H:%M"),
                    "disponivel": resultado['disponivel'],
                    "profissionais": resultado['profissionais_disponiveis'] if resultado['disponivel'] else [],
                    "motivo": resultado['motivo'] if not resultado['disponivel'] else ""
                })
            
            # Próximo horário
            hora_atual += timedelta(minutes=intervalo)
        
        # Contar disponíveis
        total_disponiveis = sum(1 for h in horarios_disponiveis if h['disponivel'])
        
        return JsonResponse({
            "data": data_str,
            "empresa": empresa.nome,
            "horarios_disponiveis": horarios_disponiveis,
            "total_disponiveis": total_disponiveis,
            "horario_funcionamento": {
                "abertura": horario_func.hora_abertura.strftime("%H:%M"),
                "fechamento": horario_func.hora_fechamento.strftime("%H:%M")
            }
        })
        
    except ConfiguracaoWhatsApp.DoesNotExist:
        return JsonResponse({"error": "Instância WhatsApp não encontrada"}, status=404)
    except Empresa.DoesNotExist:
        return JsonResponse({"error": "Empresa não encontrada"}, status=404)
    except Servico.DoesNotExist:
        return JsonResponse({"error": "Serviço não encontrado"}, status=404)
    except ValueError as e:
        return JsonResponse({"error": f"Formato inválido: {str(e)}"}, status=400)
    except Exception as e:
        logger.error(f"Erro ao listar horários disponíveis: {e}")
        return JsonResponse({"error": "Erro interno"}, status=500)




@login_required
def editar_agendamento(request, id):
    empresa = request.user.empresa
    agendamento = get_object_or_404(Agendamento, id=id, empresa=empresa)
    
    if request.method == 'POST':
        agendamento.status = request.POST.get('status', agendamento.status)
        agendamento.notas = request.POST.get('notas', agendamento.notas)
        agendamento.save()
        messages.success(request, 'Agendamento atualizado!')
        return redirect('agendamentos:calendario')
    
    context = {
        'agendamento': agendamento,
        'empresa': empresa,
    }
    return render(request, 'agendamentos/editar.html', context)

@login_required
def deletar_agendamento(request, id):
    empresa = request.user.empresa
    agendamento = get_object_or_404(Agendamento, id=id, empresa=empresa)

    if request.method == 'POST':
        agendamento.delete()
        messages.success(request, 'Agendamento deletado!')

    return redirect('agendamentos:calendario')


# ============================================
# VIEWS DE AGENDAMENTOS RECORRENTES
# ============================================

@login_required
@plano_required(feature_flag='permite_recorrencias', feature_name='Agendamentos Recorrentes')
@login_required
def listar_recorrencias(request):
    """Lista todas as recorrências da empresa"""
    from .models import AgendamentoRecorrente

    empresa = request.user.empresa
    if not empresa:
        return redirect('logout')

    recorrencias = AgendamentoRecorrente.objects.filter(
        empresa=empresa
    ).select_related('cliente', 'servico', 'profissional').order_by('-criado_em')

    context = {
        'empresa': empresa,
        'recorrencias': recorrencias,
    }
    return render(request, 'agendamentos/recorrencias/listar.html', context)


@login_required
@plano_required(feature_flag='permite_recorrencias', feature_name='Agendamentos Recorrentes')
@require_http_methods(["GET", "POST"])
def criar_recorrencia(request):
    """Cria nova recorrência"""
    from .models import AgendamentoRecorrente
    import json

    empresa = request.user.empresa
    if not empresa:
        return redirect('logout')

    clientes = empresa.clientes.filter(ativo=True)
    servicos = empresa.servicos.filter(ativo=True)
    profissionais = empresa.profissionais.filter(ativo=True)

    if request.method == 'POST':
        try:
            cliente_id = request.POST.get('cliente_id')
            servico_id = request.POST.get('servico_id')
            profissional_id = request.POST.get('profissional_id')
            frequencia = request.POST.get('frequencia')
            hora_inicio = request.POST.get('hora_inicio')
            data_inicio = request.POST.get('data_inicio')
            data_fim = request.POST.get('data_fim') or None

            # Validações
            cliente = Cliente.objects.get(id=cliente_id, empresa=empresa)
            servico = Servico.objects.get(id=servico_id, empresa=empresa)
            profissional = Profissional.objects.get(id=profissional_id, empresa=empresa) if profissional_id else None

            # Processar dias da semana (para frequência semanal)
            dias_semana = []
            if frequencia == 'semanal':
                dias_semana = request.POST.getlist('dias_semana')
                dias_semana = [int(d) for d in dias_semana if d.isdigit()]

                if not dias_semana:
                    messages.error(request, 'Para recorrência semanal, selecione pelo menos um dia da semana.')
                    return render(request, 'agendamentos/recorrencias/criar.html', {
                        'empresa': empresa,
                        'clientes': clientes,
                        'servicos': servicos,
                        'profissionais': profissionais,
                        'form_values': request.POST
                    })

            # Processar dia do mês (para frequência mensal)
            dia_mes = None
            if frequencia == 'mensal':
                dia_mes = request.POST.get('dia_mes')
                if dia_mes:
                    dia_mes = int(dia_mes)
                    if not 1 <= dia_mes <= 31:
                        messages.error(request, 'Dia do mês deve estar entre 1 e 31.')
                        return render(request, 'agendamentos/recorrencias/criar.html', {
                            'empresa': empresa,
                            'clientes': clientes,
                            'servicos': servicos,
                            'profissionais': profissionais,
                            'form_values': request.POST
                        })
                else:
                    messages.error(request, 'Para recorrência mensal, informe o dia do mês.')
                    return render(request, 'agendamentos/recorrencias/criar.html', {
                        'empresa': empresa,
                        'clientes': clientes,
                        'servicos': servicos,
                        'profissionais': profissionais,
                        'form_values': request.POST
                    })

            # Converter strings para objetos date/time
            from datetime import datetime, time as dt_time
            
            # Converter hora_inicio (string "HH:MM" para objeto time)
            hora_obj = datetime.strptime(hora_inicio, '%H:%M').time()
            
            # Converter data_inicio (string "YYYY-MM-DD" para objeto date)
            data_inicio_obj = datetime.strptime(data_inicio, '%Y-%m-%d').date()
            
            # Converter data_fim se fornecida
            data_fim_obj = None
            if data_fim:
                data_fim_obj = datetime.strptime(data_fim, '%Y-%m-%d').date()

            # Criar recorrência
            recorrencia = AgendamentoRecorrente.objects.create(
                empresa=empresa,
                cliente=cliente,
                servico=servico,
                profissional=profissional,
                frequencia=frequencia,
                dias_semana=dias_semana,
                dia_mes=dia_mes,
                hora_inicio=hora_obj,
                data_inicio=data_inicio_obj,
                data_fim=data_fim_obj,
                criado_por=request.user,
                ativo=True
            )

            # Gerar agendamentos imediatamente
            from .utils_recorrencia import gerar_agendamentos_recorrencia
            agendamentos_criados = gerar_agendamentos_recorrencia(recorrencia, dias_futuros=60)

            messages.success(
                request,
                f'Recorrência criada com sucesso! {recorrencia.get_descricao_frequencia()} '
                f'({agendamentos_criados} agendamentos gerados)'
            )
            return redirect('agendamentos:listar_recorrencias')

        except Exception as e:
            messages.error(request, f'Erro ao criar recorrência: {e}')
            return render(request, 'agendamentos/recorrencias/criar.html', {
                'empresa': empresa,
                'clientes': clientes,
                'servicos': servicos,
                'profissionais': profissionais,
                'form_values': request.POST
            })

    # GET
    context = {
        'empresa': empresa,
        'clientes': clientes,
        'servicos': servicos,
        'profissionais': profissionais,
        'form_values': {}
    }
    return render(request, 'agendamentos/recorrencias/criar.html', context)


@login_required
@plano_required(feature_flag='permite_recorrencias', feature_name='Agendamentos Recorrentes')
@require_http_methods(["POST"])
def deletar_recorrencia(request, id):
    """Deleta uma recorrência"""
    from .models import AgendamentoRecorrente

    empresa = request.user.empresa
    recorrencia = get_object_or_404(AgendamentoRecorrente, id=id, empresa=empresa)

    recorrencia.delete()
    messages.success(request, 'Recorrência removida com sucesso!')

    return redirect('agendamentos:listar_recorrencias')


@login_required
@plano_required(feature_flag='permite_recorrencias', feature_name='Agendamentos Recorrentes')
@require_http_methods(["POST"])
def ativar_desativar_recorrencia(request, id):
    """Ativa ou desativa uma recorrência"""
    from .models import AgendamentoRecorrente

    empresa = request.user.empresa
    recorrencia = get_object_or_404(AgendamentoRecorrente, id=id, empresa=empresa)

    recorrencia.ativo = not recorrencia.ativo
    recorrencia.save()

    status = 'ativada' if recorrencia.ativo else 'desativada'
    messages.success(request, f'Recorrência {status} com sucesso!')

    return redirect('agendamentos:listar_recorrencias')
# Funções auxiliares para verificação de disponibilidade

def _verificar_disponibilidade_horario(empresa, data_hora_inicio, data_hora_fim, servico, profissional_id=None):
    '''Lógica principal de verificação de disponibilidade'''
    dia_semana = data_hora_inicio.weekday()  # 0=Segunda, 6=Domingo
    
    # 1. Verificar se é data especial (feriado)
    data_especial = DataEspecial.objects.filter(
        empresa=empresa,
        data=data_hora_inicio.date(),
        tipo='feriado'
    ).first()
    
    if data_especial:
        return {
            'disponivel': False,
            'motivo': f'Fechado - {data_especial.descricao}',
            'profissionais_disponiveis': [],
            'sugestoes': _gerar_sugestoes_horarios(empresa, data_hora_inicio, servico, profissional_id)
        }
    
    # 2. Verificar horário de funcionamento da empresa
    horario_func = HorarioFuncionamento.objects.filter(
        empresa=empresa,
        dia_semana=dia_semana,
        ativo=True
    ).first()
    
    if not horario_func:
        return {
            'disponivel': False,
            'motivo': 'Empresa fechada neste dia',
            'profissionais_disponiveis': [],
            'sugestoes': _gerar_sugestoes_horarios(empresa, data_hora_inicio, servico, profissional_id)
        }
    
    # Verificar se horário está dentro do expediente
    hora_inicio = data_hora_inicio.time()
    hora_fim = data_hora_fim.time()
    
    if hora_inicio < horario_func.hora_abertura or hora_fim > horario_func.hora_fechamento:
        # Formatar horas fora da f-string (f-strings não permitem backslash)
        hora_abre = horario_func.hora_abertura.strftime("%H:%M")
        hora_fecha = horario_func.hora_fechamento.strftime("%H:%M")
        
        return {
            'disponivel': False,
            'motivo': f'Fora do horário de funcionamento ({hora_abre} - {hora_fecha})',
            'profissionais_disponiveis': [],
            'sugestoes': _gerar_sugestoes_horarios(empresa, data_hora_inicio, servico, profissional_id)
        }
    
    # 3. Verificar disponibilidade de profissionais
    if profissional_id:
        # Profissional específico
        try:
            profissional = Profissional.objects.get(id=profissional_id, empresa=empresa)
            disponivel = _profissional_disponivel(profissional, data_hora_inicio, data_hora_fim, dia_semana)
            
            if disponivel:
                return {
                    'disponivel': True,
                    'motivo': '',
                    'profissionais_disponiveis': [{
                        'id': profissional.id,
                        'nome': profissional.nome
                    }],
                    'sugestoes': []
                }
            else:
                return {
                    'disponivel': False,
                    'motivo': f'{profissional.nome} não está disponível neste horário',
                    'profissionais_disponiveis': [],
                    'sugestoes': _gerar_sugestoes_horarios(empresa, data_hora_inicio, servico, profissional_id)
                }
        except Profissional.DoesNotExist:
            return {
                'disponivel': False,
                'motivo': 'Profissional não encontrado',
                'profissionais_disponiveis': [],
                'sugestoes': []
            }
    else:
        # Qualquer profissional disponível
        profissionais = Profissional.objects.filter(empresa=empresa, ativo=True)
        profissionais_disponiveis = []
        
        for prof in profissionais:
            if _profissional_disponivel(prof, data_hora_inicio, data_hora_fim, dia_semana):
                profissionais_disponiveis.append({
                    'id': prof.id,
                    'nome': prof.nome
                })
        
        if profissionais_disponiveis:
            return {
                'disponivel': True,
                'motivo': '',
                'profissionais_disponiveis': profissionais_disponiveis,
                'sugestoes': []
            }
        else:
            return {
                'disponivel': False,
                'motivo': 'Nenhum profissional disponível neste horário',
                'profissionais_disponiveis': [],
                'sugestoes': _gerar_sugestoes_horarios(empresa, data_hora_inicio, servico, profissional_id)
            }


def _profissional_disponivel(profissional, data_hora_inicio, data_hora_fim, dia_semana):
    '''Verifica se profissional específico está disponível'''
    # 1. Verificar disponibilidade cadastrada
    disponibilidade = DisponibilidadeProfissional.objects.filter(
        profissional=profissional,
        dia_semana=dia_semana,
        ativo=True
    ).first()
    
    if disponibilidade:
        hora_inicio = data_hora_inicio.time()
        hora_fim = data_hora_fim.time()
        
        # Verificar se está dentro do horário de disponibilidade
        if hora_inicio < disponibilidade.hora_inicio or hora_fim > disponibilidade.hora_fim:
            return False
    
    # 2. Verificar conflitos com agendamentos existentes
    conflito = Agendamento.objects.filter(
        profissional=profissional,
        data_hora_inicio__lt=data_hora_fim,
        data_hora_fim__gt=data_hora_inicio,
        status__in=['pendente', 'confirmado']
    ).exists()
    
    return not conflito


def _gerar_sugestoes_horarios(empresa, data_hora_solicitada, servico, profissional_id=None):
    '''Gera sugestões de horários próximos disponíveis'''
    sugestoes = []
    data_base = data_hora_solicitada.date()
    
    # Tentar próximas 3 horas no mesmo dia
    for i in range(1, 4):
        nova_hora = data_hora_solicitada + timedelta(hours=i)
        
        if nova_hora.date() == data_base:  # Ainda no mesmo dia
            resultado = _verificar_disponibilidade_horario(
                empresa=empresa,
                data_hora_inicio=nova_hora,
                data_hora_fim=nova_hora + timedelta(minutes=servico.duracao_minutos),
                servico=servico,
                profissional_id=profissional_id
            )
            
            if resultado['disponivel']:
                sugestoes.append({
                    'data': nova_hora.strftime('%Y-%m-%d'),
                    'hora': nova_hora.strftime('%H:%M'),
                    'profissionais': resultado['profissionais_disponiveis']
                })
                
                if len(sugestoes) >= 3:
                    break
    
    return sugestoes
