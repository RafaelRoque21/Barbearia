from django import forms
from .models import Servico

class ServicoForm(forms.ModelForm):
    class Meta:
        model = Servico
        fields = ['nome', 'tipo', 'preco', 'duracao', 'descricao', 'status']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-input'}),
            'tipo': forms.Select(attrs={'class': 'form-select'}),
            'preco': forms.NumberInput(attrs={'class': 'form-input', 'step': '0.01'}),
            'duracao': forms.NumberInput(attrs={'class': 'form-input'}),
            'descricao': forms.Textarea(attrs={'class': 'form-textarea', 'rows': 3}),
            'status': forms.Select(attrs={'class': 'form-select'}),
        }
