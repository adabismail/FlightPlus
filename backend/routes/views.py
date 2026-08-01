from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Min

from .models import TrackedRoute
from .serializers import TrackedRouteSerializer
from alerts.models import Alert
from schedular.tasks import check_single_route


class TrackedRouteViewSet(viewsets.ModelViewSet):
    serializer_class   = TrackedRouteSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return TrackedRoute.objects.filter(user=self.request.user)

    @action(detail=True, methods=['post'])    # POST /routes/5/pause/
    def pause(self, request, pk=None):
        route = self.get_object()
        route.status = 'PAUSED'
        route.save(update_fields=['status', 'updated_at'])
        return Response({'status': 'paused'})

    @action(detail=True, methods=['post'])    # POST /routes/5/resume/
    def resume(self, request, pk=None):
        route = self.get_object()
        route.status = 'ACTIVE'
        route.save(update_fields=['status', 'updated_at'])
        return Response({'status': 'active'})

    @action(detail=True, methods=['post'])    # POST /routes/5/check_now/
    def check_now(self, request, pk=None):
        route = self.get_object()
        check_single_route.delay(route.id)   # queues a Celery task
        return Response({'detail': 'Price check initiated.'})

    @action(detail=False, methods=['get'])   # GET /routes/stats/
    def stats(self, request):
        routes = self.get_queryset()
        return Response({
            'total_routes':  routes.count(),
            'active_routes': routes.filter(status='ACTIVE').count(),
            'total_alerts':  Alert.objects.filter(user=request.user).count(),
            'lowest_seen':   routes.aggregate(v=Min('lowest_seen'))['v'],
        })
