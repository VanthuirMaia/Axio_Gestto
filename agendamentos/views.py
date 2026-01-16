from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from django.utils import timezone
from django.db import transaction
from dateutil import parser
from datetime import datetime, timedelta
from .models import Agendamento, DisponibilidadeProfissional
from empresas.models import Servico, Profissional
from clientes.models import Cliente
from core.decorators import plano_required

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

            # Buscar agendamentos no intervalo
            ags = Agendamento.objects.filter(
                empresa=empresa,
                data_hora_inicio__date__gte=start_date,
                data_hora_inicio__date__lt=end_date
            ).select_related("cliente", "servico", "profissional")
        except:
            # Se der erro no parse, usar método antigo
            mes = request.GET.get("mes")
            ano = request.GET.get("ano")
            ags = Agendamento.objects.filter(
                empresa=empresa,
                data_hora_inicio__month=mes,
                data_hora_inicio__year=ano
            ).select_related("cliente", "servico", "profissional")
    else:
        # Método antigo para compatibilidade
        mes = request.GET.get("mes")
        ano = request.GET.get("ano")
        ags = Agendamento.objects.filter(
            empresa=empresa,
            data_hora_inicio__month=mes,
            data_hora_inicio__year=ano
        ).select_related("cliente", "servico", "profissional")

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

            # Criar recorrência
            recorrencia = AgendamentoRecorrente.objects.create(
                empresa=empresa,
                cliente=cliente,
                servico=servico,
                profissional=profissional,
                frequencia=frequencia,
                dias_semana=dias_semana,
                dia_mes=dia_mes,
                hora_inicio=hora_inicio,
                data_inicio=data_inicio,
                data_fim=data_fim,
                criado_por=request.user,
                ativo=True
            )

            messages.success(
                request,
                f'Recorrência criada com sucesso! {recorrencia.get_descricao_frequencia()}'
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
