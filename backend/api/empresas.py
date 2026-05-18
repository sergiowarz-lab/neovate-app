from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from backend.api.deps import get_current_user
from backend.core.database import get_db
from backend.models import EmpresaAliada
from backend.schemas.empresa import EmpresaOut


router = APIRouter(
    prefix="/api/empresas",
    tags=["empresas"],
    dependencies=[Depends(get_current_user)],
)


@router.get("", response_model=list[EmpresaOut])
def listar(
    activa: bool | None = None,
    q: str | None = None,
    db: Session = Depends(get_db),
) -> list[EmpresaAliada]:
    stmt = select(EmpresaAliada)
    if activa is not None:
        stmt = stmt.where(EmpresaAliada.activa.is_(activa))
    if q:
        like = f"%{q}%"
        stmt = stmt.where(
            or_(
                EmpresaAliada.nombre_empresa.ilike(like),
                EmpresaAliada.nit.ilike(like),
                EmpresaAliada.nit9.ilike(like),
            )
        )
    stmt = stmt.order_by(EmpresaAliada.nombre_empresa)
    return list(db.scalars(stmt))


@router.get("/{nit9}", response_model=EmpresaOut)
def detalle(nit9: str, db: Session = Depends(get_db)) -> EmpresaAliada:
    empresa = db.scalar(select(EmpresaAliada).where(EmpresaAliada.nit9 == nit9))
    if not empresa:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Empresa no encontrada")
    return empresa
