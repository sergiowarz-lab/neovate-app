from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.api.deps import get_current_user
from backend.core.database import get_db
from backend.models import Colaborador
from backend.schemas.colaborador import ColaboradorOut


router = APIRouter(
    prefix="/api/colaboradores",
    tags=["colaboradores"],
    dependencies=[Depends(get_current_user)],
)


@router.get("", response_model=list[ColaboradorOut])
def listar(
    nit9: str | None = None,
    anio: int | None = None,
    mes: int | None = None,
    db: Session = Depends(get_db),
) -> list[Colaborador]:
    stmt = select(Colaborador)
    if nit9:
        stmt = stmt.where(Colaborador.nit_empresa == nit9)
    if anio is not None:
        stmt = stmt.where(Colaborador.anio == anio)
    if mes is not None:
        stmt = stmt.where(Colaborador.mes == mes)
    stmt = stmt.order_by(Colaborador.apellidos, Colaborador.nombres)
    return list(db.scalars(stmt))
