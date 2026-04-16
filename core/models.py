from django.db import models
from django.contrib.auth.models import AbstractUser

class Usuario(AbstractUser):
    TIPO_CHOICES = [
        ('admin', 'Administrador'),
        ('cliente', 'Cliente'),
        ('barbeiro', 'Barbeiro'),
    ]
    tipo = models.CharField(max_length=10, choices=TIPO_CHOICES, default='cliente')
    telefone = models.CharField(max_length=20, blank=True)

    class Meta:
        verbose_name = 'Usuário'
        verbose_name_plural = 'Usuários'

    def __str__(self):
        return f"{self.get_full_name() or self.username} ({self.get_tipo_display()})"


class Barbeiro(models.Model):
    ESPECIALIDADE_CHOICES = [
        ('cabelo', 'Cabelo'),
        ('barba', 'Barba'),
        ('sobrancelha', 'Sobrancelha'),
    ]
    STATUS_CHOICES = [
        ('ativo', 'Ativo'),
        ('inativo', 'Inativo'),
    ]

    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE, related_name='barbeiro', null=True, blank=True)
    nome = models.CharField(max_length=100)
    telefone = models.CharField(max_length=20)
    especialidade = models.CharField(max_length=20, choices=ESPECIALIDADE_CHOICES)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='ativo')
    horario_inicio = models.TimeField(default='08:00')
    horario_fim = models.TimeField(default='18:00')
    foto = models.ImageField(upload_to='barbeiros/', blank=True, null=True)

    class Meta:
        verbose_name = 'Barbeiro'
        verbose_name_plural = 'Barbeiros'

    def __str__(self):
        return self.nome
