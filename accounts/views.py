from rest_framework import viewsets, permissions
from .models import CustomUser
from .serializers import UserSerializer
from django.contrib.auth import get_user_model, login
from django.core.mail import send_mail
from django.shortcuts import render, redirect
from django.utils import timezone
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
from django.conf import settings
from .models import EmailOTP
import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException
import os
from django.contrib import messages

class AdminViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Simple API to list Admins and SuperAdmins
    """
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return CustomUser.objects.filter(role__in=["ADMIN", "SUPERADMIN"])


User = get_user_model()

@require_http_methods(["GET", "POST"])
def otp_request_view(request):
    """
    Handles OTP email sending via Brevo REST API.
    GET: shows email form
    POST: generates OTP and sends via Brevo
    """
    if request.method == "GET":
        return render(request, "accounts/otp_request.html")

    email = (request.POST.get("email") or "").strip().lower()

    # --- Handle no user / duplicates gracefully ---
    users = User.objects.filter(email__iexact=email, is_active=True)
    if not users.exists():
        messages.error(request, "No account found with this email. Please create an account first.")
        return render(request, "accounts/otp_request.html")

    if users.count() > 1:
        messages.error(request, "Multiple accounts found with this email. Please contact support or use a different email.")
        return render(request, "accounts/otp_request.html")

    # We have exactly one user
    user = users.first()

    # Create OTP record
    otp = EmailOTP.create_for_user(user, lifetime_minutes=10)

    # ---------------- Brevo SDK Integration ----------------
    configuration = sib_api_v3_sdk.Configuration()
    BREVO_API_KEY = os.environ.get("BREVO_API_KEY")
    configuration.api_key['api-key'] = BREVO_API_KEY

    api_instance = sib_api_v3_sdk.TransactionalEmailsApi(sib_api_v3_sdk.ApiClient(configuration))

    subject = "Your One-Time Passcode"
    html_content = f"""
    <p>Hello,</p>
    <p>Your one-time passcode is: <strong>{otp.code}</strong></p>
    <p>This code will expire in 10 minutes.</p>
    """

    send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
        to=[{"email": email}],
        subject=subject,
        html_content=html_content,
        sender={"email": os.getenv("DEFAULT_FROM_EMAIL", "no-reply@yourdomain.com")}
    )

    try:
        api_instance.send_transac_email(send_smtp_email)
    except ApiException as e:
        messages.error(request, "Error sending email. Please try again later.")
        return render(request, "accounts/otp_request.html")
    # --------------------------------------------------------

    messages.success(request, "A one-time passcode has been sent to your email.")
    return redirect("otp_verify")  # Go to verify page

@require_http_methods(["GET", "POST"])
def otp_verify_view(request):
    """
    Verifies OTP entered by the user.
    GET: show form
    POST: check code
    """
    if request.method == "GET":
        return render(request, "accounts/otp_verify.html")

    email = (request.POST.get("email") or "").strip().lower()
    code = (request.POST.get("code") or "").strip()

    try:
        user = User.objects.get(email__iexact=email, is_active=True)
    except User.DoesNotExist:
        messages.error(request, "Invalid email or OTP.")
        return render(request, "accounts/otp_verify.html")

    # Look up OTP record
    otp_record = EmailOTP.objects.filter(user=user, code=code).order_by("-created_at").first()

    if not otp_record:
        messages.error(request, "Invalid OTP code.")
        return render(request, "accounts/otp_verify.html")

    # Check expiration
    if otp_record.expires_at < timezone.now():
        messages.error(request, "OTP has expired. Please request a new one.")
        return render(request, "accounts/otp_verify.html")

    # OTP is valid → log user in
    login(request, user)
    messages.success(request, "You are now logged in.")
    return redirect("admin_panel:dashboard")