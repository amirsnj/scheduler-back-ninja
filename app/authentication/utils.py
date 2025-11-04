from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password


def auth_result(access, refresh):
    return {
        "access": str(access),
        "refresh": str(refresh)
    }


def apply_password_policy(password: str, user=None):
    try:
        validate_password(password, user)
    except ValidationError:
        return False
    return True