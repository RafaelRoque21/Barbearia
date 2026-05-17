from django.urls import path
from . import views

urlpatterns = [
    path('', views.atendimento_list, name='atendimento_list'),
    path('<int:pk>/iniciar/', views.iniciar_atendimento, name='iniciar_atendimento'),
    path('<int:pk>/finalizar/', views.finalizar_atendimento, name='finalizar_atendimento'),
]
