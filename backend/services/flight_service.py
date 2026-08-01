import logging
from datetime import datetime

import requests
from django.conf import settings

logger = logging.getLogger(__name__)

BASE_URL = 'https://sky-scrapper.p.rapidapi.com'
TIMEOUT = 20

# Map our cabin choices to Sky-Scrapper's cabinClass values.
_CABIN_MAP = {
    'ECONOMY': 'economy',
    'PREMIUM_ECONOMY': 'premium_economy',
    'BUSINESS': 'business',
    'FIRST': 'first',
}

# IATA -> (skyId, entityId), cached for the process lifetime to save API quota.
_AIRPORT_CACHE = {}


def _headers():
    # >>> API KEY REQUIRED <<< RAPIDAPI_KEY comes from settings (read from .env).
    return {
        'x-rapidapi-key': settings.RAPIDAPI_KEY or '',
        'x-rapidapi-host': settings.RAPIDAPI_HOST,
    }


def _get(path, params):
    resp = requests.get(f'{BASE_URL}{path}', headers=_headers(), params=params, timeout=TIMEOUT)
    resp.raise_for_status()
    return resp.json()


def resolve_airport(iata):
    """
    Map an IATA code (e.g. DEL) to Sky-Scrapper's (skyId, entityId). Cached.

    The IDs live under navigation.relevantFlightParams, and the first result can
    be a CITY (e.g. "DXB" -> Dubai city). We prefer the AIRPORT entity whose
    skyId matches the requested code.
    """
    iata = iata.upper()
    if iata in _AIRPORT_CACHE:
        return _AIRPORT_CACHE[iata]
    data = _get('/api/v1/flights/searchAirport', {'query': iata, 'locale': 'en-US'})
    results = data.get('data') or []

    def params_of(entry):
        return (entry.get('navigation') or {}).get('relevantFlightParams') or {}

    def entity_type(entry):
        return (entry.get('navigation') or {}).get('entityType')

    best = None
    # 1) exact AIRPORT match on skyId
    for x in results:
        if entity_type(x) == 'AIRPORT' and (params_of(x).get('skyId') or '').upper() == iata:
            best = params_of(x); break
    # 2) any AIRPORT
    if not best:
        for x in results:
            if entity_type(x) == 'AIRPORT':
                best = params_of(x); break
    # 3) fall back to the first result
    if not best and results:
        best = params_of(results[0])

    if not best or not best.get('skyId') or not best.get('entityId'):
        return None
    pair = (best['skyId'], best['entityId'])
    _AIRPORT_CACHE[iata] = pair
    return pair


def _parse_dt(value):
    if not value:
        return None
    try:
        return datetime.fromisoformat(value)
    except (ValueError, TypeError):
        return None


def _duration_label(minutes):
    if not minutes:
        return ''
    h, m = divmod(int(minutes), 60)
    return f'{h}h {m}m' if h else f'{m}m'


def normalize_offer(itinerary, currency):
    """Flatten one Sky-Scrapper itinerary into the shape our Alert model expects."""
    price    = float((itinerary.get('price') or {}).get('raw') or 0)
    leg      = (itinerary.get('legs') or [{}])[0]
    segment  = (leg.get('segments') or [{}])[0]
    # The segment's marketingCarrier carries the real IATA code (displayCode, e.g. "SG");
    # fall back to the leg-level carrier's alternateId if needed.
    mc       = segment.get('marketingCarrier') or {}
    leg_car  = ((leg.get('carriers') or {}).get('marketing') or [{}])[0]
    code     = str(mc.get('displayCode') or mc.get('alternateId') or leg_car.get('alternateId') or '')
    name     = mc.get('name') or leg_car.get('name') or ''
    flight_n = segment.get('flightNumber', '')
    return {
        'price':         price,
        'currency':      currency,
        'airline':       name,
        'airline_code':  code,
        'flight_number': f'{code} {flight_n}'.strip(),
        'departure_at':  _parse_dt(leg.get('departure')),
        'arrival_at':    _parse_dt(leg.get('arrival')),
        'duration':      _duration_label(leg.get('durationInMinutes')),
        'stops':         int(leg.get('stopCount') or 0),
        'raw':           itinerary,
    }


def filter_by_airlines(offers, preferred_csv):
    """Keep only offers on preferred airlines; fall back to all if that empties it."""
    codes = [c.strip().upper() for c in (preferred_csv or '').split(',') if c.strip()]
    if not codes:
        return offers
    filtered = [o for o in offers if o['airline_code'].upper() in codes]
    return filtered or offers


def search_flight_offers(route, depart_date, return_date=None, max_results=10):
    """
    Query Sky-Scrapper for offers on `route` departing `depart_date`.
    Returns normalized offer dicts sorted cheapest-first (may be empty on error).
    """
    try:
        origin = resolve_airport(route.from_code)
        dest   = resolve_airport(route.to_code)
        if not origin or not dest:
            logger.warning('Could not resolve airports %s/%s', route.from_code, route.to_code)
            return []

        params = {
            'originSkyId':         origin[0],
            'destinationSkyId':    dest[0],
            'originEntityId':      origin[1],
            'destinationEntityId': dest[1],
            'date':                depart_date.isoformat(),
            'cabinClass':          _CABIN_MAP.get(route.cabin_class, 'economy'),
            'adults':              route.adults,
            'sortBy':              'price_low',   # valid values: best, price_low, price_high, fastest, …
            'currency':            route.currency,
        }
        if return_date:
            params['returnDate'] = return_date.isoformat()

        data        = _get('/api/v2/flights/searchFlights', params)
        itineraries = (data.get('data') or {}).get('itineraries') or []
        offers      = [normalize_offer(it, route.currency) for it in itineraries[:max_results]]
        offers      = [o for o in offers if o['price'] > 0]
        offers      = filter_by_airlines(offers, route.preferred_airlines)
        offers.sort(key=lambda o: o['price'])
        return offers
    except requests.RequestException as exc:
        logger.warning('Sky-Scrapper search failed for %s→%s on %s: %s',
                       route.from_code, route.to_code, depart_date, exc)
        return []
    except Exception as exc:  # defensive: never let a parsing quirk crash the task
        logger.exception('Unexpected error parsing Sky-Scrapper response: %s', exc)
        return []
