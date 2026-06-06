"""Verificación de mora y disparo de notificaciones push."""

from __future__ import annotations

import logging
from datetime import date

from backend.core.database import SessionLocal
from backend.models import EmpresaAliada, EstadoSeguimiento, SeguimientoMensual

log = logging.getLogger("neovate.mora_checker")


def verificar_mora_empresa(nit9: str) -> None:
    """Verifica si una empresa está en mora en el período actual y notifica."""
    hoy = date.today()
    with SessionLocal() as db:
        seg = db.get(SeguimientoMensual, (nit9, hoy.year, hoy.month))
        if seg and seg.ss_estado == EstadoSeguimiento.EN_MORA:
            empresa = db.get(EmpresaAliada, seg.nit9) if seg else None
            nombre = empresa.nombre_empresa if empresa else seg.nombre_empresa or nit9
            from backend.services.push_service import notificar_mora
            count = notificar_mora(nit9, nombre)
            log.info("Mora notificada a %d suscriptores para empresa nit9=%s", count, nit9)


def verificar_todas_las_moras() -> None:
    """Job diario: recorre todas las empresas en mora del período actual y notifica."""
    hoy = date.today()
    log.info("Iniciando verificación diaria de mora %s/%s", hoy.month, hoy.year)

    with SessionLocal() as db:
        en_mora = db.query(SeguimientoMensual).filter(
            SeguimientoMensual.anio == hoy.year,
            SeguimientoMensual.mes == hoy.month,
            SeguimientoMensual.ss_estado == EstadoSeguimiento.EN_MORA,
        ).all()

        from backend.services.push_service import notificar_mora
        total = 0
        for seg in en_mora:
            empresa = db.query(EmpresaAliada).filter(EmpresaAliada.nit9 == seg.nit9).first()
            nombre = empresa.nombre_empresa if empresa else seg.nombre_empresa or seg.nit9
            total += notificar_mora(seg.nit9, nombre)

    log.info("Verificación diaria completada: %d notificaciones enviadas para %d empresas", total, len(en_mora))
