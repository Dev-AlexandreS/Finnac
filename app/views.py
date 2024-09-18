from django.shortcuts import render, redirect, HttpResponse
from django.contrib import messages
from .models import User, Flow
from datetime import datetime
import locale

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
    
        user = User(full_name=full_name, email=email)
        user.set_password(password)
        user.save()
        user = User.objects.get(email=email)
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
        id = request.session['user_id']
        flows = Flow.objects.filter(id_user = id)
        for flow in flows:
            flow.formatted_price = f"{flow.price:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
        for flow in flows:
            if flow.estatus == "P":
                flow.status = "Pago"
            if flow.estatus == "L":
                flow.status = "Atrasado"
            if flow.estatus == "O":
                flow.status = "Devendo"

        return render(request, "logged/wallet.html", {'flows':flows}) 
    else:
        return redirect("/login")

def add(request):
    if 'user_id' in request.session:
        if request.method == "POST":
            name = request.POST.get("nameAdd")
            category = request.POST.get("categoryAdd")
            price = request.POST.get("priceAdd")
            status = request.POST.get("statusAdd")
            type = request.POST.get("typeAdd")
            date = request.POST.get("dateAdd")
            id_user = request.session['user_id']

            flow = Flow(id_user=id_user,label_name=name, price=price, estatus=status, 
                        dateBill=date, tipo=type, category=category)
            flow.save()
            print(date)
            return redirect("/finnac/wallet")
    return redirect("/login")



def edit(request, id):
    if 'user_id' in request.session:
        if request.method == "POST":
            name = request.POST.get("nameModal")
            category = request.POST.get("categoryModal")
            price = request.POST.get("priceModal")
            try:
                price = price.replace('.', '').replace(',', '.')
                price = float(price)
            except ValueError:
                return redirect("/finnac/wallet")
            
            status = request.POST.get("statusModal")
            type = request.POST.get("typeModal")
            date = request.POST.get("dateModal")
            locale.setlocale(locale.LC_TIME, 'pt_BR.UTF-8')
            print(f"Data recebida: {date}")
            try:
                date_obj = datetime.strptime(date, '%d de %B de %Y')
                date = date_obj.strftime('%Y-%m-%d')
            except ValueError as e:
                print(f"Erro na conversão da data: {e}")
                return redirect("/finnac/wallet")

            if status == "Pago":
                status = "P"
            if status == "Atrasado":
                status = "L"
            if status == "Devendo":
                status = "O"
            item = Flow.objects.get(id=id)
            item.label_name = name
            item.price = price 
            item.estatus = status
            item.dateBill = date 
            item.tipo = type
            item.category = category
            item.save()
            
            return redirect("/finnac/wallet")
    
    return redirect("/login")





def delete(request, id):
    if 'user_id' in request.session:
        id_flow = id
        flow = Flow.objects.get(id=id_flow)
        flow.delete()
        return redirect("/finnac/wallet")
    return redirect("/login")

def generates(request):
    if 'user_id' in request.session:
        return render(request, "logged/toGenerate.html")
    else:
        return redirect("/login")
