from django.contrib import admin
from .models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display  = ('id', 'email', 'name', 'phone',
                     'notify_email', 'notify_sms', 'is_staff', 'date_joined')
    list_filter   = ('is_staff', 'is_active', 'notify_email', 'notify_sms')
    search_fields = ('email', 'name', 'phone')
    ordering      = ('-date_joined',)
    readonly_fields = ('date_joined', 'updated_at', 'last_login')
