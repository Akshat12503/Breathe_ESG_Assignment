from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import EmissionActivityViewSet

router = DefaultRouter()
router.register(r'activities', EmissionActivityViewSet, basename='activity')

urlpatterns = [
    path('', include(router.urls)),
]