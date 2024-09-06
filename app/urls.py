from app import views
from django.contrib import admin
from django.urls import path

urlpatterns = [
    path('', views.home, name="home"),
    path('login/', views.login, name="login"),
    path('cadastro/', views.register, name="register"),

    path('finnac/', views.main, name="main"),

    path('finnac/wallet/', views.wallet, name="wallet"),
]