from decimal import Decimal
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model

from routes.models import TrackedRoute

User = get_user_model()


def make_route(user, **overrides):
    data = dict(
        user=user, from_city='Delhi', from_code='DEL',
        to_city='Dubai', to_code='DXB', price_limit=Decimal('15000'),
    )
    data.update(overrides)
    return TrackedRoute.objects.create(**data)


class RouteApiTests(APITestCase):
    def setUp(self):
        self.user  = User.objects.create_user(email='a@b.com', name='A', password='pw')
        self.other = User.objects.create_user(email='c@d.com', name='C', password='pw')
        self.client.force_authenticate(self.user)

    def test_create_uppercases_iata_and_assigns_owner(self):
        r = self.client.post('/api/routes/', {
            'from_city': 'Delhi', 'from_code': 'del',
            'to_city': 'Dubai', 'to_code': 'dxb', 'price_limit': 15000,
        }, format='json')
        self.assertEqual(r.status_code, 201)
        self.assertEqual(r.data['from_code'], 'DEL')
        self.assertEqual(r.data['to_code'], 'DXB')
        self.assertEqual(TrackedRoute.objects.get(id=r.data['id']).user, self.user)

    def test_same_origin_destination_rejected(self):
        r = self.client.post('/api/routes/', {
            'from_city': 'Delhi', 'from_code': 'DEL',
            'to_city': 'Delhi', 'to_code': 'DEL', 'price_limit': 15000,
        }, format='json')
        self.assertEqual(r.status_code, 400)

    def test_round_trip_requires_return_date(self):
        r = self.client.post('/api/routes/', {
            'from_city': 'Delhi', 'from_code': 'DEL', 'to_city': 'Dubai', 'to_code': 'DXB',
            'price_limit': 15000, 'trip_type': 'ROUND_TRIP',
        }, format='json')
        self.assertEqual(r.status_code, 400)

    def test_users_only_see_own_routes(self):
        make_route(self.other, from_code='AAA', to_code='BBB')
        r = self.client.get('/api/routes/')
        self.assertEqual(len(r.data), 0)

    def test_pause_and_resume(self):
        route = make_route(self.user)
        self.assertEqual(self.client.post(f'/api/routes/{route.id}/pause/').status_code, 200)
        route.refresh_from_db()
        self.assertEqual(route.status, 'PAUSED')
        self.client.post(f'/api/routes/{route.id}/resume/')
        route.refresh_from_db()
        self.assertEqual(route.status, 'ACTIVE')

    def test_stats_includes_lowest_seen(self):
        make_route(self.user)
        r = self.client.get('/api/routes/stats/')
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.data['total_routes'], 1)
        self.assertIn('lowest_seen', r.data)

    def test_unauthenticated_blocked(self):
        self.client.force_authenticate(None)
        self.assertEqual(self.client.get('/api/routes/').status_code, 401)
