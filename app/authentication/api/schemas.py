from ninja import Schema
from typing import Optional


class RegisterSchema(Schema):
    username: str
    email: str
    password: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None


class LoginSchema(Schema):
    username: str
    password: str


class TokenSchema(Schema):
    access: str
    refresh: str


class RefreshTokenSchema(Schema):
    refresh: str


class UserInfoOutSchema(Schema):
    id: int
    username: str
    email: str
    first_name: str
    last_name: str


class UserUpdateSchema(Schema):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None

class ResetPasswordSchema(Schema):
    new_password: str
    current_password: str


class MessageSchema(Schema):
    message: str