import re
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _

class ComplexPasswordValidator:
    def validate(self, password, user=None):
        if len(password) < 8:
            raise ValidationError(_("Password must be at least 8 characters long."))
        if not re.search(r"[A-Z]", password):
            raise ValidationError(_("Password must include at least one uppercase letter."))
        if not re.search(r"[a-z]", password):
            raise ValidationError(_("Password must include at least one lowercase letter."))
        if not re.search(r"\d", password):
            raise ValidationError(_("Password must include at least one digit."))
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
            raise ValidationError(_("Password must include at least one special character."))

    def get_help_text(self):
        return _("Use 8+ chars with upper, lower, a number, and a special character.")
