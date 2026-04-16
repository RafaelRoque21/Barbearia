from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Usuario, Barbeiro
from .forms import ClienteForm, BarbeiroForm
from agendamento.models import Agendamento
from servicos.models import Servico
import datetime
from .forms import ClienteForm, BarbeiroForm, PerfilClienteForm
# Verificar bloqueios
from agendamento.models import HorarioBloqueado
from django.db.models import Q
import datetime as dt

def somente_admin(view_func):
    from functools import wraps
    from django.http import HttpResponseForbidden
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated or request.user.tipo == 'cliente':
            return HttpResponseForbidden('<h2 style="font-family:sans-serif;padding:2rem">Acesso negado. <a href="/">Voltar</a></h2>')
        return view_func(request, *args, **kwargs)
    return wrapper

def index(request):
    if request.user.is_authenticated:
        if request.user.tipo == 'cliente':
            return redirect('cliente_portal')
        return redirect('dashboard')
    return redirect('login')

# ── PORTAL DO CLIENTE ────────────────────────────────────────

@login_required
def cliente_portal(request):
    if request.user.tipo != 'cliente':
        return redirect('dashboard')
    agendamentos = Agendamento.objects.filter(
        cliente=request.user
    ).select_related('servico', 'barbeiro').order_by('-data', '-horario')[:5]
    return render(request, 'portal/home.html', {'agendamentos': agendamentos})

@login_required
def cliente_historico(request):
    if request.user.tipo != 'cliente':
        return redirect('dashboard')
    agendamentos = Agendamento.objects.filter(
        cliente=request.user
    ).select_related('servico', 'barbeiro').order_by('-data', '-horario')
    return render(request, 'portal/historico.html', {'agendamentos': agendamentos})

@login_required
def cliente_agendar(request):
    if request.user.tipo != 'cliente':
        return redirect('dashboard')
    from servicos.models import Servico
    from .models import Barbeiro
    from agendamento.models import Agendamento

    servicos = Servico.objects.filter(status='ativo')
    barbeiros = Barbeiro.objects.filter(status='ativo')

    if request.method == 'POST':
        servico_id = request.POST.get('servico')
        barbeiro_id = request.POST.get('barbeiro')
        data = request.POST.get('data')
        horario = request.POST.get('horario')

        erros = []
        if not all([servico_id, barbeiro_id, data, horario]):
            erros.append('Preencha todos os campos.')
        else:
            try:
                data_obj = datetime.date.fromisoformat(data)
                if data_obj < datetime.date.today():
                    erros.append('A data não pode ser no passado.')
            except ValueError:
                erros.append('Data inválida.')

        if not erros:
            servico = get_object_or_404(Servico, pk=servico_id)
            barbeiro = get_object_or_404(Barbeiro, pk=barbeiro_id)
            conflito = Agendamento.objects.filter(
    barbeiro=barbeiro, data=data, horario=horario,
    status__in=['pendente', 'confirmado']
).exists()
            
    if conflito:
        erros.append('Este horário já está ocupado. Escolha outro.')
        
    horario_obj = dt.time.fromisoformat(horario)
    bloqueios = HorarioBloqueado.objects.filter(
        data=data_obj
    ).filter(
        Q(barbeiro=barbeiro) | Q(barbeiro__isnull=True)
    )
    for b in bloqueios:
        if b.tipo == 'dia':
            erros.append(f'Este dia está bloqueado: {b.motivo or "Indisponível"}')
            break
        elif b.tipo == 'horario' and b.horario_inicio and b.horario_fim:
            if b.horario_inicio <= horario_obj <= b.horario_fim:
                erros.append(f'Este horário está bloqueado: {b.motivo or "Indisponível"}')
                break

            if erros:
                for e in erros:
                    messages.error(request, e)
            else:
                Agendamento.objects.create(
                    cliente=request.user,
                    servico=servico,
                    barbeiro=barbeiro,
                    data=data,
                    horario=horario,
                    preco=servico.preco,
                    status='pendente'
                )
                messages.success(request, 'Agendamento realizado com sucesso!')
                return redirect('cliente_portal')

        return render(request, 'portal/agendar.html', {
            'servicos': servicos,
            'barbeiros': barbeiros,
            'hoje': datetime.date.today().isoformat(),
        })

@login_required
def cliente_horarios(request):
    if request.user.tipo != 'cliente':
        return redirect('dashboard')
    from .models import Barbeiro
    from agendamento.models import Agendamento

    barbeiros = Barbeiro.objects.filter(status='ativo')
    barbeiro_id = request.GET.get('barbeiro')
    data_str = request.GET.get('data', datetime.date.today().isoformat())

    try:
        data = datetime.date.fromisoformat(data_str)
    except ValueError:
        data = datetime.date.today()

    horarios = []
    barbeiro_sel = None

    if barbeiro_id:
        barbeiro_sel = get_object_or_404(Barbeiro, pk=barbeiro_id, status='ativo')
        ocupados = set(
            Agendamento.objects.filter(
                barbeiro=barbeiro_sel, data=data,
                status__in=['pendente', 'confirmado']
            ).values_list('horario', flat=True)
        )
        hora = datetime.datetime.combine(data, barbeiro_sel.horario_inicio)
        fim = datetime.datetime.combine(data, barbeiro_sel.horario_fim)
        while hora < fim:
            horarios.append({
                'hora': hora.time(),
                'ocupado': hora.time() in ocupados,
            })
            hora += datetime.timedelta(minutes=30)

    return render(request, 'portal/horarios.html', {
        'barbeiros': barbeiros,
        'barbeiro_sel': barbeiro_sel,
        'horarios': horarios,
        'data': data,
        'hoje': datetime.date.today().isoformat(),
        'data_str': data_str,
    })

@login_required
def cliente_perfil(request):
    if request.user.tipo != 'cliente':
        return redirect('dashboard')

    if request.method == 'POST':
        form_tipo = request.POST.get('form_tipo')

        if form_tipo == 'dados':
            request.user.first_name = request.POST.get('first_name', '')
            request.user.last_name = request.POST.get('last_name', '')
            request.user.email = request.POST.get('email', '')
            request.user.telefone = request.POST.get('telefone', '')
            request.user.save()
            messages.success(request, 'Perfil atualizado com sucesso!')

        elif form_tipo == 'senha':
            atual = request.POST.get('password_atual', '')
            nova = request.POST.get('password_nova', '')
            confirmar = request.POST.get('password_confirmar', '')

            if not atual or not nova or not confirmar:
                messages.error(request, 'Preencha todos os campos de senha.')
            elif not request.user.check_password(atual):
                messages.error(request, 'Senha atual incorreta.')
            elif nova != confirmar:
                messages.error(request, 'A nova senha e a confirmação não conferem.')
            elif len(nova) < 6:
                messages.error(request, 'A nova senha deve ter pelo menos 6 caracteres.')
            else:
                request.user.set_password(nova)
                request.user.save()
                messages.success(request, 'Senha alterada! Faça login novamente.')
                from django.contrib.auth import logout
                logout(request)
                return redirect('login')

        return redirect('cliente_perfil')

    return render(request, 'portal/perfil.html', {})

@login_required
def cliente_cancelar_agendamento(request, pk):
    if request.user.tipo != 'cliente':
        return redirect('dashboard')

    agendamento = get_object_or_404(Agendamento, pk=pk, cliente=request.user)

    if agendamento.status not in ['pendente', 'confirmado']:
        messages.error(request, 'Este agendamento não pode ser cancelado.')
        return redirect('cliente_historico')

    if request.method == 'POST':
        agendamento.status = 'cancelado'
        agendamento.save()
        messages.success(request, 'Agendamento cancelado com sucesso.')
        return redirect('cliente_historico')

    return render(request, 'portal/cancelar.html', {'agendamento': agendamento})

# ── ADMIN: BARBEIROS ─────────────────────────────────────────

@somente_admin
def dashboard(request):
    if request.user.tipo == 'cliente':
        return redirect('cliente_portal')
    import datetime
    hoje = datetime.date.today()
    agendamentos_hoje = Agendamento.objects.filter(data=hoje).count()
    agendamentos_pendentes = Agendamento.objects.filter(status='pendente').count()
    total_clientes = Usuario.objects.filter(tipo='cliente').count()
    total_barbeiros = Barbeiro.objects.filter(status='ativo').count()
    ultimos_agendamentos = Agendamento.objects.select_related('cliente', 'servico', 'barbeiro').order_by('-criado_em')[:5]
    return render(request, 'dashboard.html', {
        'agendamentos_hoje': agendamentos_hoje,
        'agendamentos_pendentes': agendamentos_pendentes,
        'total_clientes': total_clientes,
        'total_barbeiros': total_barbeiros,
        'ultimos_agendamentos': ultimos_agendamentos,
    })

@somente_admin
def barbeiro_list(request):
    barbeiros = Barbeiro.objects.all()
    return render(request, 'barbeiros/list.html', {'barbeiros': barbeiros})

@somente_admin
def barbeiro_create(request):
    form = BarbeiroForm(request.POST or None)
    if form.is_valid():
        form.save()
        messages.success(request, 'Barbeiro cadastrado com sucesso!')
        return redirect('barbeiro_list')
    return render(request, 'barbeiros/form.html', {'form': form, 'title': 'Novo Barbeiro'})

@somente_admin
def barbeiro_edit(request, pk):
    barbeiro = get_object_or_404(Barbeiro, pk=pk)
    form = BarbeiroForm(request.POST or None, instance=barbeiro)
    if form.is_valid():
        form.save()
        messages.success(request, 'Barbeiro atualizado!')
        return redirect('barbeiro_list')
    return render(request, 'barbeiros/form.html', {'form': form, 'title': 'Editar Barbeiro', 'barbeiro': barbeiro})

@somente_admin
def barbeiro_delete(request, pk):
    barbeiro = get_object_or_404(Barbeiro, pk=pk)
    if request.method == 'POST':
        barbeiro.delete()
        messages.success(request, 'Barbeiro removido!')
        return redirect('barbeiro_list')
    return render(request, 'confirm_delete.html', {'obj': barbeiro, 'nome': barbeiro.nome})

@somente_admin
def cliente_list(request):
    clientes = Usuario.objects.filter(tipo='cliente')
    return render(request, 'clientes/list.html', {'clientes': clientes})

@somente_admin
def cliente_create(request):
    form = ClienteForm(request.POST or None)
    if form.is_valid():
        form.save()
        messages.success(request, 'Cliente cadastrado com sucesso!')
        return redirect('cliente_list')
    return render(request, 'clientes/form.html', {'form': form, 'title': 'Novo Cliente'})

@somente_admin
def cliente_edit(request, pk):
    cliente = get_object_or_404(Usuario, pk=pk, tipo='cliente')
    form = ClienteForm(request.POST or None, instance=cliente)
    if form.is_valid():
        form.save()
        messages.success(request, 'Cliente atualizado!')
        return redirect('cliente_list')
    return render(request, 'clientes/form.html', {'form': form, 'title': 'Editar Cliente', 'cliente': cliente})

@somente_admin
def cliente_delete(request, pk):
    cliente = get_object_or_404(Usuario, pk=pk, tipo='cliente')
    if request.method == 'POST':
        cliente.delete()
        messages.success(request, 'Cliente removido!')
        return redirect('cliente_list')
    return render(request, 'confirm_delete.html', {'obj': cliente, 'nome': cliente.get_full_name() or cliente.username})