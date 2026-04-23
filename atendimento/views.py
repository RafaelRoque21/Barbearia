from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from agendamento.models import Agendamento
import datetime
from core.views import somente_admin
from core.decorators import somente_admin

@somente_admin
def atendimento_list(request):
    hoje = datetime.date.today()
    agendamentos = Agendamento.objects.filter(data=hoje, status__in=['confirmado', 'pendente']).select_related('cliente', 'servico', 'barbeiro').order_by('horario')
    return render(request, 'atendimento/list.html', {'agendamentos': agendamentos, 'hoje': hoje})

@somente_admin
def iniciar_atendimento(request, pk):
    agendamento = get_object_or_404(Agendamento, pk=pk)
    agendamento.status = 'confirmado'
    agendamento.save()
    messages.success(request, 'Atendimento iniciado!')
    return redirect('atendimento_list')

@somente_admin
def finalizar_atendimento(request, pk):
    agendamento = get_object_or_404(Agendamento, pk=pk)
    if request.method == 'POST':
        obs = request.POST.get('observacao', '')
        agendamento.status = 'concluido'
        agendamento.observacao = obs
        agendamento.save()
        messages.success(request, 'Atendimento finalizado com sucesso!')
        return redirect('financeiro_dashboard')
    return render(request, 'atendimento/finalizar.html', {'agendamento': agendamento})
