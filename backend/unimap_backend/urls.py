from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/locations/', include('locations.urls')),
    path('api/facilities/', include('facilities.urls')),
    path('api/routing/', include('routing.urls')),
    path('api/users/', include('users.urls')),
]
