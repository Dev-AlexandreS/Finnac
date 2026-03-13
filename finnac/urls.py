from django.urls import path, include
from django.contrib import admin

urlpatterns = [
    path('', include('app.urls')),
    path('email/', include('emailSending.urls')),
    path('generate/', include('generate.urls')),
    path('admin/', admin.site.urls),
]