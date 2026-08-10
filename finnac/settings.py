# =============================================================================
# finnac/settings.py
# Arquivo de configuração central do projeto Django Finnac.
#
# Gerado inicialmente com: django-admin startproject finnac
# Django versão: 5.1.1
#
# ⚠️ ATENÇÃO ANTES DE DEPLOY EM PRODUÇÃO:
# - SECRET_KEY deve ser movida para variável de ambiente
# - DEBUG deve ser False
# - EMAIL_HOST_PASSWORD deve sair do código (usar .env)
# - ALLOWED_HOSTS deve ser restrito ao domínio real
# =============================================================================

from pathlib import Path
import os
from decouple import config
# config() lê variáveis do arquivo .env (ou das variáveis de ambiente do sistema).
# Sintaxe: config('NOME_DA_VARIAVEL', default=valor_padrao, cast=tipo)
# - default: valor usado se a variável não existir no .env
# - cast=bool: converte a string "True"/"False" do .env para booleano Python

# BASE_DIR aponta para a raiz do projeto (pasta Finnac/).
# Usado para construir caminhos absolutos: BASE_DIR / 'static', BASE_DIR / 'db.sqlite3' etc.
BASE_DIR = Path(__file__).resolve().parent.parent


# SECRET_KEY agora vem do .env — nunca mais exposta no código
SECRET_KEY = config('SECRET_KEY')

# DEBUG vem do .env como string "True" ou "False"; cast=bool converte para booleano
DEBUG = config('DEBUG', default=False, cast=bool)

# ALLOWED_HOSTS controla quais domínios podem acessar o projeto.
# "*" aceita qualquer host — restringir em produção para o domínio real
ALLOWED_HOSTS = ["*"]


# =============================================================================
# APPS INSTALADOS
# Django carrega cada app listado aqui. Os 6 primeiros são built-in do Django.
# Os 3 últimos são apps criados para o Finnac.
# =============================================================================
INSTALLED_APPS = [
    'django.contrib.admin',         # painel de administração automático
    'django.contrib.auth',          # sistema de autenticação nativo (não usado pelo Finnac diretamente)
    'django.contrib.contenttypes',  # framework de tipos de conteúdo (necessário para o admin)
    'django.contrib.sessions',      # suporte a sessões (usado para guardar user_id no login)
    'django.contrib.messages',      # sistema de flash messages (ex: "Senha atualizada!")
    'django.contrib.staticfiles',   # gerenciamento de arquivos estáticos (CSS, JS, imagens)
    'app',           # app principal: usuários, lançamentos financeiros, contas
    'emailSending',  # app de recuperação de senha via e-mail
    'generate',      # app de geração de relatórios Excel e PDF
]

# =============================================================================
# MIDDLEWARES
# Processados em ordem para cada requisição HTTP.
# SecurityMiddleware  → headers de segurança (HTTPS, XSS...)
# SessionMiddleware   → habilita o uso de request.session
# CommonMiddleware    → normalização de URLs (ex: adiciona / no fim)
# CsrfViewMiddleware  → proteção contra CSRF (token nos formulários POST)
# AuthenticationMiddleware → popula request.user (com o User nativo do Django)
# MessageMiddleware   → habilita o sistema de flash messages
# XFrameOptionsMiddleware → proteção contra clickjacking
# =============================================================================
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# Arquivo raiz de URLs do projeto
ROOT_URLCONF = 'finnac.urls'

# =============================================================================
# TEMPLATES
# APP_DIRS=True: Django procura templates dentro de cada app em /templates/
# context_processors: injetam variáveis automáticas em todos os templates
#   - debug: True/False do DEBUG
#   - request: o objeto request atual
#   - auth: request.user e request.perms
#   - messages: as flash messages pendentes
# =============================================================================
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],       # sem diretórios globais de templates; usa apenas os das apps
        'APP_DIRS': True,  # busca em app/templates/, emailSending/templates/ etc.
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# Ponto de entrada WSGI (usado pelo servidor web em produção: gunicorn, etc.)
WSGI_APPLICATION = 'finnac.wsgi.application'


# =============================================================================
# BANCO DE DADOS
# SQLite é usado por padrão — arquivo db.sqlite3 na raiz do projeto.
# Para produção, trocar para PostgreSQL ou MySQL.
# =============================================================================
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',  # caminho absoluto para o arquivo SQLite
    }
}


# =============================================================================
# VALIDADORES DE SENHA (do Django Auth nativo)
# Usados quando se chama user.set_password() via Django Auth.
# O Finnac usa seu próprio User customizado, mas mantém isso por compatibilidade.
# =============================================================================
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]


# =============================================================================
# INTERNACIONALIZAÇÃO
# pt-BR: textos do Django (mensagens de erro do admin etc.) em português
# America/Sao_Paulo: fuso horário para campos com timezone awareness
# USE_I18N=True: habilita o sistema de tradução do Django
# USE_TZ=True: campos DateTimeField armazenam com timezone (UTC internamente)
# =============================================================================
LANGUAGE_CODE = 'pt-BR'
TIME_ZONE = 'America/Sao_Paulo'
USE_I18N = True
USE_TZ = True


# =============================================================================
# ARQUIVOS ESTÁTICOS (CSS, JS, Imagens)
# STATIC_URL: URL base para acessar estáticos (ex: /static/img/logo.svg)
# STATICFILES_DIRS: pastas onde o Django procura estáticos durante desenvolvimento
# STATIC_ROOT: pasta para onde `collectstatic` copia tudo (usado em produção)
# =============================================================================
STATIC_URL = 'static/'
STATICFILES_DIRS = [
    BASE_DIR / "static",  # pasta /static/ na raiz do projeto
]
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")  # usado pelo collectstatic em produção


# Tipo de chave primária padrão para todos os models sem PK explícita
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Diz ao Django que o model de usuário do projeto é app.User (não o auth.User padrão).
# Com isso, @login_required, request.user e o Django Admin usam o nosso User customizado.
AUTH_USER_MODEL = 'app.User'


# =============================================================================
# CONFIGURAÇÃO DE E-MAIL (SMTP)
# Usado pelo app emailSending para enviar o código de recuperação de senha.
#
# Provedor: Hostinger (smtp.hostinger.com), porta 465 com SSL.
# EMAIL_USE_SSL=True / EMAIL_USE_TLS=False → conexão segura direto na porta 465.
#
# ⚠️ EMAIL_HOST_PASSWORD está hardcoded — mover para variável de ambiente!
# Ex: EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD')
# =============================================================================
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.hostinger.com'
EMAIL_PORT = 465
EMAIL_USE_SSL = True   # SSL direto (porta 465)
EMAIL_USE_TLS = False  # TLS é para porta 587; não usar junto com SSL
EMAIL_HOST_USER = config('EMAIL_HOST_USER')           # lido do .env
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD')   # lido do .env — nunca mais hardcoded
DEFAULT_FROM_EMAIL = config('EMAIL_HOST_USER')        # usa o mesmo valor do host user
