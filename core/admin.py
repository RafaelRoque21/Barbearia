from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Usuario, Barbeiro

@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    list_display = ['username', 'get_full_name', 'tipo', 'telefone', 'email']
    list_filter = ['tipo']
    fieldsets = UserAdmin.fieldsets + (
        ('Dados da Barbearia', {'fields': ('tipo', 'telefone')}),
    )

@admin.register(Barbeiro)
class BarbeiroAdmin(admin.ModelAdmin):
    list_display = ['nome', 'telefone', 'especialidade', 'status']
    list_filter = ['status', 'especialidade']
