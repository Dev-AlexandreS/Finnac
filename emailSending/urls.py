# =============================================================================
# emailSending/urls.py
# Define as rotas do app de envio de e-mail e recuperação de senha.
#
# Este arquivo é incluído por finnac/urls.py com o prefixo 'email/'.
# Portanto as rotas ficam com os seguintes caminhos finais:
#
#   /email/                              → view `email` (gera código e envia e-mail)
#   /email/finnac/auth/recoverypassword/ → view `recoverypassword` (valida código)
#   /email/finnac/auth/editPass/         → view `editPassword` (salva nova senha)
# =============================================================================

from django.urls import path
from . import views

urlpatterns = [
    # Disparado quando o usuário clica "Trocar Senha" no perfil.
    # Gera o código, salva hash no banco e envia o e-mail.
    path('', views.email, name="email"),

    # Recebe o código de 6 dígitos e valida contra o hash no banco.
    path('finnac/auth/recoverypassword/', views.recoverypassword, name="recoverypassword"),

    # Recebe a nova senha e a confirmação e atualiza no banco.
    path('finnac/auth/editPass/', views.editPassword, name="editPassword"),
]
