from unittest.mock import patch
from datetime import date, timedelta
from decimal import Decimal

from rest_framework.test import APITestCase
from django.test import TestCase
from django.contrib.auth import get_user_model

from routes.models import TrackedRoute
from alerts.models import Alert
from services import price_checker
from services.price_checker import _candidate_dates
from services.flight_service import filter_by_airlines

User = get_user_model()


def make_offer(price):
    """A normalized offer dict shaped like amadeus_service.normalize_offer()."""
    return {
        'price': price, 'currency': 'INR',
        'airline_code': 'EK', 'airline': 'Emirates', 'flight_number': 'EK512',
        'departure_at': None, 'arrival_at': None, 'duration': '3h25m',
        'stops': 0, 'raw': {'id': 'test-offer'},
    }


class PriceCheckerTests(TestCase):
    """Exercises the transform/load stage with Amadeus + delivery mocked out."""

    def setUp(self):
        self.user = User.objects.create_user(
            email='a@b.com', name='A', password='pw', notify_email=True)
        self.route = TrackedRoute.objects.create(
            user=self.user, from_city='Delhi', from_code='DEL',
            to_city='Dubai', to_code='DXB', price_limit=Decimal('15000'),
            depart_date=date.today() + timedelta(days=30), flexible_dates=False)

    @patch('services.price_checker.dispatch_alert', return_value={'email': True})
    @patch('services.price_checker.search_flight_offers')
    def test_deal_below_limit_creates_and_delivers_alert(self, mock_search, mock_dispatch):
        mock_search.return_value = [make_offer(12000.0)]
        created = price_checker.check_route_for_deals(self.route)

        self.assertEqual(len(created), 1)
        self.assertEqual(Alert.objects.count(), 1)
        alert = Alert.objects.first()
        self.assertEqual(alert.price, Decimal('12000'))
        self.assertEqual(alert.savings_amount, Decimal('3000'))
        self.assertTrue(alert.is_delivered)
        mock_dispatch.assert_called_once()

        self.route.refresh_from_db()
        self.assertEqual(self.route.lowest_seen, Decimal('12000'))
        self.assertIsNotNone(self.route.last_checked)

    @patch('services.price_checker.dispatch_alert')
    @patch('services.price_checker.search_flight_offers')
    def test_price_above_limit_creates_no_alert(self, mock_search, mock_dispatch):
        mock_search.return_value = [make_offer(20000.0)]
        created = price_checker.check_route_for_deals(self.route)

        self.assertEqual(created, [])
        self.assertEqual(Alert.objects.count(), 0)
        mock_dispatch.assert_not_called()
        # Bookkeeping still records the lowest price seen.
        self.route.refresh_from_db()
        self.assertEqual(self.route.lowest_seen, Decimal('20000'))

    @patch('services.price_checker.dispatch_alert')
    @patch('services.price_checker.search_flight_offers')
    def test_no_offers_is_safe(self, mock_search, mock_dispatch):
        mock_search.return_value = []
        created = price_checker.check_route_for_deals(self.route)
        self.assertEqual(created, [])
        self.assertEqual(Alert.objects.count(), 0)
        mock_dispatch.assert_not_called()


class AlertApiTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(email='a@b.com', name='A', password='pw')
        self.route = TrackedRoute.objects.create(
            user=self.user, from_city='Delhi', from_code='DEL',
            to_city='Dubai', to_code='DXB', price_limit=Decimal('15000'))
        Alert.objects.create(
            user=self.user, route=self.route, price=Decimal('12000'),
            airline_code='EK', channel='EMAIL', is_delivered=True)
        self.client.force_authenticate(self.user)

    def test_list_returns_user_alerts(self):
        r = self.client.get('/api/alerts/')
        self.assertEqual(r.status_code, 200)
        self.assertEqual(len(r.data), 1)
        self.assertEqual(r.data[0]['from_code'], 'DEL')

    def test_filter_by_airline_code(self):
        self.assertEqual(len(self.client.get('/api/alerts/?airline_code=EK').data), 1)
        self.assertEqual(len(self.client.get('/api/alerts/?airline_code=XX').data), 0)

    def test_alerts_are_read_only(self):
        # The viewset exposes no create route.
        self.assertEqual(self.client.post('/api/alerts/', {}, format='json').status_code, 405)


class SmartFilterTests(TestCase):
    """Preferred-airlines and weekends-only search filters."""

    def setUp(self):
        self.user = User.objects.create_user(email='sf@b.com', name='S', password='pw')

    def _route(self, depart, flexible=True, weekends=False, airlines=''):
        return TrackedRoute.objects.create(
            user=self.user, from_city='Delhi', from_code='DEL',
            to_city='Dubai', to_code='DXB', price_limit=Decimal('15000'),
            depart_date=depart, flexible_dates=flexible,
            weekends_only=weekends, preferred_airlines=airlines)

    def test_weekends_only_narrows_to_weekend_departures(self):
        # Start from a Wednesday so the ±3 window straddles a weekend.
        d = date.today() + timedelta(days=30)
        while d.weekday() != 2:           # 2 = Wednesday
            d += timedelta(days=1)
        dates = _candidate_dates(self._route(d, flexible=True, weekends=True))
        self.assertTrue(dates)
        self.assertTrue(all(x.weekday() >= 5 for x in dates))   # only Sat/Sun

    def test_preferred_airlines_filter(self):
        offers = [{'airline_code': 'EK', 'price': 100}, {'airline_code': 'AI', 'price': 120}]
        self.assertEqual(len(filter_by_airlines(offers, 'EK')), 1)
        self.assertEqual(filter_by_airlines(offers, 'EK')[0]['airline_code'], 'EK')
        # empty preference keeps everything
        self.assertEqual(len(filter_by_airlines(offers, '')), 2)
        # a preference that matches nothing falls back to all (don't hide every deal)
        self.assertEqual(len(filter_by_airlines(offers, 'XX')), 2)
