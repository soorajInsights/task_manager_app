from rest_framework.routers import DefaultRouter
from django.urls import path
from .views import AdminViewSet, otp_request_view, otp_verify_view

# DRF Router for AdminViewSet
router = DefaultRouter()
router.register(r"admins", AdminViewSet, basename="admins")

# Combine router URLs + custom paths
urlpatterns = [
    # Email OTP endpoints
    path("auth/otp/request/", otp_request_view, name="otp_request"),
    path("auth/otp/verify/", otp_verify_view, name="otp_verify"),
]

# Add router-generated URLs at the end
urlpatterns += router.urls
