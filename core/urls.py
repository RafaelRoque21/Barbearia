from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('dashboard/', views.dashboard, name='dashboard'),

    # Portal do cliente
    path('minha-area/', views.cliente_portal, name='cliente_portal'),
    path('minha-area/agendar/', views.cliente_agendar, name='cliente_agendar'),
    path('minha-area/historico/', views.cliente_historico, name='cliente_historico'),
    path('minha-area/horarios/', views.cliente_horarios, name='cliente_horarios'),
    path('minha-area/perfil/', views.cliente_perfil, name='cliente_perfil'),
    path('minha-area/cancelar/<int:pk>/', views.cliente_cancelar_agendamento, name='cliente_cancelar_agendamento'),

    # Admin
    path('barbeiros/', views.barbeiro_list, name='barbeiro_list'),
    path('barbeiros/novo/', views.barbeiro_create, name='barbeiro_create'),
    path('barbeiros/<int:pk>/editar/', views.barbeiro_edit, name='barbeiro_edit'),
    path('barbeiros/<int:pk>/excluir/', views.barbeiro_delete, name='barbeiro_delete'),
    path('clientes/', views.cliente_list, name='cliente_list'),
    path('clientes/novo/', views.cliente_create, name='cliente_create'),
    path('clientes/<int:pk>/editar/', views.cliente_edit, name='cliente_edit'),
    path('clientes/<int:pk>/excluir/', views.cliente_delete, name='cliente_delete'),
]