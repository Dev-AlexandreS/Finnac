from django.shortcuts import HttpResponse
from app import models as modelApp
import os
from django.conf import settings
from openpyxl import load_workbook
from io import BytesIO
import datetime

def excel(request):
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