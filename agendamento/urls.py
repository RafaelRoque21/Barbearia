from django.urls import path
from . import views

urlpatterns = [
    path('', views.agendamento_list, name='agendamento_list'),
    path('novo/', views.agendamento_create, name='agendamento_create'),
    path('<int:pk>/', views.agendamento_detail, name='agendamento_detail'),
    path('<int:pk>/editar/', views.agendamento_edit, name='agendamento_edit'),
    path('<int:pk>/cancelar/', views.agendamento_cancelar, name='agendamento_cancelar'),
    path('agenda/', views.agenda_view, name='agenda'),
    path('bloqueios/', views.horario_bloqueado_list, name='horario_bloqueado_list'),
    path('bloqueios/novo/', views.horario_bloqueado_create, name='horario_bloqueado_create'),
    path('bloqueios/<int:pk>/excluir/', views.horario_bloqueado_delete, name='horario_bloqueado_delete'),
]
