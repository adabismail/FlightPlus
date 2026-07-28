from django.db import models
from django.contrib.auth import get_user_model
 
User = get_user_model()
 
class Alert(models.Model):
    user         = models.ForeignKey(User, on_delete=models.CASCADE, related_name='alerts')
    route        = models.ForeignKey('routes.TrackedRoute', on_delete=models.CASCADE,
                                     related_name='alerts')
    price        = models.DecimalField(max_digits=10, decimal_places=2)
    currency     = models.CharField(max_length=3, default='INR')
    airline      = models.CharField(max_length=100, blank=True)
    airline_code = models.CharField(max_length=5, blank=True)
    flight_number= models.CharField(max_length=20, blank=True)
    departure_at = models.DateTimeField(null=True, blank=True)
    arrival_at   = models.DateTimeField(null=True, blank=True)
    duration     = models.CharField(max_length=20, blank=True)
    stops        = models.PositiveSmallIntegerField(default=0)
    booking_url  = models.URLField(blank=True)
    channel      = models.CharField(max_length=10,
                       choices=[('EMAIL','Email'),('SMS','SMS'),('BOTH','Both')],
                       default='EMAIL')
    is_delivered  = models.BooleanField(default=False)
    delivery_error= models.TextField(blank=True)
    savings_amount= models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    savings_pct   = models.DecimalField(max_digits=5, decimal_places=1, null=True, blank=True)
    alert_sent_at = models.DateTimeField(auto_now_add=True)
    raw_offer     = models.JSONField(default=dict, blank=True)
 
    class Meta:
        db_table = 'alerts'
        ordering = ['-alert_sent_at']
