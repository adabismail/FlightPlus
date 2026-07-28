# routes/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TrackedRouteViewSet
 
router = DefaultRouter()
router.register('', TrackedRouteViewSet, basename='route')
# DefaultRouter auto-creates:
#   GET  /api/routes/          → list
#   POST /api/routes/          → create
#   GET  /api/routes/{id}/     → retrieve
#   PATCH/PUT /api/routes/{id}/→ update
#   DELETE /api/routes/{id}/   → destroy
#   POST /api/routes/{id}/pause/     → pause action
#   POST /api/routes/{id}/check_now/ → check_now action
 
urlpatterns = [path('', include(router.urls))]
