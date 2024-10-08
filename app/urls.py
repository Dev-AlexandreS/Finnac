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
    path('edit/<int:id>', views.edit, name="edit"),
    path('finnac/generates/', views.generates, name="generates"),
    path('finnac/accounts/add/', views.addAccount, name="addAccount"),
    path('finnac/accounts/edit/', views.editAccount, name="editAccount"),
    path('finnac/accounts/delete/<int:id>/', views.deleteAccount, name="deleteAccount"),

    path('finnac/profile/', views.profile, name="profile"),
]