from django.urls import path
from . import views

urlpatterns = [
    path('excel/', views.excel, name="excel"),
    path('pdf/', views.pdf, name="pdf"),
]