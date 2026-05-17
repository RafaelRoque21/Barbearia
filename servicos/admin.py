from django.contrib import admin
from .models import Servico

@admin.register(Servico)
class ServicoAdmin(admin.ModelAdmin):
    list_display = ['nome', 'tipo', 'preco', 'duracao', 'status']
    list_filter = ['status', 'tipo']
