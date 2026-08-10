# =============================================================================
# app/views.py
# Contém toda a lógica principal do sistema Finnac:
# autenticação, dashboard, carteira de lançamentos e contas bancárias.
#
# Cada função aqui é uma "view" — ela recebe uma requisição HTTP (request),
# processa os dados e retorna uma resposta (HTML renderizado ou redirect).
# =============================================================================

from django.shortcuts import render, redirect, HttpResponse
from django.contrib import messages       # sistema de flash messages do Django
from .models import User, Flow, Accounts  # modelos deste app
from .decorators import login_required_custom  # protege rotas que requerem login
from django.db.models import Sum, Q       # Sum: somar campos; Q: queries complexas
from datetime import datetime             # manipulação de datas
from decimal import Decimal               # aritmética decimal precisa para valores monetários

import locale  # usado para formatar datas em português na view `edit`


# -----------------------------------------------------------------------------
# View: home
# Rota: GET /
# Renderiza a landing page pública do Finnac (index.html).
# -----------------------------------------------------------------------------
def home(request):
    return render(request, 'index.html')


# -----------------------------------------------------------------------------
# View: login
# Rota: GET /login/  →  exibe o formulário
#       POST /login/ →  processa o login
#
# Fluxo:
# 1. Busca o usuário pelo e-mail
# 2. check_password() compara a senha digitada com o hash no banco
# 3. Se correto: salva user_id na sessão e redireciona ao dashboard
# 4. Se errado: mensagem de erro e volta ao login
# -----------------------------------------------------------------------------
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
            # mesma mensagem para não revelar qual campo está errado
            messages.error(request, "Email ou senha incorretos.")

        return redirect("/login")

    elif request.method == "GET":
        return render(request, "beforeLogin/login.html")


# -----------------------------------------------------------------------------
# View: register
# Rota: GET /cadastro/  →  exibe o formulário
#       POST /cadastro/ →  processa o cadastro
# -----------------------------------------------------------------------------
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


# -----------------------------------------------------------------------------
# View: main  (Dashboard)
# Rota: GET /finnac/
#
# @login_required_custom verifica se 'user_id' existe na sessão.
# Se não existir, redireciona para /login/ antes mesmo de entrar na função.
# Isso elimina o `if 'user_id' in request.session` que existia antes.
#
# Cálculos:
# - Receitas = soma Flow(tipo='Ganho') + soma Accounts.coast
# - Despesas = soma Flow(tipo='Despesa')
# - Balanço  = Receitas - Despesas
# -----------------------------------------------------------------------------
@login_required_custom
def main(request):
    id = request.session['user_id']  # seguro: o decorator garante que existe

    # Soma de todos os ganhos do usuário
    total_ganho = Flow.objects.filter(id_user=id, tipo='Ganho').aggregate(Sum('price'))
    ganhos = total_ganho['price__sum'] or Decimal('0.00')

    # Soma de todos os saldos de contas bancárias
    total_contas = Accounts.objects.filter(id_user=id).aggregate(Sum('coast'))
    total_contas = total_contas['coast__sum'] or Decimal('0.00')

    # Receita total = ganhos registrados + saldo em contas
    ganhos += total_contas
    ganhos_formatado = f"{ganhos:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')

    # Soma de todas as despesas
    total_despesas = Flow.objects.filter(id_user=id, tipo='Despesa').aggregate(Sum('price'))
    despesas = total_despesas['price__sum'] or Decimal('0.00')
    despesas_formatado = f"{despesas:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')

    # Balanço
    faturamento = ganhos - despesas
    faturamento_formatado = f"{faturamento:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')

    accounts = Accounts.objects.filter(id_user=id)

    return render(request, "logged/main.html", {
        'ganhos': ganhos_formatado,
        'despesas': despesas_formatado,
        'faturamento': faturamento_formatado,
        'id': id,
        'contas': accounts,
        'total_contas': f"{total_contas:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
    })


# -----------------------------------------------------------------------------
# View: addAccount
# Rota: POST /finnac/accounts/add/
# @login_required_custom: só usuários logados podem adicionar contas.
# -----------------------------------------------------------------------------
@login_required_custom
def addAccount(request):
    if request.method == 'POST':
        bank = request.POST['bank']
        price = request.POST['accountValue']
        id_user = request.session['user_id']
        try:
            user = User.objects.get(id=id_user)
            accounts = Accounts(id_user=user, bank_name=bank, coast=price)
            accounts.save()
            return redirect("/finnac")
        except User.DoesNotExist:
            return redirect("/finnac")
        except Exception as e:
            print(f"Ocorreu um erro: {e}")
            return redirect("/finnac")
    return redirect("/finnac")


# -----------------------------------------------------------------------------
# View: deleteAccount
# Rota: GET /finnac/accounts/delete/<id>/
# @login_required_custom: protege a rota.
# -----------------------------------------------------------------------------
@login_required_custom
def deleteAccount(request, id):
    account = Accounts.objects.get(id=id)
    account.delete()
    return redirect("/finnac")


# -----------------------------------------------------------------------------
# View: editAccount
# Rota: POST /finnac/accounts/edit/
# @login_required_custom: protege a rota.
# Converte vírgula para ponto antes de salvar (formato BR → float).
# -----------------------------------------------------------------------------
@login_required_custom
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


# -----------------------------------------------------------------------------
# View: logout
# Rota: GET /finnac/logout/
# Remove user_id da sessão e redireciona para a landing page.
# -----------------------------------------------------------------------------
def logout(request):
    if 'user_id' in request.session:
        del request.session['user_id']
    return redirect("/")


# -----------------------------------------------------------------------------
# View: wallet  (Carteira)
# Rota: GET /finnac/wallet/
# @login_required_custom: protege a rota.
#
# Adiciona atributos extras em cada Flow antes de enviar ao template:
#   formatted_price: valor formatado em BR ("1.234,56")
#   status: tradução do código → texto legível
# -----------------------------------------------------------------------------
@login_required_custom
def wallet(request):
    id = request.session['user_id']
    flows = Flow.objects.filter(id_user=id)

    for flow in flows:
        flow.formatted_price = f"{flow.price:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')

    for flow in flows:
        if flow.estatus == "S":
            flow.status = "Único"
        if flow.estatus == "A":
            flow.status = "Recorrente"
        if flow.estatus == "I":
            flow.status = "Parcelado"

    return render(request, "logged/wallet.html", {'flows': flows})


# -----------------------------------------------------------------------------
# View: add
# Rota: POST /finnac/wallet/add/
# @login_required_custom: protege a rota.
# Cria novo lançamento Flow com os dados do formulário.
# -----------------------------------------------------------------------------
@login_required_custom
def add(request):
    if request.method == "POST":
        name = request.POST.get("nameAdd")
        category = request.POST.get("categoryAdd")
        price = request.POST.get("priceAdd")
        status = request.POST.get("statusAdd")
        type = request.POST.get("typeAdd")
        date = request.POST.get("dateAdd")
        id_user = request.session['user_id']
        user = User.objects.get(id=id_user)
        flow = Flow(id_user=user, label_name=name, price=price, estatus=status,
                    dateBill=date, tipo=type, category=category)
        flow.save()
        return redirect("/finnac/wallet")
    return redirect("/finnac/wallet")


# -----------------------------------------------------------------------------
# View: edit
# Rota: POST /edit/<id>
# @login_required_custom: protege a rota.
#
# Processos especiais:
# 1. Preço: "1.234,56" → remove pontos → substitui vírgula → float
# 2. Data: "15 de outubro de 2024" via locale pt_BR → converte para "YYYY-MM-DD"
# 3. Status: texto do modal → código de 1 letra para o banco
# -----------------------------------------------------------------------------
@login_required_custom
def edit(request, id):
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

    return redirect("/finnac/wallet")


# -----------------------------------------------------------------------------
# View: delete
# Rota: GET /delete/<id>
# @login_required_custom: protege a rota.
# -----------------------------------------------------------------------------
@login_required_custom
def delete(request, id):
    flow = Flow.objects.get(id=id)
    flow.delete()
    return redirect("/finnac/wallet")


# -----------------------------------------------------------------------------
# View: generates
# Rota: GET /finnac/generates/
# @login_required_custom: protege a rota.
# Renderiza a página de escolha de formato de relatório.
# -----------------------------------------------------------------------------
@login_required_custom
def generates(request):
    return render(request, "logged/toGenerate.html")


# -----------------------------------------------------------------------------
# View: profile
# Rota: GET /finnac/profile/  →  exibe dados do perfil
#       POST /finnac/profile/ →  atualiza nome, e-mail e opcionalmente senha
# @login_required_custom: protege a rota.
# -----------------------------------------------------------------------------
@login_required_custom
def profile(request):
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

    return redirect("/finnac")


# -----------------------------------------------------------------------------
# View: recoverycode
# Rota: GET /finnac/auth/recoverycode/<id>/
#
# Exibe o formulário de 6 dígitos para validar o código de recuperação.
# Verifica que o user_id da sessão bate com o <id> da URL para impedir
# que um usuário acesse a tela de recuperação de outro.
# -----------------------------------------------------------------------------
def recoverycode(request, id):
    if 'user_id' in request.session and request.session['user_id'] == id:
        if request.method == 'GET':
            return render(request, "logged/recoverycode.html")
    return redirect("/")
