from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model

from .models import EmailOTP

User = get_user_model()

REG = {'name': 'Ada', 'email': 'ada@example.com',
       'password': 'flightpulse123', 'password2': 'flightpulse123'}


class AuthApiTests(APITestCase):
    def test_register_creates_inactive_user_and_issues_otp(self):
        r = self.client.post('/api/auth/register/', REG, format='json')
        self.assertEqual(r.status_code, 201)
        self.assertEqual(r.data['email'], 'ada@example.com')
        user = User.objects.get(email='ada@example.com')
        self.assertFalse(user.is_active)                       # not active until verified
        self.assertTrue(EmailOTP.objects.filter(email='ada@example.com').exists())

    def test_register_does_not_return_tokens(self):
        r = self.client.post('/api/auth/register/', REG, format='json')
        self.assertNotIn('tokens', r.data)

    def test_password_mismatch_rejected(self):
        bad = {**REG, 'password2': 'different'}
        r = self.client.post('/api/auth/register/', bad, format='json')
        self.assertEqual(r.status_code, 400)

    def test_verify_otp_activates_and_returns_tokens(self):
        self.client.post('/api/auth/register/', REG, format='json')
        otp = EmailOTP.objects.filter(email='ada@example.com').latest('created_at')
        r = self.client.post('/api/auth/verify-otp/',
                             {'email': 'ada@example.com', 'code': otp.code}, format='json')
        self.assertEqual(r.status_code, 200)
        self.assertIn('access', r.data['tokens'])
        self.assertTrue(User.objects.get(email='ada@example.com').is_active)
        self.assertFalse(EmailOTP.objects.filter(email='ada@example.com').exists())  # consumed

    def test_wrong_otp_rejected(self):
        self.client.post('/api/auth/register/', REG, format='json')
        r = self.client.post('/api/auth/verify-otp/',
                             {'email': 'ada@example.com', 'code': '000000'}, format='json')
        self.assertEqual(r.status_code, 400)

    def test_login_returns_tokens(self):
        User.objects.create_user(email='ada@example.com', name='Ada', password='flightpulse123')
        r = self.client.post('/api/auth/login/',
                             {'email': 'ada@example.com', 'password': 'flightpulse123'}, format='json')
        self.assertEqual(r.status_code, 200)
        self.assertIn('access', r.data['tokens'])

    def test_login_unverified_gets_verification_hint(self):
        User.objects.create_user(email='ada@example.com', name='Ada',
                                 password='flightpulse123', is_active=False)
        r = self.client.post('/api/auth/login/',
                             {'email': 'ada@example.com', 'password': 'flightpulse123'}, format='json')
        self.assertEqual(r.status_code, 403)
        self.assertTrue(r.data.get('needs_verification'))

    def test_login_bad_credentials(self):
        User.objects.create_user(email='ada@example.com', name='Ada', password='flightpulse123')
        r = self.client.post('/api/auth/login/',
                             {'email': 'ada@example.com', 'password': 'wrong'}, format='json')
        self.assertEqual(r.status_code, 401)

    def test_me_requires_auth(self):
        self.assertEqual(self.client.get('/api/auth/me/').status_code, 401)

    def test_me_returns_profile(self):
        user = User.objects.create_user(email='ada@example.com', name='Ada', password='flightpulse123')
        self.client.force_authenticate(user)
        r = self.client.get('/api/auth/me/')
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.data['email'], 'ada@example.com')
