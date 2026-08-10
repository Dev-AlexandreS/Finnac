# Como o Projeto Finnac Foi Feito — Passo a Passo

## O que é o Finnac?

Finnac é um gestor de finanças pessoais web desenvolvido em Django. Permite que o usuário
cadastre lançamentos financeiros (ganhos e despesas), gerencie contas bancárias, visualize
um dashboard com resumo financeiro e exporte relatórios em Excel e PDF.

---

## Stack Usada

| Camada     | Tecnologia                                      |
|------------|-------------------------------------------------|
| Back-end   | Python + Django 5.1.1                           |
| Banco      | SQLite (arquivo db.sqlite3)                     |
| Front-end  | Tailwind CSS (CDN) + Flowbite + Alpine.js       |
| Tabelas    | Bootstrap 5.3.3                                 |
| Gráficos   | Chart.js                                        |
| Excel      | openpyxl                                        |
| PDF        | PyMuPDF (fitz)                                  |
| E-mail     | Django Email + SMTP Hostinger                   |

---

## Passo 1 — Criar o Projeto Django

```bash
django-admin startproject finnac
cd finnac
python manage.py startapp app
```

O comando `startproject` criou a pasta `finnac/` com `settings.py`, `urls.py`, `wsgi.py` e `asgi.py`.
O `startapp app` criou o app principal com `models.py`, `views.py`, `urls.py` etc.

---

## Passo 2 — Configurar o settings.py

Em `finnac/settings.py` foram feitas as seguintes configurações:

- `INSTALLED_APPS`: adicionado `'app'` à lista
- `LANGUAGE_CODE = 'pt-BR'` e `TIME_ZONE = 'America/Sao_Paulo'` para o contexto brasileiro
- `DATABASES`: mantido o SQLite padrão
- `STATICFILES_DIRS`: apontado para a pasta `/static/` na raiz
- Configurações de e-mail SMTP da Hostinger adicionadas ao final

---

## Passo 3 — Criar os Models (banco de dados)

Em `app/models.py` foram criados os 3 models principais:

### User
Representa o usuário do sistema. Em vez de usar o `AbstractUser` do Django, foi criado
um model próprio por simplicidade. A senha é armazenada como hash usando `make_password`
do próprio Django.

### Flow
Representa cada lançamento financeiro. Campos: nome, valor, categoria, tipo (Ganho/Despesa),
estatus (Único/Recorrente/Parcelado) e data.

### Accounts
Representa as contas bancárias do usuário. Campos: nome do banco e saldo.

Após criar os models, rodar as migrations:

```bash
python manage.py makemigrations
python manage.py migrate
```

---

## Passo 4 — Criar as URLs e Views do app principal

Em `app/urls.py` foram definidas todas as rotas. Em `app/views.py` foram escritas
as funções para cada rota.

**Controle de acesso manual:** como o User personalizado não integra com o sistema de
autenticação nativo do Django, toda view que requer login faz a verificação:
```python
if 'user_id' in request.session:
    # lógica da view
return redirect("/login")
```

O `user_id` é salvo na sessão no momento do login e removido no logout.

---

## Passo 5 — Criar os Templates HTML

Estrutura de templates criada dentro de `app/templates/`:

```
app/templates/
├── index.html              ← Landing page pública
├── beforeLogin/
│   ├── login.html
│   └── register.html
├── layout/
│   └── base.html           ← Layout base com sidebar Alpine.js
└── logged/
    ├── main.html           ← Dashboard
    ├── wallet.html         ← Carteira
    ├── profile.html        ← Perfil
    ├── recoverycode.html   ← Código de 6 dígitos
    └── toGenerate.html     ← Botões de relatório
```

O `base.html` usa Alpine.js para controlar a sidebar (abrir/fechar em mobile).
Os templates logados herdam do base com `{% extends '../layout/base.html' %}`.

---

## Passo 6 — Criar o app emailSending

```bash
python manage.py startapp emailSending
```

Adicionado em `INSTALLED_APPS`. Criado o model `RecoveryPass` para guardar o hash
do código de 6 dígitos.

Views criadas:
- `email`: gera e envia o código
- `recoverypassword`: valida o código digitado
- `editPassword`: atualiza a senha

Templates de e-mail criados em `emailSending/templates/`:
- `email_template.html`: corpo HTML do e-mail enviado
- `recoveryPassword.html`: formulário para digitar a nova senha

---

## Passo 7 — Criar o app generate

```bash
python manage.py startapp generate
```

Adicionado em `INSTALLED_APPS`. Sem models — apenas views que processam dados.

Arquivos template colocados em `generate/files/`:
- `Planilha-Finnac.xlsx`: planilha template com layout pronto; os dados são inseridos via openpyxl
- `Relatório - Finnac.pdf`: PDF template com layout pronto; os dados são inseridos via PyMuPDF

Views criadas:
- `excel`: preenche o template Excel e retorna como download
- `pdf`: insere textos em posições fixas no PDF e retorna como download

---

## Passo 8 — Conectar tudo no URL raiz

Em `finnac/urls.py` as três apps foram conectadas com `include()`:

```python
path('', include('app.urls'))
path('email/', include('emailSending.urls'))
path('generate/', include('generate.urls'))
```

---

## Passo 9 — Evolução do schema (histórico das migrations)

As migrations documentam como o banco foi evoluindo durante o desenvolvimento:

| Data       | O que mudou                                             |
|------------|----------------------------------------------------------|
| 06/09/2024 | Criação inicial: tabelas User e Flow                    |
| 10/09/2024 | Nomes de tabelas explícitos; troca de `senha` para `password` hasheado |
| 18/09/2024 | FK renomeada para `id_user`; `estatus` sem choices fixas |
| 18/09/2024 | `unique=True` removido do e-mail                        |
| 08/10/2024 | Criação da tabela `accounts` com DecimalField           |
| 08/10/2024 | `Flow.price` migrado de Float para Decimal              |
| 11/10/2024 | App emailSending: criação do model RecoveryPass         |
| 11/10/2024 | FK corrigida de auth.User para app.User; unique=True adicionado |

---

## Fluxo de dados — Login

```
GET /login/ → exibe login.html
POST /login/ → User.objects.get(email=email)
             → user.check_password(senha) → True
             → request.session['user_id'] = user.id
             → redirect /finnac/
```

## Fluxo de dados — Dashboard

```
GET /finnac/ → verifica session['user_id']
            → soma Flow(tipo='Ganho') + Accounts.coast
            → soma Flow(tipo='Despesa')
            → calcula balanço
            → formata em BR: "1.234,56"
            → render main.html com context
```

## Fluxo de dados — Recuperação de Senha

```
perfil → clica "Trocar Senha"
       → GET /email/
       → gera random(100000, 999999)
       → RecoveryPass.set_code() → hash → salva no banco
       → envia e-mail HTML com o código em texto claro
       → redirect /finnac/auth/recoverycode/<id>/

usuário digita o código (6 campos separados)
       → POST /email/finnac/auth/recoverypassword/
       → junta c1+c2+c3+c4+c5+c6
       → RecoveryPass.check_code() → compara com hash
       → render recoveryPassword.html

usuário digita nova senha
       → POST /email/finnac/auth/editPass/
       → user.set_password(nova_senha) → hash → save()
       → redirect /finnac/profile/
```

## Fluxo de dados — Gerar Excel

```
GET /generate/excel/
  → abre Planilha-Finnac.xlsx com openpyxl
  → preenche C4=nome, C5=email
  → loop nos Flow: preenche B7:F7, B8:F8...
  → salva em BytesIO
  → HttpResponse com content-type xlsx → download
```

## Fluxo de dados — Gerar PDF

```
GET /generate/pdf/
  → calcula soma de Ganhos, Despesas, Balanço
  → abre Relatório - Finnac.pdf com fitz (PyMuPDF)
  → page.insert_text() em coordenadas fixas
  → salva em BytesIO
  → HttpResponse com content-type pdf → download
```

---

## Pontos que podem ser melhorados

1. **Credenciais expostas** — `SECRET_KEY` e `EMAIL_HOST_PASSWORD` estão no código.
   Usar `python-decouple` ou `django-environ` com arquivo `.env`.

2. **Controle de acesso** — O `if 'user_id' in request.session` se repete em toda view.
   Criar um decorator `@login_required_custom` ou middleware elimina a duplicação.

3. **Usuário customizado** — Usar `AbstractBaseUser` permitiria integrar com `@login_required`,
   `request.user` e o Django Admin nativo.

4. **Bug no redirect de erro** — Em `recoverypassword`, falta o `f` na f-string do redirect.

5. **Posições hardcoded no PDF** — Qualquer mudança no template PDF quebra o texto inserido.
   Uma abordagem mais robusta seria gerar o PDF do zero com reportlab.

6. **ALLOWED_HOSTS = ["*"]** — Deve ser restrito ao domínio real antes do deploy.
