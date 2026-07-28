from django.contrib import admin
from .models import Alert


@admin.register(Alert)
class AlertAdmin(admin.ModelAdmin):
    list_display  = ('id', 'user', 'route', 'price', 'currency', 'airline_code',
                     'flight_number', 'channel', 'is_delivered', 'alert_sent_at')
    list_filter   = ('channel', 'is_delivered', 'currency')
    search_fields = ('user__email', 'airline_code', 'flight_number')
    ordering      = ('-alert_sent_at',)
    readonly_fields = ('alert_sent_at', 'raw_offer')
