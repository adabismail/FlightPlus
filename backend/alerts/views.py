from rest_framework import viewsets, mixins
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend

from .models import Alert
from .serializers import AlertSerializer


class AlertViewSet(mixins.ListModelMixin,
                   mixins.RetrieveModelMixin,
                   viewsets.GenericViewSet):
    """Read-only history of triggered alerts for the current user."""
    serializer_class   = AlertSerializer
    permission_classes = [IsAuthenticated]
    filter_backends    = [DjangoFilterBackend]
    # Smart filters: GET /api/alerts/?route=5&airline_code=EK&channel=EMAIL
    filterset_fields   = ['route', 'airline_code', 'channel', 'is_delivered']

    def get_queryset(self):
        return (Alert.objects
                .filter(user=self.request.user)
                .select_related('route'))   # avoids N+1 on route_label / from_code
