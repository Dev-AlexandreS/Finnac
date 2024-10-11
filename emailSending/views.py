from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.contrib.auth.models import User  # ou o caminho correto se você tiver um User personalizado
from django.conf import settings
from django.contrib import messages
from app import models as modelApp
from .models import RecoveryPass
from django.shortcuts import render, HttpResponse, redirect
import random

def email(request):
    user_id = request.session['user_id']
    
    recovery_code = str(random.randint(100000, 999999))

    try:
        user_instance = modelApp.User.objects.get(id=user_id)
        RecoveryPass.objects.filter(id_user=user_instance).delete() 

        recovery_pass = RecoveryPass(id_user=user_instance)
        recovery_pass.set_code(recovery_code)
        recovery_pass.save()
    except modelApp.User.DoesNotExist:
        return HttpResponse("Usuário não encontrado")
  


    context = {
        'subject': 'Bem-vindo à Finnac!',
        'username': user_instance.full_name,
        'recoverycode': recovery_code
    }

    email_html_message = render_to_string('email_template.html', context)

    email = EmailMessage(
        subject='Recuperação de senha',
        body=email_html_message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=["user@gmail.com"]  # Use o email do usuário
    )

    email.content_subtype = 'html'

    try:
        email.send()
    except Exception as e:
        return HttpResponse(f"Erro ao enviar o email: {str(e)}")

    return redirect(f"/finnac/auth/recoverycode/{user_instance.id}")

def recoverypassword(request):
    if request.method == "POST":
        user_id = request.session.get('user_id')
        c1 = request.POST.get('c1', '')
        c2 = request.POST.get('c2', '')
        c3 = request.POST.get('c3', '')
        c4 = request.POST.get('c4', '')
        c5 = request.POST.get('c5', '')
        c6 = request.POST.get('c6', '')
        code = c1 + c2 + c3 + c4 + c5 + c6

        if len(code) != 6:
            messages.error(request, "Código deve ter 6 dígitos.")
            return redirect('/finnac/auth/recoverycode/{user_id}')

        
        recovery_pass = RecoveryPass.objects.get(id_user=user_id)
        if recovery_pass.check_code(code):
            return render(request, "recoveryPassword.html")
        else:
            messages.error(request, "Código incorreto.")
            return redirect(f"/finnac/auth/recoverycode/{user_id}")
        
    return HttpResponse("Painel privado")
