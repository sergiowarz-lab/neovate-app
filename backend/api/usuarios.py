"""CRUD de usuarios — sólo admin."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.api.deps import require_admin
from backend.core.database import get_db
from backend.core.security import hash_password
from backend.models import Usuario
from backend.schemas.usuario import UsuarioCreate, UsuarioOut, UsuarioUpdate


router = APIRouter(prefix="/api/usuarios", tags=["usuarios"], dependencies=[Depends(require_admin)])


@router.get("", response_model=list[UsuarioOut])
def listar(db: Session = Depends(get_db)) -> list[UsuarioOut]:
    return list(db.scalars(select(Usuario).order_by(Usuario.username)))


@router.post("", response_model=UsuarioOut, status_code=status.HTTP_201_CREATED)
def crear(payload: UsuarioCreate, db: Session = Depends(get_db)) -> Usuario:
    if db.get(Usuario, payload.username):
        raise HTTPException(status.HTTP_409_CONFLICT, "El usuario ya existe")

    nuevo = Usuario(
        username=payload.username,
        nombre=payload.nombre,
        email=str(payload.email) if payload.email else None,
        password_hash=hash_password(payload.password),
        rol=payload.rol,
        activo=True,
        primer_login=True,
    )
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    return nuevo


@router.patch("/{username}", response_model=UsuarioOut)
def actualizar(username: str, payload: UsuarioUpdate, db: Session = Depends(get_db)) -> Usuario:
    user = db.get(Usuario, username)
    if not user:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Usuario no encontrado")

    data = payload.model_dump(exclude_unset=True)
    if "email" in data and data["email"] is not None:
        data["email"] = str(data["email"])
    for k, v in data.items():
        setattr(user, k, v)
    db.commit()
    db.refresh(user)
    return user


@router.delete("/{username}", status_code=status.HTTP_204_NO_CONTENT)
def desactivar(username: str, db: Session = Depends(get_db)) -> None:
    user = db.get(Usuario, username)
    if not user:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Usuario no encontrado")
    user.activo = False
    db.commit()
