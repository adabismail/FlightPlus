from rest_framework import serializers
from .models import TrackedRoute


class TrackedRouteSerializer(serializers.ModelSerializer):
    class Meta:
        model  = TrackedRoute
        fields = '__all__'
        # These are managed by the server / background jobs, never set by the client.
        read_only_fields = ('id', 'user', 'status', 'last_checked',
                            'lowest_seen', 'created_at', 'updated_at')

    def validate_price_limit(self, value):
        if value <= 0:
            raise serializers.ValidationError('Price limit must be greater than zero.')
        return value

    def validate(self, attrs):
        for key in ('from_code', 'to_code'):
            if key in attrs:
                attrs[key] = attrs[key].upper()

        if 'preferred_airlines' in attrs and attrs['preferred_airlines']:
            attrs['preferred_airlines'] = attrs['preferred_airlines'].upper().replace(' ', '')

        from_code = attrs.get('from_code')
        to_code   = attrs.get('to_code')
        if from_code and to_code and from_code == to_code:
            raise serializers.ValidationError('Origin and destination must differ.')

        trip_type   = attrs.get('trip_type', getattr(self.instance, 'trip_type', 'ONE_WAY'))
        depart_date = attrs.get('depart_date', getattr(self.instance, 'depart_date', None))
        return_date = attrs.get('return_date', getattr(self.instance, 'return_date', None))
        if trip_type == 'ROUND_TRIP':
            if not return_date:
                raise serializers.ValidationError('Round trips require a return date.')
            if depart_date and return_date < depart_date:
                raise serializers.ValidationError('Return date cannot be before departure date.')
        return attrs

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)
