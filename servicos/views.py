from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Servico
from .forms import ServicoForm
<<<<<<< HEAD
from core.decorators import somente_admin
=======
from core.views import somente_admin
from core.views import somente_admin
>>>>>>> 0a25220212c755bd746eca7615324b57ff95a5e6

@somente_admin
def servico_list(request):
    servicos = Servico.objects.all()
    return render(request, 'servicos/list.html', {'servicos': servicos})

@somente_admin
def servico_create(request):
    form = ServicoForm(request.POST or None)
    if form.is_valid():
        form.save()
        messages.success(request, 'Serviço cadastrado com sucesso!')
        return redirect('servico_list')
    return render(request, 'servicos/form.html', {'form': form, 'title': 'Novo Serviço'})

@somente_admin
def servico_edit(request, pk):
    servico = get_object_or_404(Servico, pk=pk)
    form = ServicoForm(request.POST or None, instance=servico)
    if form.is_valid():
        form.save()
        messages.success(request, 'Serviço atualizado!')
        return redirect('servico_list')
    return render(request, 'servicos/form.html', {'form': form, 'title': 'Editar Serviço', 'servico': servico})

@somente_admin
def servico_delete(request, pk):
    servico = get_object_or_404(Servico, pk=pk)
    if request.method == 'POST':
        servico.delete()
        messages.success(request, 'Serviço removido!')
        return redirect('servico_list')
    return render(request, 'confirm_delete.html', {'obj': servico, 'nome': servico.nome})
