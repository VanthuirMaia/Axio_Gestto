# 🇧🇷 Conformidade com CDC - Direito de Arrependimento

## ✅ O que já está implementado:

### 1. **Trial Grátis de 7 Dias** ✅
- Cliente testa ANTES de pagar
- Resolve 90% dos casos de arrependimento
- Cliente cancela durante trial → sem cobrança

### 2. **Termos de Uso e Política de Cancelamento** ✅
- Páginas criadas e disponíveis
- Links no footer de todas as páginas
- Checkbox de aceite obrigatório no cadastro
- Informação clara sobre direito de arrependimento

### 3. **Avisos Claros** ✅
- Box destacado no formulário de cadastro
- Informa sobre 7 dias grátis + 7 dias de arrependimento
- Link direto para política de cancelamento

---

## ⏳ O que precisa implementar (próxima etapa):

### 1. **Sistema de Reembolso Automático** (via Stripe API)

O Stripe já tem API para refund. Precisa implementar:

**Arquivo:** `assinaturas/refund.py`

```python
import stripe
from django.conf import settings
from .models import Assinatura, HistoricoPagamento

stripe.api_key = settings.STRIPE_SECRET_KEY

def processar_reembolso(assinatura_id, motivo='requested_by_customer'):
    """
    Processa reembolso automático via Stripe

    Args:
        assinatura_id: ID da assinatura no banco
        motivo: Motivo do reembolso (CDC, requested_by_customer, etc)

    Returns:
        dict com status do reembolso
    """
    assinatura = Assinatura.objects.get(id=assinatura_id)

    # Buscar último pagamento bem-sucedido
    ultimo_pagamento = HistoricoPagamento.objects.filter(
        assinatura=assinatura,
        status='aprovado'
    ).order_by('-data_criacao').first()

    if not ultimo_pagamento:
        return {'sucesso': False, 'erro': 'Nenhum pagamento encontrado'}

    # Verificar se está no período de 7 dias
    from django.utils.timezone import now
    from datetime import timedelta

    dias_desde_pagamento = (now() - ultimo_pagamento.data_criacao).days

    if dias_desde_pagamento > 7:
        return {
            'sucesso': False,
            'erro': 'Período de arrependimento expirado (mais de 7 dias)'
        }

    # Processar reembolso no Stripe
    try:
        # Buscar Payment Intent no Stripe
        payment_intent = stripe.PaymentIntent.retrieve(
            ultimo_pagamento.transaction_id
        )

        # Criar reembolso
        refund = stripe.Refund.create(
            payment_intent=payment_intent.id,
            reason=motivo,
            metadata={
                'assinatura_id': assinatura.id,
                'empresa_id': assinatura.empresa.id,
                'motivo_cdc': 'Art. 49 - Direito de Arrependimento'
            }
        )

        # Cancelar assinatura no Stripe
        if assinatura.subscription_id_externo:
            stripe.Subscription.delete(assinatura.subscription_id_externo)

        # Atualizar status no banco
        assinatura.status = 'cancelada'
        assinatura.motivo_cancelamento = f'CDC - Reembolso processado: {refund.id}'
        assinatura.save()

        # Registrar reembolso no histórico
        ultimo_pagamento.status = 'estornado'
        ultimo_pagamento.metadados['refund_id'] = refund.id
        ultimo_pagamento.metadados['refund_date'] = str(now())
        ultimo_pagamento.save()

        return {
            'sucesso': True,
            'refund_id': refund.id,
            'valor': refund.amount / 100,  # Centavos para reais
            'status': refund.status
        }

    except stripe.error.StripeError as e:
        return {
            'sucesso': False,
            'erro': str(e)
        }


def pode_solicitar_reembolso(assinatura_id):
    """
    Verifica se assinatura está elegível para reembolso CDC

    Returns:
        tuple (bool, str): (elegível, mensagem)
    """
    assinatura = Assinatura.objects.get(id=assinatura_id)

    # Verificar se já foi cancelada
    if assinatura.status == 'cancelada':
        return (False, 'Assinatura já foi cancelada')

    # Buscar último pagamento
    ultimo_pagamento = HistoricoPagamento.objects.filter(
        assinatura=assinatura,
        status='aprovado'
    ).order_by('-data_criacao').first()

    if not ultimo_pagamento:
        # Está em trial, pode cancelar sem reembolso
        return (True, 'Trial - Pode cancelar sem custos')

    # Verificar prazo de 7 dias
    from django.utils.timezone import now
    dias_desde_pagamento = (now() - ultimo_pagamento.data_criacao).days

    if dias_desde_pagamento <= 7:
        return (True, f'Dentro do prazo (dia {dias_desde_pagamento} de 7)')
    else:
        return (False, f'Prazo expirado (há {dias_desde_pagamento} dias)')
```

---

### 2. **View de Cancelamento com Reembolso**

**Arquivo:** `configuracoes/views.py`

```python
@login_required
def cancelar_assinatura(request):
    """View para cancelar assinatura com reembolso CDC"""

    if request.method == 'POST':
        assinatura = request.user.empresa.assinatura
        motivo = request.POST.get('motivo')

        # Verificar elegibilidade
        elegivel, mensagem = pode_solicitar_reembolso(assinatura.id)

        if not elegivel:
            messages.error(request, f'Não é possível reembolsar: {mensagem}')
            return redirect('configuracoes:assinatura')

        # Processar cancelamento
        if motivo == 'cdc_arrependimento':
            resultado = processar_reembolso(assinatura.id, motivo='requested_by_customer')

            if resultado['sucesso']:
                messages.success(
                    request,
                    f'Assinatura cancelada com sucesso! '
                    f'Reembolso de R$ {resultado["valor"]:.2f} processado. '
                    f'O valor será devolvido em até 5 dias úteis.'
                )
            else:
                messages.error(request, f'Erro ao processar reembolso: {resultado["erro"]}')
        else:
            # Cancelamento normal sem reembolso
            assinatura.status = 'cancelada'
            assinatura.motivo_cancelamento = motivo
            assinatura.save()

            messages.success(request, 'Assinatura cancelada. Acesso mantido até o fim do período pago.')

        return redirect('configuracoes:assinatura')

    # GET - Mostrar formulário
    assinatura = request.user.empresa.assinatura
    elegivel, mensagem = pode_solicitar_reembolso(assinatura.id)

    context = {
        'assinatura': assinatura,
        'pode_reembolsar': elegivel,
        'mensagem_elegibilidade': mensagem
    }

    return render(request, 'configuracoes/cancelar_assinatura.html', context)
```

---

### 3. **Template de Cancelamento**

**Arquivo:** `templates/configuracoes/cancelar_assinatura.html`

```html
<h1>Cancelar Assinatura</h1>

{% if pode_reembolsar %}
  <div class="alert alert-info">
    ⚖️ <strong>Direito de Arrependimento (CDC)</strong><br>
    {{ mensagem_elegibilidade }}<br>
    Você receberá reembolso total do valor pago.
  </div>

  <form method="post">
    {% csrf_token %}

    <label>
      <input type="radio" name="motivo" value="cdc_arrependimento" checked>
      Direito de Arrependimento (CDC - Art. 49) - Reembolso Total
    </label>

    <button type="submit">Cancelar e Receber Reembolso</button>
  </form>
{% else %}
  <p>{{ mensagem_elegibilidade }}</p>
  <p>Você pode cancelar a assinatura, mas não há direito a reembolso após 7 dias do pagamento.</p>

  <form method="post">
    {% csrf_token %}
    <input type="hidden" name="motivo" value="cancelamento_normal">
    <button type="submit">Cancelar Assinatura (sem reembolso)</button>
  </form>
{% endif %}
```

---

## 📧 Emails Automáticos (Recomendado)

### Email 1 - Confirmação de Trial
**Quando:** Ao criar conta
**Conteúdo:**
- Boas-vindas
- Lembrete: 7 dias grátis
- Como cancelar antes da cobrança

### Email 2 - Lembrete Fim do Trial
**Quando:** 2 dias antes do fim do trial (dia 5)
**Conteúdo:**
- Trial acaba em 2 dias
- Será cobrado R$ 49,00 no dia X
- Como cancelar para não ser cobrado

### Email 3 - Primeira Cobrança
**Quando:** Ao processar primeiro pagamento
**Conteúdo:**
- Confirmação de pagamento
- **Lembrete do direito de arrependimento (7 dias)**
- Link para cancelar com reembolso

### Email 4 - Confirmação de Cancelamento
**Quando:** Ao cancelar com reembolso
**Conteúdo:**
- Confirmação de cancelamento
- Valor do reembolso
- Prazo para devolução (5 dias úteis)

---

## 🔒 Checklist de Conformidade CDC

- [x] Trial grátis de 7 dias implementado
- [x] Termos de Uso disponíveis
- [x] Política de Cancelamento disponível
- [x] Aviso claro sobre direito de arrependimento
- [x] Checkbox de aceite dos termos
- [ ] Sistema de reembolso automático (implementar)
- [ ] Emails automáticos informativos (implementar)
- [ ] Página de gerenciamento de assinatura (implementar)
- [ ] Botão de cancelamento fácil de encontrar
- [ ] Formulário de cancelamento sem fricção

---

## ⚖️ Referências Legais

**Código de Defesa do Consumidor - Lei 8.078/90**

**Art. 49:**
> "O consumidor pode desistir do contrato, no prazo de 7 dias a contar de sua assinatura ou do ato de recebimento do produto ou serviço, sempre que a contratação de fornecimento de produtos e serviços ocorrer fora do estabelecimento comercial, especialmente por telefone ou a domicílio."

**Parágrafo único:**
> "Se o consumidor exercitar o direito de arrependimento previsto neste artigo, os valores eventualmente pagos, a qualquer título, durante o prazo de reflexão, serão devolvidos, de imediato, monetariamente atualizados."

---

## 📞 Suporte ao Cliente

**Email:** suporte@gestto.com.br
**WhatsApp:** (11) 99999-9999
**Horário:** Segunda a Sexta, 9h às 18h

**Prazo de resposta:** Até 24 horas
**Prazo de reembolso:** Até 5 dias úteis
