# =============================================================================
# app/models.py
# Define as tabelas principais do banco de dados do Finnac.
#
# MUDANÇA PRINCIPAL: User agora herda de AbstractBaseUser + PermissionsMixin
# em vez de models.Model puro. Isso integra o usuário ao sistema de auth
# nativo do Django, permitindo usar:
#   - @login_required nas views
#   - request.user para acessar o usuário logado
#   - django.contrib.auth.login() / logout() nativos
#   - Django Admin para gerenciar usuários
#
# Requer AUTH_USER_MODEL = 'app.User' no settings.py.
# =============================================================================

from django.db import models
from django.db.models import Sum  # usado nas views para agregação
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
# AbstractBaseUser → classe base para usuários customizados; fornece set_password,
#                    check_password, last_login, is_active e o hash de senha
# BaseUserManager  → classe base para o Manager do User customizado; fornece
#                    create_user() e create_superuser() que o Django Admin usa
# PermissionsMixin → adiciona is_superuser, groups e user_permissions;
#                    necessário para o sistema de permissões do Django Admin


# -----------------------------------------------------------------------------
# UserManager
# O Django exige um Manager customizado quando se usa AbstractBaseUser.
# O Manager é o objeto que sabe "como criar" instâncias do User.
# Acessado via User.objects.create_user(...) e User.objects.create_superuser(...)
# -----------------------------------------------------------------------------
class UserManager(BaseUserManager):

    def create_user(self, email, full_name, password=None):
        """
        Cria um usuário comum.
        normalize_email() padroniza o e-mail (deixa o domínio em minúsculo).
        set_password() hasheia a senha — vem do AbstractBaseUser.
        """
        if not email:
            raise ValueError('O e-mail é obrigatório')
        user = self.model(
            email=self.normalize_email(email),
            full_name=full_name
        )
        user.set_password(password)  # hasheia e salva no campo `password`
        user.save(using=self._db)    # `using=self._db` respeita banco de dados múltiplos
        return user

    def create_superuser(self, email, full_name, password):
        """
        Cria um superusuário (acesso total ao Django Admin).
        Chama create_user() e depois ativa is_staff e is_superuser.
        """
        user = self.create_user(email, full_name, password)
        user.is_staff = True       # permite acessar o painel /admin/
        user.is_superuser = True   # acesso total a todas as permissões
        user.save(using=self._db)
        return user


# -----------------------------------------------------------------------------
# Model: User  →  tabela "users" no banco
#
# AbstractBaseUser fornece:
#   - password (CharField com hash) — não precisa declarar
#   - last_login (DateTimeField) — atualizado automaticamente pelo Django Auth
#   - set_password(raw) — hasheia e salva a senha
#   - check_password(raw) — compara senha com o hash
#   - is_active (BooleanField) — usuário ativo ou bloqueado
#
# PermissionsMixin fornece:
#   - is_superuser (BooleanField)
#   - groups (M2M para Group)
#   - user_permissions (M2M para Permission)
# -----------------------------------------------------------------------------
class User(AbstractBaseUser, PermissionsMixin):
    full_name = models.CharField(max_length=30)
    email = models.EmailField(max_length=50, unique=True)
    # unique=True voltou: o e-mail é o campo de login (USERNAME_FIELD),
    # então precisa ser único no banco

    is_active = models.BooleanField(default=True)
    # Controla se a conta está ativa. False = usuário bloqueado/desativado.
    # O Django Auth usa isso para impedir logins sem precisar deletar o registro.

    is_staff = models.BooleanField(default=False)
    # True = pode acessar o painel /admin/ do Django.
    # Necessário junto com PermissionsMixin.

    objects = UserManager()
    # Conecta o Manager customizado ao model.
    # Isso faz User.objects.create_user() funcionar.

    USERNAME_FIELD = 'email'
    # Define qual campo é usado no login. O padrão do Django é 'username',
    # mas aqui usamos 'email'.

    REQUIRED_FIELDS = ['full_name']
    # Campos obrigatórios além de USERNAME_FIELD e password.
    # Usados pelo comando `python manage.py createsuperuser`.

    class Meta:
        db_table = 'users'

    def __str__(self):
        return self.full_name

    # NOTA: set_password() e check_password() NÃO precisam mais ser reimplementados.
    # AbstractBaseUser já os fornece com a mesma funcionalidade.


# -----------------------------------------------------------------------------
# Model: Flow  →  tabela "flow" no banco
# Sem mudanças estruturais — apenas a FK aponta para o mesmo User,
# que agora é AbstractBaseUser.
# -----------------------------------------------------------------------------
class Flow(models.Model):
    id_user = models.ForeignKey(
        User, on_delete=models.CASCADE
        # CASCADE: se o usuário for deletado, todos os lançamentos também são
    )
    label_name = models.CharField(max_length=50)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    estatus = models.CharField(max_length=1)
    # 'S' = Único / 'A' = Recorrente / 'I' = Parcelado
    dateBill = models.DateField()
    tipo = models.CharField(max_length=20)
    # 'Ganho' / 'Despesa' / 'Transferências'
    category = models.CharField(max_length=20)

    class Meta:
        db_table = 'flow'

    def __str__(self):
        return self.label_name


# -----------------------------------------------------------------------------
# Model: Accounts  →  tabela "accounts" no banco
# Sem mudanças — representa contas bancárias do usuário.
# -----------------------------------------------------------------------------
class Accounts(models.Model):
    id_user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    bank_name = models.CharField(max_length=50)
    coast = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        db_table = 'accounts'

    def __str__(self):
        return self.bank_name
