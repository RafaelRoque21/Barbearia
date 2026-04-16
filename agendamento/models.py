from django.db import models
from core.models import Usuario, Barbeiro
from servicos.models import Servico

class Agendamento(models.Model):
    STATUS_CHOICES = [
        ('pendente', 'Pendente'),
        ('confirmado', 'Confirmado'),
        ('cancelado', 'Cancelado'),
        ('concluido', 'Concluído'),
    ]

    cliente = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='agendamentos', limit_choices_to={'tipo': 'cliente'})
    servico = models.ForeignKey(Servico, on_delete=models.CASCADE)
    barbeiro = models.ForeignKey(Barbeiro, on_delete=models.CASCADE)
    data = models.DateField()
    horario = models.TimeField()
    preco = models.DecimalField(max_digits=8, decimal_places=2)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='pendente')
    observacao = models.TextField(blank=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Agendamento'
        verbose_name_plural = 'Agendamentos'
        ordering = ['data', 'horario']

    def __str__(self):
        return f"{self.cliente.get_full_name() or self.cliente.username} — {self.servico.nome} em {self.data} às {self.horario}"

class HorarioBloqueado(models.Model):
    TIPO_CHOICES = [
        ('dia', 'Dia Inteiro'),
        ('horario', 'Horário Específico'),
    ]

    barbeiro = models.ForeignKey(Barbeiro, on_delete=models.CASCADE, related_name='horarios_bloqueados', null=True, blank=True, help_text='Deixe vazio para bloquear todos os barbeiros')
    tipo = models.CharField(max_length=10, choices=TIPO_CHOICES, default='dia')
    data = models.DateField()
    horario_inicio = models.TimeField(null=True, blank=True, help_text='Obrigatório para tipo Horário Específico')
    horario_fim = models.TimeField(null=True, blank=True, help_text='Obrigatório para tipo Horário Específico')
    motivo = models.CharField(max_length=200, blank=True, help_text='Ex: Feriado, Férias, Almoço')
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Horário Bloqueado'
        verbose_name_plural = 'Horários Bloqueados'
        ordering = ['data', 'horario_inicio']

    def __str__(self):
        if self.tipo == 'dia':
            alvo = self.barbeiro.nome if self.barbeiro else 'Todos os barbeiros'
            return f'{alvo} — {self.data} (dia inteiro) — {self.motivo}'
        return f'{self.barbeiro.nome if self.barbeiro else "Todos"} — {self.data} {self.horario_inicio}–{self.horario_fim} — {self.motivo}'