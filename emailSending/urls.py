from django.urls import path
from . import views

urlpatterns = [
    path('', views.email, name="email"),
     path('finnac/auth/recoverypassword/', views.recoverypassword, name="recoverypassword"),
]