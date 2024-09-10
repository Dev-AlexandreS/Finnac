from django.shortcuts import render, redirect
from django.contrib import messages
from .models import User

def home(request):
    return render(request, 'index.html')

def login(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("senha")

        try:
            user = User.objects.get(email=email)
            if user.check_password(password):
                request.session['user_id'] = user.id
                return redirect("/finnac")
            else:
                messages.error(request, "Email ou senha incorretos.")
        except User.DoesNotExist:
            messages.error(request, "Email ou senha incorretos.")
        
        return redirect("/login")
    elif request.method == "GET":
        return render(request, "beforeLogin/login.html")

def register(request):
    if request.method == "POST":
        full_name = request.POST.get("name")
        email = request.POST.get("email")
        password = request.POST.get("password")
        
        # Cria um novo usuário
        user = User(full_name=full_name, email=email)
        user.set_password(password)
        user.save()

        # Autentica o usuário e cria uma sessão
        # Note que o Django recomenda usar o modelo User padrão e suas funcionalidades de autenticação
        user = User.objects.get(email=email)  # Aqui você deve buscar pelo email, já que a senha foi criptografada
        request.session['user_id'] = user.id

        return redirect("/finnac")
    
    elif request.method == "GET":
        return render(request, "beforeLogin/register.html")

def main(request):
    if 'user_id' in request.session:
        return render(request, "logged/main.html")
    else:
        return redirect("/login")

def logout(request):
    if 'user_id' in request.session:
        del request.session['user_id']
    return redirect("/")

def wallet(request):
    if 'user_id' in request.session:
        return render(request, "logged/wallet.html")
    else:
        return redirect("/login")

def generates(request):
    if 'user_id' in request.session:
        return render(request, "logged/toGenerate.html")
    else:
        return redirect("/login")
