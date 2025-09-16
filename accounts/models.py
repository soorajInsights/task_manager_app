from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
import random

class CustomUser(AbstractUser):
    class Roles(models.TextChoices):
        SUPERADMIN = "SUPERADMIN", "SuperAdmin"
        ADMIN = "ADMIN", "Admin"
        USER = "USER", "User"

    role = models.CharField(max_length=20, choices=Roles.choices, default=Roles.USER)

    # Which Admin manages this user (for scoping tasks in the admin panel)
    manager = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="managed_users",
        limit_choices_to={"role": "ADMIN"},
    )


    def is_superadmin(self):
        return self.role == self.Roles.SUPERADMIN

    def is_admin(self):
        return self.role == self.Roles.ADMIN

    def is_user(self):
        return self.role == self.Roles.USER

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"

class EmailOTP(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    used_at = models.DateTimeField(null=True, blank=True)
    attempts = models.PositiveIntegerField(default=0)

    @classmethod
    def create_for_user(cls, user, lifetime_minutes=10):
        code = f"{random.randint(100000, 999999)}"  # 6-digit OTP
        return cls.objects.create(
            user=user,
            code=code,
            expires_at=timezone.now() + timedelta(minutes=lifetime_minutes),
        )

    def is_valid(self):
        return (
            self.used_at is None
            and timezone.now() < self.expires_at
            and self.attempts < 5
        )
