# =============================================================================
# app/urls.py
# Define as rotas (URLs) do app principal do Finnac.
#
# Este arquivo é incluído pelo arquivo raiz finnac/urls.py com o prefixo ''.
# Ou seja, todas as rotas aqui são acessadas diretamente do domínio raiz.
#
# Padrão de URL do Django: path('rota/', views.funcao, name="apelido")
# - 'rota/'     → caminho na URL
# - views.funcao → função Python que será chamada quando a URL for acessada
# - name="..."  → apelido para usar com {% url 'apelido' %} nos templates
# =============================================================================

from . import views
from django.contrib import admin
from django.urls import path

urlpatterns = [
    # --- Páginas públicas (não requerem login) ---
    path('', views.home, name="home"),                  # Landing page: /
    path('login/', views.login, name="login"),           # Tela de login: /login/
    path('cadastro/', views.register, name="register"),  # Tela de cadastro: /cadastro/

    # --- Área logada ---
    path('finnac/logout/', views.logout, name="logout"),   # Destroi a sessão e desloga
    path('finnac/', views.main, name="main"),               # Dashboard com resumo financeiro
    path('finnac/wallet/', views.wallet, name="wallet"),    # Carteira: lista de lançamentos
    path('finnac/wallet/add/', views.add, name="add"),      # POST: adiciona novo lançamento
    path('delete/<int:id>', views.delete),                  # GET: deleta lançamento pelo id
    path('edit/<int:id>', views.edit, name="edit"),         # POST: edita lançamento pelo id
    path('finnac/generates/', views.generates, name="generates"),  # Página de geração de relatórios

    # --- Contas bancárias (seção do dashboard) ---
    path('finnac/accounts/add/', views.addAccount, name="addAccount"),             # POST: adiciona conta
    path('finnac/accounts/edit/', views.editAccount, name="editAccount"),           # POST: edita conta
    path('finnac/accounts/delete/<int:id>/', views.deleteAccount, name="deleteAccount"),  # GET: deleta conta

    # --- Recuperação de senha ---
    # Exibe o formulário de 6 dígitos após o envio do e-mail
    # O <int:id> é o id do usuário, usado para verificar que é a pessoa certa
    path('finnac/auth/recoverycode/<int:id>/', views.recoverycode, name="recoverycode"),

    # --- Perfil do usuário ---
    path('finnac/profile/', views.profile, name="profile"),  # GET: exibe / POST: atualiza perfil
]
