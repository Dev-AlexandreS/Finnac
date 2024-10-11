from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.conf import settings
from django.shortcuts import render, HttpResponse

def email(request):
    context = {
        'subject': 'Bem-vindo ao nosso site!',
        'username': 'Usuário'
    }


    email_html_message = render_to_string('email_template.html', context)

    email = EmailMessage(
        subject='Assunto do E-mail',
        body=email_html_message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=['email@gmail.com']
    )

    email.content_subtype = 'html'

    email.send()
    return HttpResponse("Pronto")