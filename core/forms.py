from django import forms
from .models import Usuario, Barbeiro

class ClienteForm(forms.ModelForm):
    password1 = forms.CharField(label='Senha', widget=forms.PasswordInput(attrs={'class': 'form-input'}), required=False)
    password2 = forms.CharField(label='Confirmar Senha', widget=forms.PasswordInput(attrs={'class': 'form-input'}), required=False)

    class Meta:
        model = Usuario
        fields = ['first_name', 'last_name', 'username', 'email', 'telefone']
        widgets = {f: forms.TextInput(attrs={'class': 'form-input'}) for f in ['first_name', 'last_name', 'username', 'telefone']}

    def clean(self):
        cleaned_data = super().clean()
        p1 = cleaned_data.get('password1')
        p2 = cleaned_data.get('password2')
        if p1 and p1 != p2:
            raise forms.ValidationError('As senhas não conferem.')
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.tipo = 'cliente'
        password = self.cleaned_data.get('password1')
        if password:
            user.set_password(password)
        if commit:
            user.save()
        return user


class BarbeiroForm(forms.ModelForm):
    class Meta:
        model = Barbeiro
        fields = ['nome', 'telefone', 'especialidade', 'status', 'horario_inicio', 'horario_fim']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-input'}),
            'telefone': forms.TextInput(attrs={'class': 'form-input'}),
            'especialidade': forms.Select(attrs={'class': 'form-select'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'horario_inicio': forms.TimeInput(attrs={'class': 'form-input', 'type': 'time'}),
            'horario_fim': forms.TimeInput(attrs={'class': 'form-input', 'type': 'time'}),
        }
        
class PerfilClienteForm(forms.ModelForm):
    password_atual = forms.CharField(
        label='Senha Atual', 
        widget=forms.PasswordInput(attrs={'class': 'form-input'}), 
        required=False
    )
    password_nova = forms.CharField(
        label='Nova Senha', 
        widget=forms.PasswordInput(attrs={'class': 'form-input'}), 
        required=False
    )
    password_confirmar = forms.CharField(
        label='Confirmar Nova Senha', 
        widget=forms.PasswordInput(attrs={'class': 'form-input'}), 
        required=False
    )

    class Meta:
        model = Usuario
        fields = ['first_name', 'last_name', 'email', 'telefone']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-input'}),
            'last_name': forms.TextInput(attrs={'class': 'form-input'}),
            'email': forms.EmailInput(attrs={'class': 'form-input'}),
            'telefone': forms.TextInput(attrs={'class': 'form-input'}),
        }
        labels = {
            'first_name': 'Nome',
            'last_name': 'Sobrenome',
            'email': 'E-mail',
            'telefone': 'Telefone',
        }

    def clean(self):
        cleaned_data = super().clean()
        atual = cleaned_data.get('password_atual')
        nova = cleaned_data.get('password_nova')
        confirmar = cleaned_data.get('password_confirmar')

        if nova or confirmar:
            if not atual:
                raise forms.ValidationError('Informe a senha atual para alterá-la.')
            if nova != confirmar:
                raise forms.ValidationError('A nova senha e a confirmação não conferem.')
            if len(nova) < 6:
                raise forms.ValidationError('A nova senha deve ter pelo menos 6 caracteres.')
        return cleaned_data