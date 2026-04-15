from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import CampusPathViewSet, RouteView

router = DefaultRouter()
router.register(r'paths', CampusPathViewSet, basename='path')

urlpatterns = router.urls + [
    path('route/', RouteView.as_view(), name='route'),
]
