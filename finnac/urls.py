# =============================================================================
# finnac/urls.py  (arquivo raiz de URLs)
# Ponto de entrada de todas as rotas do projeto Finnac.
#
# O Django usa ROOT_URLCONF = 'finnac.urls' (definido em settings.py) para
# saber qual arquivo de URLs processar primeiro em cada requisição.
#
# As rotas são distribuídas para os apps com `include()`:
#
#   ''         → app.urls      (rotas principais: home, login, dashboard, carteira...)
#   'email/'   → emailSending.urls  (envio de e-mail e recuperação de senha)
#   'generate/'→ generate.urls      (download de relatórios Excel e PDF)
#
# Por que separar em apps?
# Cada app tem sua responsabilidade bem definida (Single Responsibility Principle).
# Isso facilita manutenção e permite incluir ou excluir funcionalidades sem afetar o restante.
# =============================================================================

from django.urls import path, include

urlpatterns = [
    # Rotas do app principal (home, login, cadastro, dashboard, carteira, perfil...)
    # prefixo vazio: as URLs do app ficam na raiz do domínio (ex: /login/, /finnac/)
    path('', include('app.urls')),

    # Rotas de recuperação de senha por e-mail
    # ex: /email/ → dispara o envio do código
    #     /email/finnac/auth/recoverypassword/ → valida o código
    path('email/', include('emailSending.urls')),

    # Rotas de geração de relatórios
    # ex: /generate/excel/ → download da planilha
    #     /generate/pdf/   → download do PDF
    path('generate/', include('generate.urls')),
]
