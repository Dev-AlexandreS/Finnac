from django.shortcuts import HttpResponse, redirect
from app import models as modelApp
import os
from django.conf import settings
from openpyxl import load_workbook
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
import fitz

def excel(request):
    if 'user_id' in request.session:
        idUser = request.session['user_id']

        user = modelApp.User.objects.get(id=idUser)

        file_path = os.path.join(settings.BASE_DIR, 'generate', 'files', 'Planilha-Finnac.xlsx')
        workbook = load_workbook(file_path)
        sheet = workbook["Planilha1"]

        sheet["C4"] = user.full_name
        sheet["C5"] = user.email

        flows = modelApp.Flow.objects.filter(id_user=idUser)
        line = 7

        for flow in flows:
            formatted_date = flow.dateBill.strftime("%d/%m/%Y")

            sheet[f"B{line}"] = flow.label_name
            sheet[f"C{line}"] = flow.tipo
            sheet[f"D{line}"] = flow.category
            sheet[f"E{line}"] = formatted_date 
            sheet[f"F{line}"] = flow.price

            line += 1
            
        buffer = BytesIO()
        workbook.save(buffer)
        buffer.seek(0)

        response = HttpResponse(buffer, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = f'attachment; filename=Planilha Finnac.xlsx'

        return response
    return redirect("/login")

def pdf(request):
    if 'user_id' in request.session:
        user_id = request.session['user_id']
        user = modelApp.User.objects.get(id=user_id)

        flows = modelApp.Flow.objects.filter(id_user=user_id)

        total_income = sum(flow.price for flow in flows if flow.tipo == "Ganho")
        total_expense = sum(flow.price for flow in flows if flow.tipo == "Despesa")
        total_balance = float(total_income) - float(total_expense)

        pdf_path = os.path.join(settings.BASE_DIR, 'generate', 'files', 'Relatório - Finnac.pdf')

        doc = fitz.open(pdf_path)

        page = doc[0]

        name_position = (128, 125)  
        email_position = (128, 148)  
        total_income_position = (163, 372) 
        total_expense_position = (165, 405) 
        total_balance_position = (163, 437)

        page.insert_text(name_position, f"{user.full_name}", fontsize=12, color=(0, 0, 0))
        page.insert_text(email_position, f"{user.email}", fontsize=12, color=(0, 0, 0))

        page.insert_text(total_income_position, f"R$ {total_income:.2f}", fontsize=16, color=(0, 0, 0))
        page.insert_text(total_expense_position, f"R$ {total_expense:.2f}", fontsize=16, color=(0, 0, 0))
        page.insert_text(total_balance_position, f"R$ {total_balance:.2f}", fontsize=16, color=(0, 0, 0))

        buffer = BytesIO()
        doc.save(buffer)
        doc.close()

        buffer.seek(0)

        response = HttpResponse(buffer, content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="Relatório Finnac.pdf"'

        return response
    return redirect("/login")