#!/bin/bash
echo "================================================"
echo "  BarberOS — Setup do Sistema"
echo "================================================"

# Verificar Python
python3 --version || { echo "Python3 não encontrado!"; exit 1; }

# Criar venv
echo "Criando ambiente virtual..."
python3 -m venv venv
source venv/bin/activate

# Instalar dependências
echo "Instalando dependências..."
pip install -r requirements.txt

# Migrações
echo "Aplicando migrações..."
python manage.py migrate

# Dados de exemplo (opcional)
read -p "Deseja criar dados de exemplo? (s/n): " resp
if [ "$resp" = "s" ]; then
    python manage.py shell << 'PYEOF'
from django.contrib.auth import get_user_model
from core.models import Barbeiro
from servicos.models import Servico
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    u = User.objects.create_superuser('admin', 'admin@barberos.com', 'admin123')
    u.tipo = 'admin'
    u.save()
    print("Superusuário criado: admin / admin123")
else:
    print("Superusuário já existe.")
PYEOF
fi

echo ""
echo "================================================"
echo "  Setup concluído!"
echo "  Rode: source venv/bin/activate"
echo "        python manage.py runserver"
echo "  Acesse: http://127.0.0.1:8000"
echo "  Login:  admin / admin123"
echo "================================================"
