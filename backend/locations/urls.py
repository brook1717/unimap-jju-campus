from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import CampusLocationViewSet

router = DefaultRouter()
router.register(r'', CampusLocationViewSet, basename='location')

urlpatterns = [
    path('', include(router.urls)),
]
