from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
 
class TrackedRouteViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
 
    def get_queryset(self):
        # CRITICAL: users can only see THEIR OWN routes
        return TrackedRoute.objects.filter(user=self.request.user)
 
    @action(detail=True, methods=['post'])    # POST /routes/5/pause/
    def pause(self, request, pk=None):
        route = self.get_object()
        route.status = 'PAUSED'
        route.save()
        return Response({'status': 'paused'})
 
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
        })

