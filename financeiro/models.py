from django.db import models
from agendamento.models import Agendamento

class Pagamento(models.Model):
    MODALIDADE_CHOICES = [
        ('pix', 'Pix'),
        ('credito', 'Crédito'),
        ('debito', 'Débito'),
        ('dinheiro', 'Dinheiro'),
    ]

    agendamento = models.OneToOneField(Agendamento, on_delete=models.CASCADE, related_name='pagamento')
    modalidade = models.CharField(max_length=10, choices=MODALIDADE_CHOICES)
    valor = models.DecimalField(max_digits=8, decimal_places=2)
    pago_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Pagamento'
        verbose_name_plural = 'Pagamentos'

    def __str__(self):
        return f"Pagamento #{self.id} — {self.get_modalidade_display()} — R$ {self.valor}"
