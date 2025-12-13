from clientes.services.metricas_clientes import listar_clientes_com_metricas

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Cliente

@login_required
def listar_clientes(request):
    empresa = request.user.empresa
    if not empresa:
        return redirect('logout')
    
    clientes = Cliente.objects.filter(empresa=empresa).order_by('nome')
    
    context = {
        'empresa': empresa,
        'clientes': clientes,
    }
    return render(request, 'clientes/listar.html', context)

@login_required
def criar_cliente(request):
    empresa = request.user.empresa
    if not empresa:
        return redirect('logout')
    
    if request.method == 'POST':
        nome = request.POST.get('nome')
        email = request.POST.get('email')
        telefone = request.POST.get('telefone')
        cpf = request.POST.get('cpf', '')
        data_nascimento = request.POST.get('data_nascimento', None)
        endereco = request.POST.get('endereco', '')
        cidade = request.POST.get('cidade', '')
        estado = request.POST.get('estado', '')
        cep = request.POST.get('cep', '')
        notas = request.POST.get('notas', '')
        
        try:
            cliente = Cliente.objects.create(
                empresa=empresa,
                nome=nome,
                email=email,
                telefone=telefone,
                cpf=cpf,
                data_nascimento=data_nascimento if data_nascimento else None,
                endereco=endereco,
                cidade=cidade,
                estado=estado,
                cep=cep,
                notas=notas,
            )
            messages.success(request, f'Cliente {nome} criado com sucesso!')
            return redirect('listar_clientes')
        except Exception as e:
            messages.error(request, f'Erro ao criar cliente: {str(e)}')
    
    context = {
        'empresa': empresa,
    }
    return render(request, 'clientes/criar.html', context)

@login_required
def editar_cliente(request, id):
    empresa = request.user.empresa
    cliente = get_object_or_404(Cliente, id=id, empresa=empresa)
    
    if request.method == 'POST':
        cliente.nome = request.POST.get('nome', cliente.nome)
        cliente.email = request.POST.get('email', cliente.email)
        cliente.telefone = request.POST.get('telefone', cliente.telefone)
        cliente.cpf = request.POST.get('cpf', cliente.cpf)
        cliente.data_nascimento = request.POST.get('data_nascimento', cliente.data_nascimento)
        cliente.endereco = request.POST.get('endereco', cliente.endereco)
        cliente.cidade = request.POST.get('cidade', cliente.cidade)
        cliente.estado = request.POST.get('estado', cliente.estado)
        cliente.cep = request.POST.get('cep', cliente.cep)
        cliente.notas = request.POST.get('notas', cliente.notas)
        cliente.save()
        
        messages.success(request, 'Cliente atualizado com sucesso!')
        return redirect('listar_clientes')
    
    context = {
        'empresa': empresa,
        'cliente': cliente,
    }
    return render(request, 'clientes/editar.html', context)

@login_required
def deletar_cliente(request, id):
    empresa = request.user.empresa
    cliente = get_object_or_404(Cliente, id=id, empresa=empresa)
    
    if request.method == 'POST':
        nome = cliente.nome
        cliente.delete()
        messages.success(request, f'Cliente {nome} deletado com sucesso!')
        return redirect('listar_clientes')
    
    context = {
        'empresa': empresa,
        'cliente': cliente,
    }
    return render(request, 'clientes/deletar.html', context)

def dashboard_clientes(request):
    clientes = listar_clientes_com_metricas()
    return render(request, 'clientes/dashboard.html', {'clientes': clientes})

def lista_clientes(request):
    return render(request, 'clientes/lista.html')
