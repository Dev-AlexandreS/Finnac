# =============================================================================
# emailSending/views.py
# Responsável por todo o fluxo de recuperação de senha do Finnac.
#
# Fluxo completo:
# 1. Usuário clica "Trocar Senha" no perfil → acessa /email/
# 2. Sistema gera código de 6 dígitos, salva hash no banco, envia e-mail HTML
# 3. Usuário é redirecionado para /finnac/auth/recoverycode/<id>/
# 4. Usuário preenche os 6 campos com o código recebido → POST para /finnac/auth/recoverypassword/
# 5. Sistema valida o hash → se correto, renderiza tela de nova senha
# 6. Usuário digita nova senha → POST para /finnac/auth/editPass/
# 7. Nova senha é salva hasheada → usuário retorna ao perfil
# =============================================================================

from django.core.mail import EmailMessage            # classe para montar e enviar e-mails
from django.template.loader import render_to_string  # renderiza template HTML para string
from django.contrib.auth.models import User          # importado mas NÃO usado (sobra do início)
from django.conf import settings                     # acessa EMAIL_HOST, DEFAULT_FROM_EMAIL etc.
from django.contrib import messages                  # flash messages para o template
from app import models as modelApp                   # User e outros models do app principal
from .models import RecoveryPass                     # model do código de recuperação
from django.shortcuts import render, HttpResponse, redirect
import random                                        # geração do código aleatório
from django.contrib.auth import update_session_auth_hash
# update_session_auth_hash: após trocar a senha, atualiza o hash da sessão para
# evitar que o usuário seja deslogado automaticamente pelo Django


# -----------------------------------------------------------------------------
# View: email
# Rota: GET /email/
#
# Disparada quando o usuário clica em "Trocar Senha" no perfil.
# O que faz:
# 1. Pega o id do usuário logado da sessão
# 2. Gera um código aleatório de 6 dígitos (ex: "482931")
# 3. Deleta qualquer código anterior desse usuário no banco (garante unicidade)
# 4. Cria novo RecoveryPass, hasheia o código com set_code() e salva
# 5. Monta o e-mail HTML usando o template email_template.html
# 6. Envia via SMTP (configurado em settings.py: smtp.hostinger.com:465)
# 7. Redireciona o usuário para a tela de inserção do código
# -----------------------------------------------------------------------------
def email(request):
    user_id = request.session['user_id']
    
    # gera código numérico de 6 dígitos (100000 a 999999)
    recovery_code = str(random.randint(100000, 999999))

    try:
        user_instance = modelApp.User.objects.get(id=user_id)
        
        # remove o código anterior deste usuário para evitar ter dois registros
        # (unique=True no banco também impediria, mas isso evita o erro de violação de constraint)
        RecoveryPass.objects.filter(id_user=user_instance).delete()

        # cria novo código com o hash
        recovery_pass = RecoveryPass(id_user=user_instance)
        recovery_pass.set_code(recovery_code)  # hasheia antes de salvar
        recovery_pass.save()
    except modelApp.User.DoesNotExist:
        return HttpResponse("Usuário não encontrado")

    # dados enviados para o template do e-mail
    context = {
        'subject': 'Bem-vindo à Finnac!',       # título exibido no corpo do e-mail
        'username': user_instance.full_name,     # nome do usuário para saudação
        'recoverycode': recovery_code            # código em texto claro (só vai no e-mail, não no banco)
    }

    # renderiza o template HTML do e-mail como string para usar no corpo
    email_html_message = render_to_string('email_template.html', context)

    # monta o e-mail com assunto, corpo HTML, remetente e destinatário
    email = EmailMessage(
        subject='Recuperação de senha',
        body=email_html_message,
        from_email=settings.DEFAULT_FROM_EMAIL,  # noreply@ccode.com.br
        to=[user_instance.email]                 # e-mail do usuário cadastrado
    )

    email.content_subtype = 'html'  # define que o corpo é HTML, não texto simples

    try:
        email.send()
    except Exception as e:
        # se o envio falhar (ex: SMTP fora do ar), mostra o erro para debug
        return HttpResponse(f"Erro ao enviar o email: {str(e)}")

    # redireciona para a tela onde o usuário digita o código recebido
    return redirect(f"/finnac/auth/recoverycode/{user_instance.id}")


# -----------------------------------------------------------------------------
# View: recoverypassword
# Rota: POST /finnac/auth/recoverypassword/
#
# Recebe os 6 dígitos do código vindos de 6 inputs separados (c1 a c6),
# monta o código completo, busca o hash no banco e compara.
#
# Por que 6 inputs separados?
# UX: facilita a digitação e permite auto-avançar para o próximo campo com JS.
#
# ⚠️ Bug identificado: o redirect de erro usa '{user_id}' sem o prefixo f,
# enviando para "/finnac/auth/recoverycode/{user_id}" literalmente.
# -----------------------------------------------------------------------------
def recoverypassword(request):
    if request.method == "POST":
        user_id = request.session.get('user_id')
        
        # cada dígito vem em um campo separado
        c1 = request.POST.get('c1', '')
        c2 = request.POST.get('c2', '')
        c3 = request.POST.get('c3', '')
        c4 = request.POST.get('c4', '')
        c5 = request.POST.get('c5', '')
        c6 = request.POST.get('c6', '')
        code = c1 + c2 + c3 + c4 + c5 + c6  # junta os 6 dígitos em uma string

        if len(code) != 6:
            messages.error(request, "Código deve ter 6 dígitos.")
            return redirect(f'/finnac/auth/recoverycode/{user_id}')

        # busca o código no banco pelo usuário logado e valida o hash
        recovery_pass = RecoveryPass.objects.get(id_user=user_id)
        if recovery_pass.check_code(code):
            # código correto: renderiza a tela para definir nova senha
            return render(request, "recoveryPassword.html")
        else:
            messages.error(request, "Código incorreto.")
            return redirect(f"/finnac/auth/recoverycode/{user_id}")

    # acesso direto via GET retorna mensagem genérica (rota não é para uso direto)
    return HttpResponse("Painel privado")


# -----------------------------------------------------------------------------
# View: editPassword
# Rota: POST /finnac/auth/editPass/
#
# Recebe a nova senha e a confirmação do formulário recoveryPassword.html.
# Validações:
# - senhas devem coincidir
# - mínimo 8 caracteres
#
# update_session_auth_hash() é chamado para manter o usuário logado após
# a troca de senha (o Django Auth nativo geraria um novo hash de sessão).
# Aqui é uma chamada de compatibilidade — pode não ter efeito com auth custom.
# -----------------------------------------------------------------------------
def editPassword(request):
    if request.method == 'POST':
        user_id = request.session.get('user_id')
        
        new_password = request.POST["new-password"]
        confirm_password = request.POST["confirm-password"]
        userModel = modelApp.User.objects.get(id=user_id)

        if new_password != confirm_password:
            messages.error(request, 'As senhas não coincidem.')
        elif len(new_password) < 8:
            messages.error(request, 'A nova senha deve ter no mínimo 8 caracteres.')
        else:
            # atualiza e hasheia a nova senha antes de salvar
            userModel.set_password(new_password)
            userModel.save()
            # mantém a sessão ativa após a troca de senha
            update_session_auth_hash(request, userModel)
            messages.success(request, 'Senha atualizada com sucesso!')
        
        return redirect("/finnac/profile/")
        
    return redirect("/finnac")
