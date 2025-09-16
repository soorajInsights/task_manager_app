from rest_framework.permissions import AllowAny
from drf_spectacular.utils import extend_schema
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
    TokenBlacklistView,
)

@extend_schema(tags=["Auth"])
class LoginView(TokenObtainPairView):
    permission_classes = [AllowAny]

@extend_schema(tags=["Auth"])
class RefreshView(TokenRefreshView):
    permission_classes = [AllowAny]

@extend_schema(tags=["Auth"])
class VerifyView(TokenVerifyView):
    permission_classes = [AllowAny]

@extend_schema(tags=["Auth"])
class LogoutView(TokenBlacklistView):
    # Blacklists a REFRESH token (body: {"refresh": "..."}).
    permission_classes = [AllowAny]
