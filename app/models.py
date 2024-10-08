from django.db import models
from django.db.models import Sum
from django.contrib.auth.hashers import make_password, check_password

class User(models.Model):
    full_name = models.CharField(max_length=30)
    email = models.EmailField(max_length=50)
    password = models.CharField(max_length=128)

    class Meta:
        db_table = 'users'

    def __str__(self):
        return self.full_name

    def set_password(self, raw_password):
        self.password = make_password(raw_password)

    def check_password(self, raw_password):
        return check_password(raw_password, self.password)


    
class Flow(models.Model):   
    id_user = models.ForeignKey(User, on_delete=models.CASCADE)
    label_name = models.CharField(max_length=50)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    estatus = models.CharField(max_length=1)
    dateBill = models.DateField()
    tipo = models.CharField(max_length=20)
    category = models.CharField(max_length=20)
    class Meta:
        db_table = 'flow'
    def __str__(self):
        return self.label_name
    
class Accounts(models.Model):
    id_user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    bank_name = models.CharField(max_length=50)
    coast = models.DecimalField(max_digits=10, decimal_places=2)  # Mudado para DecimalField

    class Meta:
        db_table = 'accounts'  # Adicionado db_table ausente

    def __str__(self):
        return self.bank_name