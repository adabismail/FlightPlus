from django.contrib import admin
from .models import TrackedRoute


@admin.register(TrackedRoute)
class TrackedRouteAdmin(admin.ModelAdmin):
    list_display  = ('id', 'user', 'from_code', 'to_code', 'price_limit',
                     'currency', 'cabin_class', 'status', 'lowest_seen', 'last_checked')
    list_filter   = ('status', 'cabin_class', 'trip_type', 'currency')
    search_fields = ('from_code', 'to_code', 'from_city', 'to_city', 'user__email')
    ordering      = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at', 'last_checked', 'lowest_seen')
