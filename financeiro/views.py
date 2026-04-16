from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum
from agendamento.models import Agendamento
from .models import Pagamento
from .forms import PagamentoForm
import datetime
from core.views import somente_admin

@somente_admin
def financeiro_dashboard(request):
    hoje = datetime.date.today()
    mes_inicio = hoje.replace(day=1)
    concluidos = Agendamento.objects.filter(status='concluido')
    ganhos_hoje = concluidos.filter(data=hoje).aggregate(total=Sum('preco'))['total'] or 0
    ganhos_mes = concluidos.filter(data__gte=mes_inicio).aggregate(total=Sum('preco'))['total'] or 0
    sem_pagamento = concluidos.filter(pagamento__isnull=True)
    pagamentos = Pagamento.objects.select_related('agendamento__cliente', 'agendamento__barbeiro').order_by('-pago_em')[:10]
    return render(request, 'financeiro/dashboard.html', {
        'ganhos_hoje': ganhos_hoje,
        'ganhos_mes': ganhos_mes,
        'sem_pagamento': sem_pagamento,
        'pagamentos': pagamentos,
    })

@somente_admin
def registrar_pagamento(request, agendamento_id):
    agendamento = get_object_or_404(Agendamento, pk=agendamento_id, status='concluido')
    form = PagamentoForm(request.POST or None, initial={'valor': agendamento.preco})
    if form.is_valid():
        pagamento = form.save(commit=False)
        pagamento.agendamento = agendamento
        pagamento.save()
        messages.success(request, 'Pagamento registrado!')
        return redirect('financeiro_dashboard')
    return render(request, 'financeiro/pagamento.html', {'form': form, 'agendamento': agendamento})

@somente_admin
def relatorio(request):
    agendamentos = Agendamento.objects.select_related('cliente', 'servico', 'barbeiro').order_by('-data')
    total_faturamento = agendamentos.filter(status='concluido').aggregate(total=Sum('preco'))['total'] or 0
    return render(request, 'financeiro/relatorio.html', {
        'agendamentos': agendamentos,
        'total_faturamento': total_faturamento,
    })
