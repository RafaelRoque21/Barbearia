# BarberOS — Sistema de Gestão para Barbearias

## Requisitos
- Python 3.10+
- pip

## Instalação Rápida

```bash
# 1. Instale as dependências
pip install -r requirements.txt

# 2. Aplique as migrações
python manage.py migrate

# 3. Inicie o servidor
python manage.py runserver
```

Acesse: http://127.0.0.1:8000
Login: `admin` / `admin123`

## Módulos do MVP

| Módulo | URL | Descrição |
|--------|-----|-----------|
| Dashboard | `/dashboard/` | Visão geral |
| Agendamentos | `/agendamentos/` | CRUD de agendamentos |
| Agenda | `/agendamentos/agenda/` | Visualização semanal |
| Clientes | `/clientes/` | Cadastro de clientes |
| Barbeiros | `/barbeiros/` | Cadastro de barbeiros |
| Serviços | `/servicos/` | Cadastro de serviços |
| Atendimento | `/atendimento/` | Fila do dia |
| Financeiro | `/financeiro/` | Ganhos e pagamentos |
| Relatórios | `/financeiro/relatorio/` | Relatório geral |
| Admin Django | `/admin/` | Painel administrativo |

## Estrutura do Projeto

```
barbearia/          # Configurações Django
core/               # Usuários e Barbeiros
servicos/           # Módulo de Serviços
agendamento/        # Módulo de Agendamentos + Agenda
atendimento/        # Módulo de Atendimento
financeiro/         # Módulo Financeiro + Relatórios
templates/          # Templates HTML (Tailwind CSS)
```

## Usuários de Teste
| Usuário | Senha | Tipo |
|---------|-------|------|
| admin | admin123 | Administrador |
| joao.silva | cliente123 | Cliente |
| maria.santos | cliente123 | Cliente |
"# Barbearia-1.5" 
