from django.shortcuts import render

def home(request):
    return render(request, "index.html")

def login(request):
    return render(request, "beforeLogin/login.html")

def register(request):
    return render(request, "beforeLogin/register.html")

def main(request):
    return render(request, "logged/main.html")
