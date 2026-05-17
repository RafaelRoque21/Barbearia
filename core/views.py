from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.contrib import messages
from .models import Usuario, Barbeiro
from .forms import ClienteForm, BarbeiroForm, PerfilClienteForm
from agendamento.models import Agendamento, HorarioBloqueado
from servicos.models import Servico
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
                data_obj = dt.date.fromisoformat(data)
                if data_obj < dt.date.today():
                    erros.append('A data não pode ser no passado.')
            except ValueError:
                erros.append('Data inválida.')

        if not erros:
            servico = get_object_or_404(Servico, pk=servico_id)
            barbeiro = get_object_or_404(Barbeiro, pk=barbeiro_id)

            # Verificar conflito de horário
            conflito = Agendamento.objects.filter(
                barbeiro=barbeiro,
                data=data,
                horario=horario,
                status__in=['pendente', 'confirmado']
            ).exists()
            if conflito:
                erros.append('Este horário já está ocupado. Escolha outro.')

            # Verificar bloqueios
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

    barbeiros = Barbeiro.objects.filter(status='ativo')
    barbeiro_id = request.GET.get('barbeiro')
    data_str = request.GET.get('data', dt.date.today().isoformat())

    try:
        data = dt.date.fromisoformat(data_str)
    except ValueError:
        data = dt.date.today()

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
        hora = dt.datetime.combine(data, barbeiro_sel.horario_inicio)
        fim = dt.datetime.combine(data, barbeiro_sel.horario_fim)
        while hora < fim:
            horarios.append({
                'hora': hora.time(),
                'ocupado': hora.time() in ocupados,
            })
            hora += dt.timedelta(minutes=30)

    return render(request, 'portal/horarios.html', {
        'barbeiros': barbeiros,
        'barbeiro_sel': barbeiro_sel,
        'horarios': horarios,
        'data': data,
        'hoje': dt.date.today().isoformat(),
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
    hoje = dt.date.today()
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

def obter_ip_cliente(request) -> str:
    """Obter IP real do cliente."""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


@csrf_exempt
def api_chat(request):
    """Endpoint da API para o chatbot."""
    
    if request.method != 'POST':
        return JsonResponse({'erro': 'Método não permitido'}, status=405)
    
    try:
        # Extrair JSON
        dados = json.loads(request.body)
        mensagem = dados.get('mensagem', '').strip()
        historico = dados.get('historico', [])

        # Validação
        if not mensagem:
            return JsonResponse({'erro': 'Mensagem vazia'}, status=400)

        if len(mensagem) > 1000:
            return JsonResponse({'erro': 'Mensagem muito longa'}, status=400)

        # Gerar resposta com IA
        resposta = gerar_resposta_chatbot(
            mensagem=mensagem,
            historico=historico
        )

        # Salvar no banco
        usuario = request.user if request.user.is_authenticated else None
        ConversaWebsite.objects.create(
            usuario=usuario,
            mensagem_entrada=mensagem,
            mensagem_saida=resposta,
            ip_visitante=obter_ip_cliente(request)
        )

        # Retornar resposta
        return JsonResponse({
            'resposta': resposta,
            'sucesso': True
        })

    except json.JSONDecodeError:
        return JsonResponse({'erro': 'JSON inválido'}, status=400)
    except Exception as e:
        print(f"❌ Erro no chat: {e}")
        return JsonResponse({'erro': 'Erro interno'}, status=500)
    
def cadastro_cliente(request):
    """
    View para cadastro de novos clientes.
    """
    if request.method == 'POST':
        nome = request.POST.get('first_name', '').strip()
        sobrenome = request.POST.get('last_name', '').strip()
        email = request.POST.get('email', '').strip()
        telefone = request.POST.get('telefone', '').strip()
        username = request.POST.get('username', '').strip()
        senha1 = request.POST.get('senha1', '').strip()
        senha2 = request.POST.get('senha2', '').strip()

        # Validações
        erros = []

        if not all([nome, sobrenome, email, username, senha1, senha2]):
            erros.append('Todos os campos são obrigatórios.')

        if len(username) < 3:
            erros.append('Username deve ter pelo menos 3 caracteres.')

        if len(senha1) < 6:
            erros.append('Senha deve ter pelo menos 6 caracteres.')

        if senha1 != senha2:
            erros.append('As senhas não conferem.')

        if Usuario.objects.filter(username=username).exists():
            erros.append('Este username já está em uso.')

        if Usuario.objects.filter(email=email).exists():
            erros.append('Este email já está cadastrado.')

        if erros:
            for erro in erros:
                messages.error(request, erro)
            return render(request, 'cadastro.html', {
                'form_data': request.POST
            })

        # Criar usuário
        try:
            usuario = Usuario.objects.create_user(
                username=username,
                email=email,
                password=senha1,
                first_name=nome,
                last_name=sobrenome,
                telefone=telefone,
                tipo='cliente'  # Sempre cliente no cadastro
            )

            messages.success(request, 'Cadastro realizado com sucesso! Faça login.')
            
            # Fazer login automático (opcional)
            usuario = authenticate(request, username=username, password=senha1)
            if usuario:
                login(request, usuario)
                return redirect('cliente_portal')
            
            return redirect('login')

        except Exception as e:
            messages.error(request, f'Erro ao criar usuário: {str(e)}')
            return render(request, 'cadastro.html', {'form_data': request.POST})

    return render(request, 'cadastro.html')