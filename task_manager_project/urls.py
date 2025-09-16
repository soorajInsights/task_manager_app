from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView
from django.views.generic import RedirectView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

# use your wrappers (nice tags in docs)
from accounts.api_auth import LoginView, RefreshView, VerifyView, LogoutView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("admin_panel/", include("admin_panel.urls")),

    # --- Auth (JWT) ---
    path("api/v1/auth/login/",   LoginView.as_view(),   name="auth_login"),
    path("api/v1/auth/refresh/", RefreshView.as_view(), name="auth_refresh"),
    path("api/v1/auth/verify/",  VerifyView.as_view(),  name="auth_verify"),
    path("api/v1/auth/logout/",  LogoutView.as_view(),  name="auth_logout"),

    
    path("api/v1/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/v1/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),

    # App routes
    path("api/v1/accounts/", include("accounts.urls")),
    path("api/v1/tasks/", include("tasks.urls")),

    # OpenAPI schema & docs
    path("api/v1/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/v1/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path("api/v1/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),

    path("", RedirectView.as_view(url="/admin_panel/")),
]
