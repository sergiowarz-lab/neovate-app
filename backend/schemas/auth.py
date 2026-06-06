from pydantic import BaseModel, Field

from backend.models import RolUsuario


class LoginRequest(BaseModel):
    username: str = Field(min_length=1, max_length=50)
    password: str = Field(min_length=1)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in_minutes: int
    primer_login: bool
    rol: RolUsuario
    nombre: str
    nit_empresa: str | None = None


class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str = Field(min_length=8, max_length=128)


class CurrentUserInfo(BaseModel):
    username: str
    nombre: str
    email: str | None
    rol: RolUsuario
    primer_login: bool
    nit_empresa: str | None = None
