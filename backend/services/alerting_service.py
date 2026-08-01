import logging

from django.conf import settings
from django.core.mail import send_mail

logger = logging.getLogger(__name__)


def _headline(route, offer):
    return (f"{route.from_code} → {route.to_code} for "
            f"{offer['currency']} {offer['price']:,.0f}")


def send_deal_email(user, route, offer):
    """Send the deal email. Returns True on success, False otherwise."""
    subject = f"✈ Deal Alert: {_headline(route, offer)}"
    body = (
        f"Hi {user.name},\n\n"
        f"We found a flight under your target price!\n\n"
        f"  Route   : {route.from_city} ({route.from_code}) → "
        f"{route.to_city} ({route.to_code})\n"
        f"  Price   : {offer['currency']} {offer['price']:,.0f} "
        f"(your limit: {offer['currency']} {route.price_limit:,.0f})\n"
        f"  Airline : {offer['airline'] or offer['airline_code']} "
        f"({offer['flight_number']})\n"
        f"  Departs : {offer['departure_at']}\n"
        f"  Stops   : {offer['stops']}\n\n"
        f"Happy travels,\nFlightPulse"
    )
    try:
        send_mail(
            subject=subject,
            message=body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )
        return True
    except Exception as exc:
        logger.error('Email delivery failed for user %s: %s', user.id, exc)
        return False


def send_deal_sms(user, route, offer):
    """Send the deal SMS via Twilio. Returns True on success, False otherwise."""
    if not user.phone:
        logger.info('User %s has no phone number; skipping SMS.', user.id)
        return False
    try:
        # >>> API KEYS REQUIRED <<< TWILIO_ACCOUNT_SID / TWILIO_AUTH_TOKEN /
        # TWILIO_PHONE_NUMBER come from settings (read from .env).
        from twilio.rest import Client
        client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        client.messages.create(
            body=f"✈ Deal! {_headline(route, offer)} ({offer['flight_number']})",
            from_=settings.TWILIO_PHONE_NUMBER,
            to=user.phone,
        )
        return True
    except Exception as exc:
        logger.error('SMS delivery failed for user %s: %s', user.id, exc)
        return False


def dispatch_alert(user, route, offer):
    """Deliver across every channel the user has opted into."""
    report = {'email': False, 'sms': False}
    if user.notify_email:
        report['email'] = send_deal_email(user, route, offer)
    if user.notify_sms:
        report['sms'] = send_deal_sms(user, route, offer)
    if not any(report.values()):
        report['error'] = 'No notification channel enabled or all channels failed.'
    return report
