from app import views
from django.contrib import admin
from django.urls import path

urlpatterns = [
    path('', views.home, name="home"),

    path('login/', views.login, name="login"),
    path('cadastro/', views.register, name="register"),
    path('finnac/logout/', views.logout, name="logout"),
    path('finnac/', views.main, name="main"),
    path('finnac/wallet/', views.wallet, name="wallet"),
    path('finnac/wallet/add/', views.add, name="add"),
    path('delete/<int:id>', views.delete),
    path('finnac/generates/', views.generates, name="generates"),
]