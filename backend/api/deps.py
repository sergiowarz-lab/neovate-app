"""Dependencias compartidas de los routers FastAPI."""

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from sqlalchemy.orm import Session

from backend.core.database import get_db
from backend.core.security import decode_token
from backend.models import RolUsuario, Usuario


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/token")


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> Usuario:
    creds_exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credenciales inválidas o token expirado",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_token(token)
        username: str | None = payload.get("sub")
        if not username:
            raise creds_exc
    except JWTError as exc:
        raise creds_exc from exc

    user = db.get(Usuario, username)
    if not user or not user.activo:
        raise creds_exc
    return user


def require_admin(user: Usuario = Depends(get_current_user)) -> Usuario:
    if user.rol != RolUsuario.ADMIN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Se requiere rol admin")
    return user


def require_admin_or_analista(user: Usuario = Depends(get_current_user)) -> Usuario:
    if user.rol not in (RolUsuario.ADMIN, RolUsuario.ANALISTA):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Se requiere rol admin o analista"
        )
    return user


def require_can_upload(user: Usuario = Depends(get_current_user)) -> Usuario:
    """Permite subir planillas a admin, analista y empresa."""
    if user.rol not in (RolUsuario.ADMIN, RolUsuario.ANALISTA, RolUsuario.EMPRESA):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Sin permiso para cargar planillas"
        )
    return user
