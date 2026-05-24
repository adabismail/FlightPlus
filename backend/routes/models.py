from django.db import models
from django.contrib.auth import get_user_model
 
User = get_user_model()   # gets our custom User, not Django's default
 
class TrackedRoute(models.Model):
    CABIN_CHOICES  = [('ECONOMY','Economy'),('PREMIUM_ECONOMY','Premium Economy'),
                      ('BUSINESS','Business'),('FIRST','First Class')]
    TRIP_TYPE      = [('ONE_WAY','One Way'),('ROUND_TRIP','Round Trip')]
    STATUS_CHOICES = [('ACTIVE','Active'),('PAUSED','Paused'),('EXPIRED','Expired')]
 
    user          = models.ForeignKey(User, on_delete=models.CASCADE,
                                      related_name='tracked_routes')
    from_city     = models.CharField(max_length=100)   # 'New Delhi'
    from_code     = models.CharField(max_length=3)     # 'DEL'  (IATA code)
    to_city       = models.CharField(max_length=100)
    to_code       = models.CharField(max_length=3)
    price_limit   = models.DecimalField(max_digits=10, decimal_places=2)
    currency      = models.CharField(max_length=3, default='INR')
    cabin_class   = models.CharField(max_length=20, choices=CABIN_CHOICES, default='ECONOMY')
    trip_type     = models.CharField(max_length=15, choices=TRIP_TYPE, default='ONE_WAY')
    adults        = models.PositiveSmallIntegerField(default=1)
    depart_date   = models.DateField(null=True, blank=True)
    return_date   = models.DateField(null=True, blank=True)
    flexible_dates= models.BooleanField(default=True)  # check ±3 days
    status        = models.CharField(max_length=10, choices=STATUS_CHOICES, default='ACTIVE')
    last_checked  = models.DateTimeField(null=True, blank=True)
    lowest_seen   = models.DecimalField(max_digits=10, decimal_places=2,
                                        null=True, blank=True)
    created_at    = models.DateTimeField(auto_now_add=True)
    updated_at    = models.DateTimeField(auto_now=True)
 
    class Meta:
        db_table = 'tracked_routes'
        ordering = ['-created_at']   # newest routes first
    
