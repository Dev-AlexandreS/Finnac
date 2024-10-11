from django.urls import path, include

urlpatterns = [
    path('', include('app.urls')),
    path('email/', include('emailSending.urls')),
]