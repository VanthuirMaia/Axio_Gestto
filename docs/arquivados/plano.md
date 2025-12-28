Para evoluir seu sistema de agendamento/atendimento WhatsApp (Gestto + n8n + Google Calendar + Supabase) para SaaS self-service, siga essas 5 etapas sequenciais. Cada uma tem tempo estimado, pré-requisitos, ações exatas e teste de conclusão. Faça uma por vez, teste 100% antes de avançar. Total: 2-4 semanas se dedicar 2h/dia.
​

Etapa 1: Congele o Produto Mínimo (2 dias)
Objetivo: Definir exatamente o que o cliente Essencial recebe, sem ambiguidade.

Pré-requisitos: Seu Gestto e n8n funcionando em produção (como já estão).

Ações:

Crie um doc Google/MD chamado "Especificação Essencial":

Agenda: 1 profissional, 500 agendamentos/mês.

WhatsApp: Bot padrão agenda/lembrete/confirma no Google Calendar.

Relatórios: Faturamento simples do mês.

Grave um vídeo de 2min mostrando o fluxo completo (cliente manda msg → agenda → confirma).

Publique em pasta privada no Drive/Notion.

Teste de conclusão: Mostre o doc/vídeo para 1 amigo dono de salão. Ele entende em 5min o que recebe por R$49/mês? ✅

Etapa 2: Configure Pagamentos + Criação Automática de Empresa (3-4 dias)
Objetivo: Cliente paga → sistema cria conta dele sozinho.

Pré-requisitos: Etapa 1 ok. Conta Stripe/PagSeguro/Asaas ativa (R$0 inicial).
​

Ações:

Na LP (Carrd/Webflow grátis): Botão "Assinar Essencial R$49 trial 7dias".

Checkout → webhook chama sua API Django: POST /api/create-tenant.

No Django, crie models/views:

text

# models.py

class Tenant(models.Model):
name = CharField()
subdomain = CharField() # empresa.gestto.com.br
plan = CharField(choices=['essencial'])
max_appointments = 500
created_at = DateTimeField()

# views.py

@api_view(['POST'])
def create_tenant(request):
tenant = Tenant.objects.create(
name=request.data['company_name'],
subdomain=slugify(request.data['company_name']),
plan='essencial'
) # Cria admin user básico # Retorna login: admin@empresa.gestto.com.br / senha temporária
return Response({'login_url': f'https://{tenant.subdomain}.gestto.com.br/onboarding'})
Configure webhook no Stripe: URL https://seuvps.com/api/webhook-stripe.

Teste de conclusão: Pague R$1 teste → recebe email com login → entra no sistema como nova empresa. ✅
​

Etapa 3: Onboarding Guiado no App (3 dias)
Objetivo: Nova empresa configura tudo em 10min sem falar com você.

Pré-requisitos: Etapa 2 ok.

Ações:

Crie rota /onboarding/ no Django (wizard 4 passos):

Passo 1: Cadastre serviços/horários.

Passo 2: Cadastre 1 profissional (você mesmo pra testar).

Passo 3: Cole token WhatsApp (de Z-API/Evolution) → testa conexão.

Passo 4: Copie link de agendamento → pronto!

Salve configs no Tenant: whatsapp_token, services_json, etc.

Após passo 4: Redireciona pra dashboard com confete 🎉.

Teste de conclusão: Crie tenant teste → complete wizard → mande msg WhatsApp → agenda criada no Calendar. ✅
​

Etapa 4: WhatsApp Multi-Tenant Seguro (4-5 dias)
Objetivo: 1 webhook recebe msgs de todos clientes, roteia certo.

Pré-requisitos: Etapas 1-3 ok. Seu provedor WhatsApp com API webhook.
​

Ações:

1 endpoint único: POST /api/whatsapp-webhook.

text
@api_view(['POST'])
def whatsapp_webhook(request):
phone = request.data['from'] # 5511999999999
tenant = Tenant.objects.get(whatsapp_phone=phone) # Chama n8n com tenant_id
n8n_webhook(f"https://n8n.seuvps.com/webhook/{tenant.id}", request.data)
return Response({'status': 'ok'})
No n8n: Workflow genérico com variável {{ $json.tenant_id }}:

Pega configs do tenant (horários, serviços) via Supabase API.

Agenda no Google Calendar do tenant.

Responde msg.

Rate limit: Cloudflare free blocking >10 req/seg por IP.

Teste de conclusão: 2 números WhatsApp diferentes → msgs vão pro tenant certo, agendas separadas. ✅
​

Etapa 5: Limites + Monitoramento (2 dias)
Objetivo: Proteger custos, forçar upgrade.

Pré-requisitos: Todas anteriores ok.

Ações:

Middleware Django checa tenant.plan.max_appointments.

Dashboard mostra: "320/500 agendamentos usados (64%)".

Ao atingir 90%: Bloqueia novos, botão "Upgrade Pro R$149".

Monitore: n8n executions, Supabase rows por tenant.

Teste de conclusão: Force 501º agendamento → bloqueia + mostra upgrade. ✅
​

Próximo após Etapa 5: LP ao vivo + 5 clientes piloto grátis 30dias. Me mande prints de cada ✅ pra ajustar antes avançar!
​
