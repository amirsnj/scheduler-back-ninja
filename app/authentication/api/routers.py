from ninja import Router
from .auth import JWTAuth
from .schemas import (
    RegisterSchema, LoginSchema, TokenSchema,
    RefreshTokenSchema, MessageSchema, UserInfoOutSchema,
    UserUpdateSchema, ResetPasswordSchema
)
from ..services import AuthService


router = Router(tags=["Authentication"])


@router.get("/users/me", response=UserInfoOutSchema, auth=JWTAuth())
def get_user_info(request):
    return request.auth


@router.patch("/users/me", response=UserInfoOutSchema, auth=JWTAuth())
def update_current_user_info(request, data: UserUpdateSchema):

    new_data = AuthService.update_user_info(data_obj=request.auth, new_data=data.dict())

    return new_data

@router.post("/users/set_password", auth=JWTAuth(), response={204: MessageSchema, 400: MessageSchema})
def reset_password(request, data: ResetPasswordSchema):
    try:
        result = AuthService.reset_password(user_obj=request.auth, data=data.dict())
        return 204, result
    except ValueError as e:
        return 400, {"message": str(e)}


@router.post("/users", response={201: TokenSchema, 401: MessageSchema})
def register(request, data: RegisterSchema):
    try:
        user, tokens = AuthService.register_user(
            username=data.username,
            email=data.email,
            password=data.password,
            first_name=data.first_name,
            last_name=data.last_name
        )
        return 201, tokens
    except ValueError as e:
        return 401, {"message": str(e)}
    

@router.post("/jwt/create", response={200: TokenSchema, 401: MessageSchema})
def login(request, data: LoginSchema):
    tokens = AuthService.login_user(username=data.username, password=data.password)
    if tokens:
        return 200, tokens
    return 401, {"message": "Invalid credentials"}


@router.post("/jwt/refresh", response={200: TokenSchema, 401: MessageSchema})
def refresh_token(request, data: RefreshTokenSchema):
    try:
        tokens = AuthService.refresh_access_token(data.refresh)
        return 200, tokens
    except ValueError as e:
        return 401, {"message": str(e)}