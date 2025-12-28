"""
Views do wizard de onboarding (4 passos)

Fluxo:
1. Configurar serviços
2. Cadastrar profissional
3. Conectar WhatsApp
4. Concluído! 🎉
"""
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.timezone import now
from empresas.models import Servico, Profissional, HorarioFuncionamento
from datetime import time


@login_required
def onboarding_wizard(request):
    """
    Redireciona para etapa correta do onboarding ou dashboard se já completo
    """
    empresa = request.user.empresa

    # Se onboarding já completo, vai para dashboard
    if empresa.onboarding_completo:
        return redirect('dashboard')

    # Redirecionar para etapa atual
    etapa = empresa.onboarding_etapa

    if etapa == 0:
        return redirect('onboarding_step_1')
    elif etapa == 1:
        return redirect('onboarding_step_2')
    elif etapa >= 2:  # Pula WhatsApp, vai direto para conclusão
        return redirect('onboarding_step_4')
    else:
        return redirect('onboarding_step_1')


@login_required
def onboarding_step_1_servicos(request):
    """
    PASSO 1: Cadastrar serviços que a empresa oferece
    """
    empresa = request.user.empresa

    if request.method == 'POST':
        # Processar formulário de serviços
        servicos_nomes = request.POST.getlist('servico_nome[]')
        servicos_precos = request.POST.getlist('servico_preco[]')
        servicos_duracoes = request.POST.getlist('servico_duracao[]')

        # Validar que tem pelo menos 1 serviço
        servicos_validos = []
        for nome, preco, duracao in zip(servicos_nomes, servicos_precos, servicos_duracoes):
            if nome and preco and duracao:
                try:
                    servicos_validos.append({
                        'nome': nome.strip(),
                        'preco': float(preco),
                        'duracao': int(duracao)
                    })
                except ValueError:
                    continue

        if not servicos_validos:
            messages.error(request, 'Cadastre pelo menos 1 serviço para continuar.')
            return redirect('onboarding_step_1')

        # Criar serviços
        for servico_data in servicos_validos:
            Servico.objects.create(
                empresa=empresa,
                nome=servico_data['nome'],
                preco=servico_data['preco'],
                duracao_minutos=servico_data['duracao'],
                ativo=True
            )

        # Avançar para próxima etapa
        empresa.onboarding_etapa = 1
        empresa.save()

        messages.success(request, f'{len(servicos_validos)} serviço(s) cadastrado(s) com sucesso!')
        return redirect('onboarding_step_2')

    # GET - Mostrar formulário
    servicos_existentes = Servico.objects.filter(empresa=empresa)

    context = {
        'empresa': empresa,
        'servicos': servicos_existentes,
        'etapa_atual': 1,
        'total_etapas': 3,
        'progresso': 33,  # 33% = 1/3
    }

    return render(request, 'onboarding/step_1_servicos.html', context)


@login_required
def onboarding_step_2_profissional(request):
    """
    PASSO 2: Cadastrar pelo menos 1 profissional
    """
    empresa = request.user.empresa

    # Verificar se está na etapa correta
    if empresa.onboarding_etapa < 1:
        messages.warning(request, 'Complete o passo anterior primeiro.')
        return redirect('onboarding_step_1')

    if request.method == 'POST':
        # Extrair dados do formulário
        nome = request.POST.get('prof_nome', '').strip()
        email = request.POST.get('prof_email', '').strip()
        telefone = request.POST.get('prof_telefone', '').strip()
        servicos_ids = request.POST.getlist('prof_servicos')

        # Validar campos obrigatórios
        if not nome or not email:
            messages.error(request, 'Nome e email são obrigatórios.')
            return redirect('onboarding_step_2')

        if not servicos_ids:
            messages.error(request, 'Selecione pelo menos 1 serviço que este profissional executa.')
            return redirect('onboarding_step_2')

        # Criar profissional
        try:
            profissional = Profissional.objects.create(
                empresa=empresa,
                nome=nome,
                email=email,
                telefone=telefone,
                ativo=True,
                cor_hex='#3b82f6'  # Azul padrão
            )

            # Associar serviços
            profissional.servicos.set(servicos_ids)

            # Avançar para próxima etapa (pula WhatsApp)
            empresa.onboarding_etapa = 3
            empresa.save()

            messages.success(request, f'Profissional {nome} cadastrado com sucesso!')
            return redirect('onboarding_step_4')

        except Exception as e:
            messages.error(request, f'Erro ao cadastrar profissional: {str(e)}')
            return redirect('onboarding_step_2')

    # GET - Mostrar formulário
    servicos = Servico.objects.filter(empresa=empresa, ativo=True)
    profissionais_existentes = Profissional.objects.filter(empresa=empresa)

    if not servicos.exists():
        messages.error(request, 'Você precisa cadastrar serviços primeiro!')
        return redirect('onboarding_step_1')

    context = {
        'empresa': empresa,
        'servicos': servicos,
        'profissionais': profissionais_existentes,
        'etapa_atual': 2,
        'total_etapas': 3,
        'progresso': 66,  # 66% = 2/3
    }

    return render(request, 'onboarding/step_2_profissional.html', context)


@login_required
def onboarding_step_3_whatsapp(request):
    """
    PASSO 3: Conectar WhatsApp (opcional, pode pular)
    """
    empresa = request.user.empresa

    # Verificar se está na etapa correta
    if empresa.onboarding_etapa < 2:
        messages.warning(request, 'Complete os passos anteriores primeiro.')
        return redirect('onboarding_wizard')

    if request.method == 'POST':
        # Verificar se quer pular
        pular = request.POST.get('pular', False)

        if pular:
            # Pular WhatsApp por enquanto
            empresa.onboarding_etapa = 3
            empresa.save()
            messages.info(request, 'WhatsApp não configurado. Você pode configurar depois em Configurações.')
            return redirect('onboarding_step_4')

        # Configurar WhatsApp
        whatsapp_numero = request.POST.get('whatsapp_numero', '').strip()
        whatsapp_token = request.POST.get('whatsapp_token', '').strip()
        whatsapp_instance_id = request.POST.get('whatsapp_instance_id', '').strip()

        if not whatsapp_numero or not whatsapp_instance_id:
            messages.error(request, 'Informe o número do WhatsApp e o Instance ID.')
            return redirect('onboarding_step_3')

        # Verificar se instance_id já existe (deve ser único)
        from empresas.models import Empresa as EmpresaModel
        if EmpresaModel.objects.filter(whatsapp_instance_id=whatsapp_instance_id).exclude(id=empresa.id).exists():
            messages.error(request, 'Este Instance ID já está em uso por outra empresa. Use um ID único.')
            return redirect('onboarding_step_3')

        # Salvar configuração (validação real será feita depois)
        empresa.whatsapp_numero = whatsapp_numero
        empresa.whatsapp_token = whatsapp_token
        empresa.whatsapp_instance_id = whatsapp_instance_id
        empresa.whatsapp_conectado = False  # Marcar como não testado ainda
        empresa.onboarding_etapa = 3
        empresa.save()

        messages.success(request, f'WhatsApp configurado! Instance: {whatsapp_instance_id}')
        return redirect('onboarding_step_4')

    # GET - Mostrar formulário
    context = {
        'empresa': empresa,
        'etapa_atual': 3,
        'total_etapas': 4,
        'progresso': 75,  # 75% = 3/4
    }

    return render(request, 'onboarding/step_3_whatsapp.html', context)


@login_required
def onboarding_step_4_pronto(request):
    """
    PASSO 4: Concluído! Mostrar resumo e confete 🎉
    """
    empresa = request.user.empresa

    # Verificar se está na etapa correta
    if empresa.onboarding_etapa < 3:
        messages.warning(request, 'Complete os passos anteriores primeiro.')
        return redirect('onboarding_wizard')

    # Marcar onboarding como completo
    if not empresa.onboarding_completo:
        empresa.onboarding_completo = True
        empresa.onboarding_etapa = 4
        empresa.save()

        # Criar horários de funcionamento padrão (seg-sex 9h-18h)
        _criar_horarios_padrao(empresa)

    # Coletar estatísticas para mostrar
    total_servicos = Servico.objects.filter(empresa=empresa).count()
    total_profissionais = Profissional.objects.filter(empresa=empresa).count()
    whatsapp_configurado = empresa.whatsapp_conectado

    context = {
        'empresa': empresa,
        'total_servicos': total_servicos,
        'total_profissionais': total_profissionais,
        'whatsapp_configurado': whatsapp_configurado,
        'link_agendamento': f'/agendar/{empresa.slug}/',  # Link público de agendamento
        'etapa_atual': 3,
        'total_etapas': 3,
        'progresso': 100,
    }

    return render(request, 'onboarding/step_4_pronto.html', context)


def _criar_horarios_padrao(empresa):
    """
    Cria horários de funcionamento padrão (seg-sex 9h-18h)
    """
    # Verificar se já tem horários
    if HorarioFuncionamento.objects.filter(empresa=empresa).exists():
        return

    # Criar horários padrão (segunda a sexta)
    dias_uteis = [0, 1, 2, 3, 4]  # 0=segunda, 4=sexta

    for dia in dias_uteis:
        HorarioFuncionamento.objects.create(
            empresa=empresa,
            dia_semana=dia,
            hora_abertura=time(9, 0),
            hora_fechamento=time(18, 0),
            ativo=True
        )
