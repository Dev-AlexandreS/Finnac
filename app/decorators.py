# =============================================================================
# app/decorators.py
# Decorators reutilizáveis para o Finnac.
#
# O que é um decorator?
# É uma função que "envolve" outra função, adicionando comportamento antes
# ou depois dela ser executada, sem modificar o código original.
#
# Sintaxe de uso:
#   @login_required_custom
#   def minha_view(request):
#       ...
#
# Isso é equivalente a escrever:
#   minha_view = login_required_custom(minha_view)
# =============================================================================

from django.shortcuts import redirect
from functools import wraps
# functools.wraps: preserva o nome e a docstring da função original após decorar.
# Sem isso, todas as views decoradas teriam o nome "wrapper" no debug/logs.


def login_required_custom(view_func):
    """
    Decorator que protege views que requerem login.

    Como funciona:
    1. Quando a view decorada é chamada, `wrapper` é executado primeiro
    2. Verifica se 'user_id' existe na sessão do usuário
    3. Se sim: executa a view normalmente
    4. Se não: redireciona para /login/ sem executar a view

    Uso:
        @login_required_custom
        def dashboard(request):
            user_id = request.session['user_id']  # garantido que existe aqui
            ...
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        # *args e **kwargs repassam qualquer parâmetro de URL para a view
        # ex: se a view recebe `id` da URL, ele chega aqui e é repassado
        if 'user_id' in request.session:
            return view_func(request, *args, **kwargs)
        return redirect('/login/')
    return wrapper
