from django.db import models
from django.contrib.auth.hashers import make_password, check_password

class User(models.Model):
    full_name = models.CharField(max_length=30)
    email = models.EmailField(max_length=50, unique=True)
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
    id_user = models.CharField(max_length=50)
    label_name = models.CharField(max_length=50)
    price = models.FloatField()
    estatus = models.CharField(max_length=1)
    dateBill = models.DateField()
    tipo = models.CharField(max_length=20)
    category = models.CharField(max_length=20)
    class Meta:
        db_table = 'flow'
    def __str__(self):
        return self.label_name
