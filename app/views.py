from django.shortcuts import render, redirect
from .models import User, Flow

def home(request):
    return render(request, "index.html")

def login(request):
    return render(request, "beforeLogin/login.html")

def register(request):
    if request.method == "POST":
        full_name = request.POST.get("name")
        email = request.POST.get("email")
        password = request.POST.get("password")
        
        userModel = User(full_name = full_name, email = email, senha = password)
        userModel.save()

        return redirect("/")
    
    elif request.method == "GET":
        return render(request, "beforeLogin/register.html")

def main(request):
    return render(request, "logged/main.html")

def wallet(request):
    return render(request, "logged/wallet.html")

def generates(request):
    return render(request, "logged/toGenerate.html")