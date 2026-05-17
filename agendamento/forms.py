from django import forms
from .models import Agendamento
from core.models import Usuario, Barbeiro
from servicos.models import Servico

class AgendamentoForm(forms.ModelForm):
    class Meta:
        model = Agendamento
        fields = ['cliente', 'servico', 'barbeiro', 'data', 'horario', 'preco', 'status', 'observacao']
        widgets = {
            'cliente': forms.Select(attrs={'class': 'form-select'}),
            'servico': forms.Select(attrs={'class': 'form-select'}),
            'barbeiro': forms.Select(attrs={'class': 'form-select'}),
            'data': forms.DateInput(attrs={'class': 'form-input', 'type': 'date'}),
            'horario': forms.TimeInput(attrs={'class': 'form-input', 'type': 'time'}),
            'preco': forms.NumberInput(attrs={'class': 'form-input', 'step': '0.01'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'observacao': forms.Textarea(attrs={'class': 'form-textarea', 'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['cliente'].queryset = Usuario.objects.filter(tipo='cliente')
        self.fields['barbeiro'].queryset = Barbeiro.objects.filter(status='ativo')
        self.fields['servico'].queryset = Servico.objects.filter(status='ativo')

from .models import Agendamento, HorarioBloqueado

class HorarioBloqueadoForm(forms.ModelForm):
    class Meta:
        model = HorarioBloqueado
        fields = ['barbeiro', 'tipo', 'data', 'horario_inicio', 'horario_fim', 'motivo']
        widgets = {
            'barbeiro': forms.Select(attrs={'class': 'form-select'}),
            'tipo': forms.Select(attrs={'class': 'form-select'}),
            'data': forms.DateInput(attrs={'class': 'form-input', 'type': 'date'}),
            'horario_inicio': forms.TimeInput(attrs={'class': 'form-input', 'type': 'time'}),
            'horario_fim': forms.TimeInput(attrs={'class': 'form-input', 'type': 'time'}),
            'motivo': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Ex: Feriado, Férias, Almoço'}),
        }
        labels = {
            'barbeiro': 'Barbeiro (vazio = todos)',
            'tipo': 'Tipo de Bloqueio',
            'data': 'Data',
            'horario_inicio': 'Horário Início',
            'horario_fim': 'Horário Fim',
            'motivo': 'Motivo',
        }

    def clean(self):
        cleaned_data = super().clean()
        tipo = cleaned_data.get('tipo')
        inicio = cleaned_data.get('horario_inicio')
        fim = cleaned_data.get('horario_fim')

        if tipo == 'horario':
            if not inicio or not fim:
                raise forms.ValidationError('Para bloqueio por horário, informe o início e o fim.')
            if inicio >= fim:
                raise forms.ValidationError('O horário de início deve ser antes do fim.')
        return cleaned_data