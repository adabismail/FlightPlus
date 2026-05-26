from rest_framework import status, generics
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import RegisterSerializer, LoginSerializer, UserProfileSerializer
 
def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)  # creates a refresh token
    return {
        'refresh': str(refresh),
        'access':  str(refresh.access_token),  # access token is embedded in refresh
    }
 
class RegisterView(APIView):
    permission_classes = [AllowAny]  # no login needed to register
 
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({
                'user':   UserProfileSerializer(user).data,
                'tokens': get_tokens_for_user(user),
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=400)

class LoginView(APIView):
    permission_classes = [AllowAny]
 
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            return Response({'user': UserProfileSerializer(user).data,
                             'tokens': get_tokens_for_user(user)})
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


