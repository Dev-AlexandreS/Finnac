from django.db import models

class User(models.Model):
    full_name = models.CharField(max_length=30)
    email = models.EmailField(max_length=50, unique=True)
    senha = models.CharField(max_length=12)

    class Meta:
        db_table = 'users'
    def __str__(self):
        return self.full_name

class Flow(models.Model):
    STATUS_CHOICES = [
        ('A', 'Active'),
        ('I', 'Inactive'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    label_name = models.CharField(max_length=50)
    price = models.FloatField()
    estatus = models.CharField(max_length=1, choices=STATUS_CHOICES)
    dateBill = models.DateField()
    tipo = models.CharField(max_length=20)
    category = models.CharField(max_length=20)
    class Meta:
        db_table = 'flow'
    def __str__(self):
        return self.label_name
