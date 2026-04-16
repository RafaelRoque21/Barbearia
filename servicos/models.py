from django.db import models

class Servico(models.Model):
    TIPO_CHOICES = [
        ('cabelo', 'Cabelo'),
        ('barba', 'Barba'),
        ('sobrancelha', 'Sobrancelha'),
    ]
    STATUS_CHOICES = [
        ('ativo', 'Ativo'),
        ('inativo', 'Inativo'),
    ]

    nome = models.CharField(max_length=100)
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    preco = models.DecimalField(max_digits=8, decimal_places=2)
    duracao = models.PositiveIntegerField(help_text='Duração em minutos')
    descricao = models.TextField(blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='ativo')

    class Meta:
        verbose_name = 'Serviço'
        verbose_name_plural = 'Serviços'

    def __str__(self):
        return f"{self.nome} — R$ {self.preco}"
