from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.api.deps import get_current_user
from backend.core.database import get_db
from backend.models import EstadoReporte, ReporteNomina, ReporteSS
from backend.schemas.reporte import ReporteNominaOut, ReporteSSOut


router = APIRouter(
    prefix="/api/reportes",
    tags=["reportes"],
    dependencies=[Depends(get_current_user)],
)


@router.get("/ss", response_model=list[ReporteSSOut])
def historial_ss(
    nit9: str | None = None,
    anio: int | None = None,
    mes: int | None = None,
    estado: EstadoReporte | None = None,
    db: Session = Depends(get_db),
) -> list[ReporteSS]:
    stmt = select(ReporteSS)
    if nit9:
        stmt = stmt.where(ReporteSS.nit9 == nit9)
    if anio is not None:
        stmt = stmt.where(ReporteSS.anio == anio)
    if mes is not None:
        stmt = stmt.where(ReporteSS.mes_obligacion == mes)
    if estado:
        stmt = stmt.where(ReporteSS.estado == estado)
    stmt = stmt.order_by(ReporteSS.anio.desc(), ReporteSS.mes_obligacion.desc(), ReporteSS.id.desc())
    return list(db.scalars(stmt))


@router.get("/ss/{reporte_id}", response_model=ReporteSSOut)
def detalle_ss(reporte_id: str, db: Session = Depends(get_db)) -> ReporteSS:
    rep = db.get(ReporteSS, reporte_id)
    if not rep:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Reporte SS no encontrado")
    return rep


@router.get("/nomina", response_model=list[ReporteNominaOut])
def historial_nomina(
    nit9: str | None = None,
    anio: int | None = None,
    mes: int | None = None,
    estado: EstadoReporte | None = None,
    db: Session = Depends(get_db),
) -> list[ReporteNomina]:
    stmt = select(ReporteNomina)
    if nit9:
        stmt = stmt.where(ReporteNomina.nit9 == nit9)
    if anio is not None:
        stmt = stmt.where(ReporteNomina.anio == anio)
    if mes is not None:
        stmt = stmt.where(ReporteNomina.mes_obligacion == mes)
    if estado:
        stmt = stmt.where(ReporteNomina.estado == estado)
    stmt = stmt.order_by(ReporteNomina.anio.desc(), ReporteNomina.mes_obligacion.desc())
    return list(db.scalars(stmt))


@router.get("/nomina/{reporte_id}", response_model=ReporteNominaOut)
def detalle_nomina(reporte_id: str, db: Session = Depends(get_db)) -> ReporteNomina:
    rep = db.get(ReporteNomina, reporte_id)
    if not rep:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Reporte Nómina no encontrado")
    return rep
