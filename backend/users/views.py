import random
from datetime import timedelta

from rest_framework import status, generics
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.conf import settings
from django.core.mail import send_mail
from django.utils import timezone

from .models import User, EmailOTP
from .serializers import RegisterSerializer, LoginSerializer, UserProfileSerializer

OTP_TTL_MINUTES = 10


def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)  # creates a refresh token
    return {
        'refresh': str(refresh),
        'access':  str(refresh.access_token),  # access token is embedded in refresh
    }


def issue_otp(email, name=''):
    """Create + email a fresh 6-digit code. In dev (console backend) it prints to logs."""
    code = f'{random.randint(0, 999999):06d}'
    EmailOTP.objects.create(
        email=email, code=code,
        expires_at=timezone.now() + timedelta(minutes=OTP_TTL_MINUTES),
    )
    send_mail(
        subject='Your FlightPulse verification code',
        message=(f'Hi {name or "there"},\n\n'
                 f'Your FlightPulse verification code is {code}.\n'
                 f'It expires in {OTP_TTL_MINUTES} minutes.\n\n— FlightPulse'),
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[email],
        fail_silently=True,
    )
    return code


class RegisterView(APIView):
    permission_classes = [AllowAny]  # no login needed to register

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()            # created inactive
            issue_otp(user.email, user.name)
            return Response({
                'detail': 'A verification code has been sent to your email.',
                'email':  user.email,
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=400)


class VerifyOTPView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = (request.data.get('email') or '').strip().lower()
        code  = (request.data.get('code') or '').strip()
        try:
            otp = EmailOTP.objects.filter(email=email).latest('created_at')
        except EmailOTP.DoesNotExist:
            return Response({'detail': 'No code found. Please request a new one.'}, status=400)
        if otp.code != code:
            return Response({'detail': 'Invalid code.'}, status=400)
        if otp.is_expired():
            return Response({'detail': 'Code expired. Please request a new one.'}, status=400)

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({'detail': 'Account not found.'}, status=404)

        user.is_active = True
        user.save(update_fields=['is_active'])
        EmailOTP.objects.filter(email=email).delete()   # one-time use
        return Response({
            'user':   UserProfileSerializer(user).data,
            'tokens': get_tokens_for_user(user),
        })


class ResendOTPView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = (request.data.get('email') or '').strip().lower()
        # Only (re)issue for accounts that still need verification.
        if User.objects.filter(email=email, is_active=False).exists():
            issue_otp(email)
        # Always respond the same way so we don't leak which emails exist.
        return Response({'detail': 'If your account needs verification, a new code was sent.'})


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            return Response({'user': UserProfileSerializer(user).data,
                             'tokens': get_tokens_for_user(user)})

        # Distinguish "wrong password" from "unverified account" for a clearer UX.
        email = (request.data.get('email') or '').strip().lower()
        user = User.objects.filter(email=email).first()
        if user and not user.is_active and user.check_password(request.data.get('password') or ''):
            return Response({'detail': 'Please verify your email first.',
                             'needs_verification': True, 'email': email}, status=403)
        return Response(serializer.errors, status=401)


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            token = RefreshToken(request.data.get('refresh'))
            token.blacklist()   # invalidate forever
            return Response({'detail': 'Logged out.'})
        except Exception:
            return Response({'detail': 'Invalid token.'}, status=400)


class UserProfileView(generics.RetrieveUpdateAPIView):
    serializer_class   = UserProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user  # return the currently logged-in user
