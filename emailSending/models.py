# =============================================================================
# emailSending/models.py
# Define o model de recuperação de senha por código.
#
# Por que um model separado?
# O código de recuperação é temporário e vinculado a um usuário. Guardar no
# banco (hasheado) é mais seguro do que usar apenas sessão ou e-mail simples,
# pois garante que o código seja validado no servidor com hash seguro.
# =============================================================================

from django.db import models
from app import models as appModel  # importa os models do app principal
from django.contrib.auth.hashers import make_password, check_password
# make_password  → cria um hash seguro a partir do código em texto claro
# check_password → valida o código digitado pelo usuário contra o hash no banco


# -----------------------------------------------------------------------------
# Model: RecoveryPass  →  tabela "recoverypass" no banco
#
# Armazena um código de recuperação de senha hasheado por usuário.
# Regra: um usuário pode ter apenas UM código ativo por vez (unique=True no id_user).
# Antes de gerar um novo código, o anterior é deletado (feito na view `email`).
#
# Histórico das migrations:
# - 0001: FK apontava para o User nativo do Django (auth.User) — incorreto
# - 0002: FK corrigida para app.User
# - 0003: tabela renomeada para 'recoverypass'
# - 0004: adicionado unique=True no id_user
# - 0005: unique=True removido
# - 0006: unique=True re-adicionado (estado final atual)
# -----------------------------------------------------------------------------
class RecoveryPass(models.Model):
    code = models.CharField(max_length=128)
    # Armazena o HASH do código de 6 dígitos (nunca o código em texto claro).
    # max_length=128 pois os hashes do Django têm ~77-128 caracteres.

    id_user = models.ForeignKey(
        appModel.User, on_delete=models.CASCADE, unique=True
        # ForeignKey: vincula o código a um usuário
        # CASCADE: se o usuário for deletado, o código também é removido
        # unique=True: garante que cada usuário tenha no máximo um código ativo
    )

    def set_code(self, raw_password):
        """
        Recebe o código de 6 dígitos em texto claro (ex: "482931")
        e salva o hash no campo `code`. Chamado na view `email` antes de .save().
        O mesmo padrão usado em User.set_password().
        """
        self.code = make_password(raw_password)

    def check_code(self, raw_password):
        """
        Compara o código digitado pelo usuário com o hash salvo no banco.
        Retorna True se o código for válido, False caso contrário.
        Chamado na view `recoverypassword`.
        """
        return check_password(raw_password, self.code)

    class Meta:
        db_table = 'recoverypass'  # força o nome da tabela no banco
