from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Agendamento
from .forms import AgendamentoForm
import datetime
from core.views import somente_admin
from .models import Agendamento, HorarioBloqueado
from .forms import AgendamentoForm, HorarioBloqueadoForm
from core.views import somente_admin
from django.db import models

@somente_admin
def agendamento_list(request):
    agendamentos = Agendamento.objects.select_related('cliente', 'servico', 'barbeiro').order_by('-data', '-horario')
    status_filter = request.GET.get('status')
    if status_filter:
        agendamentos = agendamentos.filter(status=status_filter)
    return render(request, 'agendamentos/list.html', {'agendamentos': agendamentos, 'status_filter': status_filter})

@login_required
def agendamento_create(request):
    form = AgendamentoForm(request.POST or None)
    if form.is_valid():
        ag = form.save(commit=False)

        # Verificar bloqueios
        bloqueios = HorarioBloqueado.objects.filter(
            data=ag.data
        ).filter(
            models.Q(barbeiro=ag.barbeiro) | models.Q(barbeiro__isnull=True)
        )

        bloqueio_encontrado = None
        for b in bloqueios:
            if b.tipo == 'dia':
                bloqueio_encontrado = b
                break
            elif b.tipo == 'horario' and b.horario_inicio and b.horario_fim:
                if b.horario_inicio <= ag.horario <= b.horario_fim:
                    bloqueio_encontrado = b
                    break

        if bloqueio_encontrado:
            motivo = bloqueio_encontrado.motivo or 'Horário indisponível'
            form.add_error(None, f'Este horário está bloqueado: {motivo}')
        else:
            ag.save()
            messages.success(request, 'Agendamento criado com sucesso!')
            return redirect('agendamento_list')

    return render(request, 'agendamentos/form.html', {'form': form, 'title': 'Novo Agendamento'})

@somente_admin
def agendamento_detail(request, pk):
    agendamento = get_object_or_404(Agendamento, pk=pk)
    return render(request, 'agendamentos/detail.html', {'agendamento': agendamento})

@somente_admin
def agendamento_edit(request, pk):
    agendamento = get_object_or_404(Agendamento, pk=pk)
    form = AgendamentoForm(request.POST or None, instance=agendamento)
    if form.is_valid():
        form.save()
        messages.success(request, 'Agendamento atualizado!')
        return redirect('agendamento_list')
    return render(request, 'agendamentos/form.html', {'form': form, 'title': 'Editar Agendamento'})

@somente_admin
def agendamento_cancelar(request, pk):
    agendamento = get_object_or_404(Agendamento, pk=pk)
    if request.method == 'POST':
        agendamento.status = 'cancelado'
        agendamento.save()
        messages.warning(request, 'Agendamento cancelado.')
        return redirect('agendamento_list')
    return render(request, 'confirm_delete.html', {'obj': agendamento, 'nome': f'agendamento de {agendamento.cliente}', 'action': 'cancelar'})

@somente_admin
def agenda_view(request):
    hoje = datetime.date.today()
    data_str = request.GET.get('data', str(hoje))
    try:
        data = datetime.date.fromisoformat(data_str)
    except ValueError:
        data = hoje
    agendamentos_dia = Agendamento.objects.filter(data=data).select_related('cliente', 'servico', 'barbeiro').order_by('horario')
    semana_inicio = data - datetime.timedelta(days=data.weekday())
    semana = [semana_inicio + datetime.timedelta(days=i) for i in range(7)]
    return render(request, 'agendamentos/agenda.html', {
        'data': data,
        'agendamentos_dia': agendamentos_dia,
        'semana': semana,
        'hoje': hoje,
    })

@somente_admin
def horario_bloqueado_list(request):
    bloqueios = HorarioBloqueado.objects.select_related('barbeiro').order_by('data')
    return render(request, 'agendamentos/bloqueios.html', {'bloqueios': bloqueios})

@somente_admin
def horario_bloqueado_create(request):
    form = HorarioBloqueadoForm(request.POST or None)
    if form.is_valid():
        form.save()
        messages.success(request, 'Bloqueio criado com sucesso!')
        return redirect('horario_bloqueado_list')
    return render(request, 'agendamentos/bloqueio_form.html', {'form': form, 'title': 'Novo Bloqueio'})

@somente_admin
def horario_bloqueado_delete(request, pk):
    bloqueio = get_object_or_404(HorarioBloqueado, pk=pk)
    if request.method == 'POST':
        bloqueio.delete()
        messages.success(request, 'Bloqueio removido!')
        return redirect('horario_bloqueado_list')
    return render(request, 'confirm_delete.html', {'nome': str(bloqueio)})