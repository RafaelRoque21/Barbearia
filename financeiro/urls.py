from django.urls import path
from . import views

urlpatterns = [
    path('', views.financeiro_dashboard, name='financeiro_dashboard'),
    path('pagamento/<int:agendamento_id>/', views.registrar_pagamento, name='registrar_pagamento'),
    path('relatorio/', views.relatorio, name='relatorio'),
]
