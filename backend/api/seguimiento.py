from datetime import date

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from backend.api.deps import get_current_user
from backend.core.database import get_db
from backend.models import EstadoSeguimiento, RolUsuario, SeguimientoMensual, Usuario
from backend.schemas.seguimiento import DashboardKPIs, SeguimientoMensualOut


router = APIRouter(
    prefix="/api/seguimiento",
    tags=["seguimiento"],
    dependencies=[Depends(get_current_user)],
)


@router.get("", response_model=list[SeguimientoMensualOut])
def listar(
    anio: int | None = None,
    mes: int | None = None,
    nit9: str | None = None,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[SeguimientoMensual]:
    # Empresa solo ve su propia data
    if current_user.rol == RolUsuario.EMPRESA:
        nit9 = current_user.nit_empresa

    stmt = select(SeguimientoMensual)
    if anio is not None:
        stmt = stmt.where(SeguimientoMensual.anio == anio)
    if mes is not None:
        stmt = stmt.where(SeguimientoMensual.mes == mes)
    if nit9:
        stmt = stmt.where(SeguimientoMensual.nit9 == nit9)
    stmt = stmt.order_by(
        SeguimientoMensual.anio.desc(),
        SeguimientoMensual.mes.desc(),
        SeguimientoMensual.nombre_empresa,
    )
    return list(db.scalars(stmt))


@router.get("/kpis", response_model=DashboardKPIs)
def kpis(
    anio: int | None = None,
    mes: int | None = None,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> DashboardKPIs:
    hoy = date.today()
    anio_q = anio or hoy.year
    mes_q = mes or hoy.month

    base = select(
        SeguimientoMensual.ss_estado, func.count()
    ).where(
        SeguimientoMensual.anio == anio_q,
        SeguimientoMensual.mes == mes_q,
    )

    # Empresa solo ve sus propios KPIs
    if current_user.rol == RolUsuario.EMPRESA and current_user.nit_empresa:
        base = base.where(SeguimientoMensual.nit9 == current_user.nit_empresa)

    base = base.group_by(SeguimientoMensual.ss_estado)
    counts: dict[EstadoSeguimiento | None, int] = dict(db.execute(base).all())
    total = sum(counts.values())

    return DashboardKPIs(
        total_empresas=total,
        cumple=counts.get(EstadoSeguimiento.CUMPLE, 0),
        en_mora=counts.get(EstadoSeguimiento.EN_MORA, 0),
        pendiente=counts.get(EstadoSeguimiento.PENDIENTE, 0),
        periodo_anio=anio_q,
        periodo_mes=mes_q,
    )
