# =============================================================================
# generate/urls.py
# Define as rotas do app de geração de relatórios.
#
# Este arquivo é incluído por finnac/urls.py com o prefixo 'generate/'.
# Portanto os caminhos finais são:
#
#   /generate/excel/  → baixa planilha Excel com os dados do usuário
#   /generate/pdf/    → baixa PDF com o resumo financeiro do usuário
# =============================================================================

from django.urls import path
from . import views

urlpatterns = [
    # Gera e retorna o arquivo Excel preenchido com os lançamentos do usuário
    path('excel/', views.excel, name="excel"),

    # Gera e retorna o PDF com totais de receitas, despesas e balanço
    path('pdf/', views.pdf, name="pdf"),
]
