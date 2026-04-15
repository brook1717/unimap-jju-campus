from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView,
)

urlpatterns = [
    path('admin/', admin.site.urls),

    # ── App APIs ──────────────────────────────────────────────────────────
    path('api/locations/', include('locations.urls')),
    path('api/facilities/', include('facilities.urls')),
    path('api/routing/', include('routing.urls')),
    path('api/users/', include('users.urls')),

    # ── OpenAPI 3.0 schema & interactive docs ─────────────────────────────
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]
