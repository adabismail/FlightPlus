from rest_framework import serializers
from .models import Alert


class AlertSerializer(serializers.ModelSerializer):
    # Convenience fields for the dashboard so it doesn't need a second request.
    route_label = serializers.SerializerMethodField()
    from_code   = serializers.CharField(source='route.from_code', read_only=True)
    to_code     = serializers.CharField(source='route.to_code',   read_only=True)

    class Meta:
        model  = Alert
        fields = ('id', 'route', 'route_label', 'from_code', 'to_code',
                  'price', 'currency', 'airline', 'airline_code', 'flight_number',
                  'departure_at', 'arrival_at', 'duration', 'stops', 'booking_url',
                  'channel', 'is_delivered', 'delivery_error',
                  'savings_amount', 'savings_pct', 'alert_sent_at')
        read_only_fields = fields   # alerts are created by the system, never the client

    def get_route_label(self, obj):
        return f'{obj.route.from_code} → {obj.route.to_code}'
