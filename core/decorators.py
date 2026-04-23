from functools import wraps
from django.http import HttpResponseForbidden

def somente_admin(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated or request.user.tipo == 'cliente':
            return HttpResponseForbidden('''
                <!DOCTYPE html>
                <html>
                <head>
                  <meta charset="UTF-8">
                  <script src="https://cdn.tailwindcss.com"></script>
                  <link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700&family=DM+Sans:wght@400;500&display=swap" rel="stylesheet">
                </head>
                <body style="background:#0D0D0D;font-family:DM Sans,sans-serif" class="min-h-screen flex items-center justify-center">
                  <div class="text-center">
                    <div class="text-6xl mb-4">🔒</div>
                    <h1 style="font-family:Playfair Display,serif;color:#C9A84C" class="text-4xl font-bold mb-2">Acesso Negado</h1>
                    <p style="color:#6b7280" class="mb-6">Você não tem permissão para acessar esta página.</p>
                    <a href="/" style="background:linear-gradient(135deg,#C9A84C,#8B6914);color:#0D0D0D;padding:0.6rem 1.5rem;border-radius:8px;font-weight:600;text-decoration:none">
                      Voltar ao início
                    </a>
                  </div>
                </body>
                </html>
            ''')
        return view_func(request, *args, **kwargs)
    return wrapper