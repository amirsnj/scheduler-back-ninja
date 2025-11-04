from django.contrib.auth import get_user_model, authenticate
from django.contrib.auth.hashers import check_password
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from .utils import auth_result, apply_password_policy


User = get_user_model()


class AuthService:

    @staticmethod
    def register_user(username, email, password, first_name, last_name):
        if User.objects.filter(username=username).exists():
            raise ValueError("Username already exitst")
        
        if User.objects.filter(email=email).exists():
            raise ValueError("Email already exitst")
        
        if not apply_password_policy(password):
            raise ValueError("The password length must be 8 or more.")
        
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name or "",
            last_name=last_name or ""
        )

        refresh = RefreshToken.for_user(user)

        tokens = auth_result(access=refresh.access_token, refresh=refresh)

        return user, tokens
    

    @staticmethod
    def login_user(username, password):
        user = authenticate(username=username, password=password)
        if user is None:
            return None
        
        refresh = RefreshToken.for_user(user)
        return auth_result(access=refresh.access_token, refresh=refresh)


    @staticmethod
    def refresh_access_token(refresh_token):
        try:
            refresh = RefreshToken(refresh_token)
            return auth_result(access=refresh. access_token, refresh=refresh)
        except TokenError:
            raise ValueError("Invalid or expired refresh token")
        

    @staticmethod
    def update_user_info(data_obj, new_data, allowed_fields=None):
        allowed_fields = allowed_fields or ["first_name", "last_name", "email"]

        for field, value in new_data.items():
            if field in allowed_fields and value is not None:
                setattr(data_obj, field, value)

        data_obj.save()
        return data_obj
    
    @staticmethod
    def reset_password(user_obj, data: dict):
        current_password = data.get("current_password")
        new_password = data.get("new_password")

        if not current_password or not new_password:
            raise ValueError("Missing required fields")
        
        if not apply_password_policy(new_password):
            raise ValueError("The password length must be 8 or more.")
        
        if not check_password(current_password, user_obj.password):
            raise ValueError("Current password is incorrect")
        
        if check_password(new_password, user_obj.password):
            raise ValueError("New password must be different")
        
        user_obj.set_password(new_password)
        user_obj.save()

        return {"message": "Password updated successfully."}