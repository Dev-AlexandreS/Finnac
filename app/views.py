from django.shortcuts import render, redirect, HttpResponse
from django.contrib import messages
from .models import User, Flow, Accounts
from django.db.models import Sum, Q
from datetime import datetime
from decimal import Decimal

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
    if request.method == 'POST':
        name = request.POST['name']
        email = request.POST['email']
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']
        
        if password != confirm_password:
            messages.error(request, 'As senhas não coincidem.')
        elif len(password) < 8:
            messages.error(request, 'A senha deve ter no mínimo 6 caracteres.')
        elif User.objects.filter(email=email).exists():
            messages.error(request, 'Um usuário com este e-mail já existe.')
        else:
            user = User(full_name=name, email=email)
            user.set_password(password)
            user.save()
            
            request.session['user_id'] = user.id
            return redirect("/finnac")  
    return render(request, 'beforeLogin/register.html')




def main(request):
    if 'user_id' in request.session:
        id = request.session['user_id']
        
        total_ganho = Flow.objects.filter(id_user=id, tipo='Ganho').aggregate(Sum('price')) 
        ganhos = total_ganho['price__sum'] or Decimal('0.00')  
    
        total_contas = Accounts.objects.filter(id_user=id).aggregate(Sum('coast'))
        total_contas = total_contas['coast__sum'] or Decimal('0.00')  
        
       
        ganhos += total_contas  
        ganhos_formatado = f"{ganhos:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')

      
        total_despesas = Flow.objects.filter(id_user=id, tipo='Despesa').aggregate(Sum('price')) 
        despesas = total_despesas['price__sum'] or Decimal('0.00')  
        despesas_formatado = f"{despesas:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')

      
        faturamento = ganhos - despesas  
        faturamento_formatado = f"{faturamento:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')

        accounts = Accounts.objects.filter(id_user=id)  

        return render(request, "logged/main.html", {
            'ganhos': ganhos_formatado,  
            'despesas': despesas_formatado,
            'faturamento': faturamento_formatado,
            'id': id,
            'contas': accounts,
            'total_contas': f"{total_contas:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')  # Formatação opcional
        })
    return redirect("/login")



def addAccount(request):
    if request.method == 'POST':
        bank = request.POST['bank']
        price = request.POST['accountValue']
        if 'user_id' in request.session:
            id_user = request.session['user_id']
            try:
                user = User.objects.get(id=id_user)
                accounts = Accounts(id_user=user, bank_name=bank, coast=price)
                accounts.save()
                print("Conta adicionada com sucesso.")
                return redirect("/finnac")
            except User.DoesNotExist:
                print("Usuário não encontrado.")
                return redirect("/finnac")
            except Exception as e:
                print(f"Ocorreu um erro: {e}")
                return redirect("/finnac")
    else:
        print("erro ao add conta ")
        
        return redirect("/finnac")

def deleteAccount(request, id):
    if request.method == 'GET':
        if 'user_id' in request.session:
            if 'user_id' in request.session:
                id_account = id
                account = Accounts.objects.get(id=id_account)
                account.delete()
                print("deletado")
                return redirect("/finnac")
        return redirect("/login")
        

def editAccount(request):
    if request.method == 'POST':
        bank = request.POST["editBank"]
        coast = request.POST["editAccountValue"]
        idAccount = request.POST["idAccount"]
        coast = coast.replace(',', '.') 
        coast = float(coast)
        account = Accounts.objects.get(id=idAccount)
        
        account.bank_name = bank
        account.coast = coast
    
        account.save()
        
        return redirect("/finnac")

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
            if flow.estatus == "S":
                flow.status = "Único"
            if flow.estatus == "A":
                flow.status = "Recorrente"
            if flow.estatus == "I":
                flow.status = "Parcelado"

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
            user = User.objects.get(id=id_user)
            flow = Flow(id_user=user,label_name=name, price=price, estatus=status, 
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
    
def profile(request):
    if 'user_id' in request.session:
        user = User.objects.get(id=request.session['user_id'])

        if request.method == "GET":
            return render(request, "logged/profile.html", {'user': user})

        if request.method == "POST":
            full_name = request.POST.get("full_name")
            email = request.POST.get("email")
            password = request.POST.get("password")

            user.full_name = full_name
            user.email = email
            if password:
                user.set_password(password)

            user.save()

            messages.success(request, 'Perfil atualizado com sucesso.')
            return redirect("/finnac")

    return redirect("/login")
