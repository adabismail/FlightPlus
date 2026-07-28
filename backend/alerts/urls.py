# alerts/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AlertViewSet

router = DefaultRouter()
router.register('', AlertViewSet, basename='alert')
# DefaultRouter auto-creates:
#   GET /api/alerts/        → list (filterable)
#   GET /api/alerts/{id}/   → retrieve

urlpatterns = [path('', include(router.urls))]
