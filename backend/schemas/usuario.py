from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from backend.models import RolUsuario


class UsuarioOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    username: str
    nombre: str
    email: str | None
    rol: RolUsuario
    nit_empresa: str | None
    activo: bool
    primer_login: bool
    fecha_creacion: datetime
    ultimo_acceso: datetime | None


class UsuarioCreate(BaseModel):
    username: str = Field(min_length=3, max_length=50, pattern=r"^[a-zA-Z0-9_.-]+$")
    nombre: str = Field(min_length=1, max_length=100)
    email: EmailStr | None = None
    password: str = Field(min_length=8, max_length=128)
    rol: RolUsuario = RolUsuario.VIEWER
    nit_empresa: str | None = Field(default=None, max_length=9)


class UsuarioUpdate(BaseModel):
    nombre: str | None = None
    email: EmailStr | None = None
    rol: RolUsuario | None = None
    activo: bool | None = None
    nit_empresa: str | None = None
