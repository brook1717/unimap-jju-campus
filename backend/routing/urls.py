from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import CampusPathViewSet, DirectionsView

router = DefaultRouter()
router.register(r'paths', CampusPathViewSet, basename='path')

urlpatterns = router.urls + [
    path('directions/', DirectionsView.as_view(), name='directions'),
]
