from django.db import models
from agendamento.models import Agendamento

class Atendimento(models.Model):
    """Registra informações do atendimento realizado."""
    
    agendamento = models.OneToOneField(
        Agendamento,
        on_delete=models.CASCADE,
        related_name='atendimento'
    )
    
    iniciado_em = models.DateTimeField(auto_now_add=True)
    finalizado_em = models.DateTimeField(null=True, blank=True)
    observacao = models.TextField(blank=True)
    
    class Meta:
        verbose_name = 'Atendimento'
        verbose_name_plural = 'Atendimentos'
        ordering = ['-iniciado_em']
    
    def __str__(self):
        return f"Atendimento - {self.agendamento.cliente.get_full_name()} - {self.iniciado_em.strftime('%d/%m %H:%M')}"
