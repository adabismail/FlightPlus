from celery import shared_task
 
@shared_task(bind=True, name='scheduler.tasks.check_all_routes')
def check_all_routes(self):
    """Called by Celery Beat every day at 6 AM UTC."""
    from services.price_checker import check_all_active_routes
    total = check_all_active_routes()
    return {'alerts_sent': total}
 
@shared_task(bind=True, name='scheduler.tasks.check_single_route')
def check_single_route(self, route_id: int):
    """Called when user clicks 'Check Now' on a specific route."""
    from routes.models import TrackedRoute
    from services.price_checker import check_route_for_deals
    route  = TrackedRoute.objects.get(id=route_id)
    alerts = check_route_for_deals(route)
    return {'route_id': route_id, 'alerts_created': len(alerts)}
