from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenRefreshView
from users.views import LoginView, RegisterView, LogoutView, UserProfileView
 
urlpatterns = [
    path('admin/', admin.site.urls),
    # Auth endpoints
    path('api/auth/register/', RegisterView.as_view()),
    path('api/auth/login/',    LoginView.as_view()),
    path('api/auth/logout/',   LogoutView.as_view()),
    path('api/auth/refresh/',  TokenRefreshView.as_view()),
    path('api/auth/me/',       UserProfileView.as_view()),
    # App endpoints (delegated to each app's urls.py)
    path('api/routes/',  include('routes.urls')),
    path('api/alerts/',  include('alerts.urls')),
]
