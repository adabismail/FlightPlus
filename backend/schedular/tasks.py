from celery import shared_task


@shared_task(name='scheduler.tasks.check_all_routes')
def check_all_routes():
    """
    Called by Celery Beat every day at 6 AM UTC.

    Instead of checking every route inline, we *fan out* one independent
    task per active route. This is the ingest stage of the ETL pipeline:
    many small, retryable, parallelizable units of work.
    """
    from routes.models import TrackedRoute
    route_ids = list(
        TrackedRoute.objects.filter(status='ACTIVE').values_list('id', flat=True)
    )
    for route_id in route_ids:
        check_single_route.delay(route_id)
    return {'routes_dispatched': len(route_ids)}


@shared_task(bind=True, name='scheduler.tasks.check_single_route',
             max_retries=3, default_retry_delay=60)
def check_single_route(self, route_id: int):
    """
    Transform + load stage: fetch live prices for one route, compare against
    the threshold, and persist/deliver an alert if a deal is found.
    Retries transient failures (e.g. Amadeus hiccups) up to 3 times.
    """
    from routes.models import TrackedRoute
    from services.price_checker import check_route_for_deals
    try:
        route = TrackedRoute.objects.get(id=route_id)
    except TrackedRoute.DoesNotExist:
        return {'route_id': route_id, 'error': 'route not found'}

    try:
        alerts = check_route_for_deals(route)
    except Exception as exc:
        raise self.retry(exc=exc)

    return {'route_id': route_id, 'alerts_created': len(alerts)}
