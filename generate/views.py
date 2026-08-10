# =============================================================================
# generate/views.py
# Responsável por gerar e entregar os relatórios financeiros do usuário
# nos formatos Excel (.xlsx) e PDF.
#
# Nenhum model é necessário aqui — os dados vêm de app.Flow e app.User,
# e os arquivos template ficam em generate/files/.
#
# Bibliotecas usadas:
#   openpyxl → leitura e escrita de arquivos Excel (.xlsx)
#   PyMuPDF (fitz) → manipulação de PDFs (inserção de texto em posições fixas)
#   io.BytesIO → buffer em memória para não precisar salvar arquivo no disco
# =============================================================================

from django.shortcuts import HttpResponse, redirect
from app import models as modelApp  # acessa User, Flow e Accounts
import os
from django.conf import settings     # para construir caminhos com BASE_DIR
from openpyxl import load_workbook   # abre o template .xlsx
from io import BytesIO               # buffer em memória para o arquivo gerado
from reportlab.pdfgen import canvas  # importado mas NÃO usado (sobra de versão anterior)
from reportlab.lib.pagesizes import A4  # importado mas NÃO usado
import fitz  # PyMuPDF: leitura e edição de PDFs


# -----------------------------------------------------------------------------
# View: excel
# Rota: GET /generate/excel/
# Requer login (verifica 'user_id' na sessão).
#
# Como funciona:
# 1. Abre o arquivo template "Planilha-Finnac.xlsx" de generate/files/
# 2. Preenche células fixas com nome e e-mail do usuário (C4, C5)
# 3. Itera todos os lançamentos (Flow) do usuário a partir da linha 7:
#    B = nome, C = tipo, D = categoria, E = data (dd/mm/yyyy), F = valor
# 4. Salva o workbook em memória (BytesIO) sem gravar em disco
# 5. Retorna como resposta HTTP com content-type correto para download
#
# Por que BytesIO? Evita criar arquivos temporários no servidor e é mais rápido.
# -----------------------------------------------------------------------------
def excel(request):
    if 'user_id' in request.session:
        idUser = request.session['user_id']

        user = modelApp.User.objects.get(id=idUser)

        # caminho absoluto para o arquivo template Excel
        file_path = os.path.join(settings.BASE_DIR, 'generate', 'files', 'Planilha-Finnac.xlsx')
        workbook = load_workbook(file_path)
        sheet = workbook["Planilha1"]  # acessa a aba específica do template

        # preenche as células de identificação do usuário no cabeçalho
        sheet["C4"] = user.full_name
        sheet["C5"] = user.email

        # busca todos os lançamentos do usuário
        flows = modelApp.Flow.objects.filter(id_user=idUser)
        line = 7  # linha inicial dos dados na planilha (1 a 6 são cabeçalho)

        for flow in flows:
            # converte a data de "YYYY-MM-DD" (banco) para "DD/MM/YYYY" (planilha)
            formatted_date = flow.dateBill.strftime("%d/%m/%Y")

            sheet[f"B{line}"] = flow.label_name  # nome do lançamento
            sheet[f"C{line}"] = flow.tipo         # tipo: Ganho, Despesa, Transferências
            sheet[f"D{line}"] = flow.category     # categoria
            sheet[f"E{line}"] = formatted_date    # data formatada
            sheet[f"F{line}"] = flow.price        # valor

            line += 1  # avança para a próxima linha
            
        # salva o arquivo preenchido em memória
        buffer = BytesIO()
        workbook.save(buffer)
        buffer.seek(0)  # volta o ponteiro ao início do buffer para leitura

        # retorna o arquivo como download
        response = HttpResponse(
            buffer,
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = f'attachment; filename=Planilha Finnac.xlsx'

        return response
    
    return redirect("/login")


# -----------------------------------------------------------------------------
# View: pdf
# Rota: GET /generate/pdf/
# Requer login (verifica 'user_id' na sessão).
#
# Como funciona:
# 1. Abre o arquivo template "Relatório - Finnac.pdf" de generate/files/
# 2. Calcula totais de receitas, despesas e balanço a partir dos Flow
# 3. Usa PyMuPDF para inserir texto em posições hardcoded na primeira página
# 4. Salva o PDF editado em memória (BytesIO) e retorna como download
#
# Posições de texto na página (em pontos PDF, eixo Y invertido):
#   Nome do usuário:      (128, 125)
#   E-mail do usuário:    (128, 148)
#   Total receitas:       (163, 372)
#   Total despesas:       (165, 405)
#   Balanço total:        (163, 437)
#
# ⚠️ As posições são fixas e dependem do layout exato do PDF template.
# Qualquer mudança no template quebra o posicionamento do texto.
# -----------------------------------------------------------------------------
def pdf(request):
    if 'user_id' in request.session:
        user_id = request.session['user_id']
        user = modelApp.User.objects.get(id=user_id)

        flows = modelApp.Flow.objects.filter(id_user=user_id)

        # calcula os totais iterando pelos lançamentos em Python
        # (não usa aggregate do Django para manter o código simples)
        total_income = sum(flow.price for flow in flows if flow.tipo == "Ganho")
        total_expense = sum(flow.price for flow in flows if flow.tipo == "Despesa")
        total_balance = float(total_income) - float(total_expense)

        # caminho absoluto para o PDF template
        pdf_path = os.path.join(settings.BASE_DIR, 'generate', 'files', 'Relatório - Finnac.pdf')

        # abre o PDF template com PyMuPDF
        doc = fitz.open(pdf_path)
        page = doc[0]  # usa apenas a primeira página

        # coordenadas (x, y) em pontos para cada campo do relatório
        name_position = (128, 125)             # campo: nome do usuário
        email_position = (128, 148)            # campo: e-mail do usuário
        total_income_position = (163, 372)     # campo: total de receitas
        total_expense_position = (165, 405)    # campo: total de despesas
        total_balance_position = (163, 437)    # campo: balanço final

        # insere os textos nas posições definidas acima
        page.insert_text(name_position, f"{user.full_name}", fontsize=12, color=(0, 0, 0))
        page.insert_text(email_position, f"{user.email}", fontsize=12, color=(0, 0, 0))

        page.insert_text(total_income_position, f"R$ {total_income:.2f}", fontsize=16, color=(0, 0, 0))
        page.insert_text(total_expense_position, f"R$ {total_expense:.2f}", fontsize=16, color=(0, 0, 0))
        page.insert_text(total_balance_position, f"R$ {total_balance:.2f}", fontsize=16, color=(0, 0, 0))

        # salva o PDF editado em memória
        buffer = BytesIO()
        doc.save(buffer)
        doc.close()  # fecha o documento PyMuPDF para liberar recursos

        buffer.seek(0)

        # retorna o PDF como download
        response = HttpResponse(buffer, content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="Relatório Finnac.pdf"'

        return response
    
    return redirect("/login")
