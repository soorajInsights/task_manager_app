from django import forms
from accounts.models import CustomUser
from tasks.models import Task
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError


# ---------- Create Admin / SuperAdmin Form ----------
class CreateAdminForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, required=True, label="Password")

    class Meta:
        model = CustomUser
        fields = ("username", "email", "first_name", "last_name", "role", "password")
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Show only ADMIN and SUPERADMIN choices in the dropdown
        self.fields["role"].choices = [
            ("ADMIN", "Admin"),
            ("SUPERADMIN", "SuperAdmin"),
        ]

    def clean_role(self):
        role = self.cleaned_data.get("role")
        if role not in ("ADMIN", "SUPERADMIN"):
            raise forms.ValidationError("Invalid role.")
        return role

    def clean_password(self):
        password = self.cleaned_data.get("password")
        # Enforce strong password (uses settings.AUTH_PASSWORD_VALIDATORS)
        validate_password(password)   # raises ValidationError -> shown in the form
        return password

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if user.role in ("ADMIN", "SUPERADMIN"):
            user.is_staff = True
        if commit:
            user.save()
        return user

# ---------- Task Form ----------
class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ["title", "description", "assigned_to", "due_date", "status", "completion_report", "worked_hours"]

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

        # Add placeholder/help text for due_date field
        self.fields["due_date"].widget.attrs.update({
            "placeholder": "YYYY-MM-DD",
            "type": "date"  # browsers show date picker if supported
        })
        self.fields["due_date"].help_text = "Enter date in format YYYY-MM-DD."

        # Limit assigned_to choices depending on who is creating
        if user and user.is_admin():
            self.fields["assigned_to"].queryset = CustomUser.objects.filter(manager=user)
        elif user and user.is_superadmin():
            self.fields["assigned_to"].queryset = CustomUser.objects.filter(role="USER")


class AssignUserForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ["manager"]  # only assign admin

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Only Admins in the dropdown
        self.fields["manager"].queryset = CustomUser.objects.filter(role="ADMIN")

# ---------- User Form ----------
class CreateUserForm(forms.ModelForm):
    password1 = forms.CharField(
        widget=forms.PasswordInput,
        required=True,
        label="Password"
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput,
        required=True,
        label="Confirm Password"
    )

    class Meta:
        model = CustomUser
        fields = ("username", "email", "first_name", "last_name")

    def clean(self):
        cleaned_data = super().clean()
        p1 = cleaned_data.get("password1")
        p2 = cleaned_data.get("password2")

        if p1 and p2 and p1 != p2:
            raise forms.ValidationError("Passwords do not match.")

        if p1:
            validate_password(p1)  # enforces strong password rules
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        # Make sure role defaults to USER
        if not getattr(user, "role", None):
            user.role = "USER"
        # Set hashed password
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user

