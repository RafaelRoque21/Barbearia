from django.contrib import admin
from .models import Agendamento

@admin.register(Agendamento)
class AgendamentoAdmin(admin.ModelAdmin):
    list_display = ['cliente', 'servico', 'barbeiro', 'data', 'horario', 'status']
    list_filter = ['status', 'data']
    date_hierarchy = 'data'
