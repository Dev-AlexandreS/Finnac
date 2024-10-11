from django.db import models
from app import models as appModel
from django.contrib.auth.hashers import make_password, check_password

class RecoveryPass(models.Model):
    code = models.CharField(max_length=128)
    id_user = models.ForeignKey(appModel.User, on_delete=models.CASCADE, unique=True)

    def set_code(self, raw_password):
        self.code = make_password(raw_password)

    def check_code(self, raw_password):
        return check_password(raw_password, self.code)
    class Meta:
        db_table = 'recoverypass'

    

