"""Autenticación: login, info del usuario, cambio de contraseña."""

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from backend.api.deps import get_current_user
from backend.core.config import settings
from backend.core.database import get_db
from backend.core.security import create_access_token, hash_password, verify_password
from backend.models import Usuario
from backend.schemas.auth import (
    ChangePasswordRequest,
    CurrentUserInfo,
    TokenResponse,
)


router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/token", response_model=TokenResponse)
def login(
    form: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
) -> TokenResponse:
    user = db.get(Usuario, form.username)
    if not user or not user.activo or not verify_password(form.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario o contraseña incorrectos",
        )

    user.ultimo_acceso = datetime.utcnow()
    db.commit()

    token = create_access_token(subject=user.username, extra_claims={"rol": user.rol.value})
    return TokenResponse(
        access_token=token,
        expires_in_minutes=settings.JWT_EXPIRE_MINUTES,
        primer_login=user.primer_login,
        rol=user.rol,
        nombre=user.nombre,
        nit_empresa=user.nit_empresa,
    )


@router.get("/me", response_model=CurrentUserInfo)
def me(user: Usuario = Depends(get_current_user)) -> CurrentUserInfo:
    return CurrentUserInfo(
        username=user.username,
        nombre=user.nombre,
        email=user.email,
        rol=user.rol,
        primer_login=user.primer_login,
        nit_empresa=user.nit_empresa,
    )


@router.post("/change-password", status_code=status.HTTP_204_NO_CONTENT)
def change_password(
    payload: ChangePasswordRequest,
    user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> None:
    if not verify_password(payload.old_password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La contraseña actual no es correcta",
        )
    user.password_hash = hash_password(payload.new_password)
    user.primer_login = False
    db.commit()
