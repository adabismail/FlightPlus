"""
Core deal-detection logic — the "transform + compare" stage of the ETL.

check_route_for_deals(route):
    fetch offers (with optional flexible-date spread), find the cheapest,
    update bookkeeping on the route, and if it beats the user's price limit
    create an Alert and dispatch the notification.
"""
import logging
from datetime import timedelta
from decimal import Decimal

from django.utils import timezone

from alerts.models import Alert
from services.flight_service import search_flight_offers
from services.alerting_service import dispatch_alert

logger = logging.getLogger(__name__)

# How many days either side of the target date to scan when flexible_dates is on.
FLEX_WINDOW = 3


def _candidate_dates(route):
    """Build the list of departure dates to scan for this route."""
    if not route.depart_date:
        return []
    if route.flexible_dates:
        today = timezone.now().date()
        dates = [route.depart_date + timedelta(days=d)
                 for d in range(-FLEX_WINDOW, FLEX_WINDOW + 1)
                 if route.depart_date + timedelta(days=d) >= today]
    else:
        dates = [route.depart_date]

    # Smart filter: weekends-only narrows the window to Sat/Sun departures,
    # but only if that still leaves something to check.
    if route.weekends_only:
        weekend = [d for d in dates if d.weekday() >= 5]   # 5=Sat, 6=Sun
        if weekend:
            dates = weekend
    return dates


def check_route_for_deals(route):
    """
    Returns a list of Alert objects created for this route (0 or 1 per run).
    """
    created = []
    dates = _candidate_dates(route)
    if not dates:
        logger.info('Route %s has no usable departure date; skipping.', route.id)
        return created

    # Gather the cheapest offer across every candidate date.
    cheapest = None
    for depart in dates:
        offers = search_flight_offers(
            route, depart,
            return_date=route.return_date if route.trip_type == 'ROUND_TRIP' else None,
        )
        if offers and (cheapest is None or offers[0]['price'] < cheapest['price']):
            cheapest = offers[0]

    # Bookkeeping happens whether or not we alerted.
    route.last_checked = timezone.now()
    if cheapest:
        price = Decimal(str(cheapest['price']))
        if route.lowest_seen is None or price < route.lowest_seen:
            route.lowest_seen = price
    route.save(update_fields=['last_checked', 'lowest_seen', 'updated_at'])

    if not cheapest:
        return created

    price = Decimal(str(cheapest['price']))
    if price > route.price_limit:
        logger.info('Route %s cheapest %s still above limit %s.',
                    route.id, price, route.price_limit)
        return created

    # Deal! Build the alert, then try to deliver it.
    savings     = route.price_limit - price
    savings_pct = (savings / route.price_limit * 100) if route.price_limit else Decimal('0')
    channel     = _channel_for(route.user)

    alert = Alert(
        user=route.user,
        route=route,
        price=price,
        currency=cheapest['currency'],
        airline=cheapest['airline'],
        airline_code=cheapest['airline_code'],
        flight_number=cheapest['flight_number'],
        departure_at=cheapest['departure_at'],
        arrival_at=cheapest['arrival_at'],
        duration=cheapest['duration'],
        stops=cheapest['stops'],
        channel=channel,
        savings_amount=savings,
        savings_pct=round(savings_pct, 1),
        raw_offer=cheapest['raw'],
    )

    report = dispatch_alert(route.user, route, cheapest)
    alert.is_delivered = any(report.values())
    if not alert.is_delivered:
        alert.delivery_error = report.get('error', 'No channel succeeded.')
    alert.save()

    created.append(alert)
    logger.info('Alert %s created for route %s at %s %s.',
                alert.id, route.id, price, cheapest['currency'])
    return created


def _channel_for(user):
    if user.notify_email and user.notify_sms:
        return 'BOTH'
    if user.notify_sms:
        return 'SMS'
    return 'EMAIL'
