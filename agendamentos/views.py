from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from datetime import datetime, timedelta
from .models import Agendamento, DisponibilidadeProfissional
from empresas.models import Servico, Profissional
from clientes.models import Cliente

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
    
    if request.method == 'POST':
        cliente_id = request.POST.get('cliente_id')
        servico_id = request.POST.get('servico_id')
        profissional_id = request.POST.get('profissional_id')
        data_hora_inicio = request.POST.get('data_hora_inicio')
        notas = request.POST.get('notas', '')
        
        try:
            cliente = Cliente.objects.get(id=cliente_id, empresa=empresa)
            servico = Servico.objects.get(id=servico_id, empresa=empresa)
            profissional = Profissional.objects.get(id=profissional_id, empresa=empresa) if profissional_id else None
            
            data_hora = datetime.fromisoformat(data_hora_inicio)
            duracao = timedelta(minutes=servico.duracao_minutos)
            data_hora_fim = data_hora + duracao
            
            agendamento = Agendamento.objects.create(
                empresa=empresa,
                cliente=cliente,
                servico=servico,
                profissional=profissional,
                data_hora_inicio=data_hora,
                data_hora_fim=data_hora_fim,
                notas=notas,
                valor_cobrado=servico.preco,
                status='confirmado'
            )
            
            messages.success(request, f'Agendamento criado com sucesso!')
            return redirect('calendario')
        except Exception as e:
            messages.error(request, f'Erro ao criar agendamento: {str(e)}')
    
    context = {
        'empresa': empresa,
        'clientes': empresa.clientes.filter(ativo=True),
        'servicos': empresa.servicos.filter(ativo=True),
        'profissionais': empresa.profissionais.filter(ativo=True),
    }
    return render(request, 'agendamentos/criar.html', context)

@login_required
def api_agendamentos(request):
    empresa = request.user.empresa
    if not empresa:
        return JsonResponse({'error': 'Nao autorizado'}, status=403)

    mes = int(request.GET.get('mes', datetime.now().month))
    ano = int(request.GET.get('ano', datetime.now().year))

    agendamentos = Agendamento.objects.filter(
        empresa=empresa,
        data_hora_inicio__month=mes,
        data_hora_inicio__year=ano
    ).select_related('cliente', 'servico', 'profissional')

    eventos = []

    for ag in agendamentos:
        eventos.append({
            "id": ag.id,
            "title": f"{ag.cliente.nome} – {ag.servico.nome}",
            "start": ag.data_hora_inicio.strftime("%Y-%m-%dT%H:%M:%S"),
            "end": ag.data_hora_fim.strftime("%Y-%m-%dT%H:%M:%S"),
            "status": ag.status,
            "cliente": ag.cliente.nome,
            "servico": ag.servico.nome,
            "profissional": ag.profissional.nome if ag.profissional else None,
            "valor": float(ag.valor_cobrado or 0),
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
        return redirect('calendario')
    
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
    
    return redirect('calendario')
