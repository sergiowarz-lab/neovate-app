"""Procesador de PDFs Neovate — se ejecuta en BackgroundTasks tras un upload.

Responsable de:
 1. Parsear el nombre del archivo (parser_nombre.parsear_nombre).
 2. Extraer el texto del PDF (extractor.extraer_texto_completo).
 3. Resolver el validador correspondiente (registry.obtener_validador).
 4. Ejecutar validar() y registrar el resultado en la BD (ReporteSS o ReporteNomina).
"""

from __future__ import annotations

import logging
from datetime import datetime
from pathlib import Path

from backend.core.database import SessionLocal
from backend.models import EstadoReporte, ReporteNomina, ReporteSS
from backend.services.cumplimiento import nit9, parse_fecha
from backend.services.validadores import (  # noqa: F401  — registra validadores
    aportes_en_linea, asopagos, compensar_miplanilla, enlace, nomina,
    simple_planilla, soi,
)
from backend.services.validadores.extractor import extraer_texto_completo
from backend.services.validadores.parser_nombre import parsear_nombre
from backend.services.validadores.registry import obtener_validador, obtener_hoja_destino

log = logging.getLogger("neovate.procesador")


def procesar_pdf(ruta: str, eliminar_temp: bool = True) -> None:
    """Procesa un PDF y persiste el resultado.

    Diseñado para correr dentro de fastapi.BackgroundTasks: cualquier excepción
    se registra en log y NO propaga (el cliente ya recibió su 202).
    """
    ruta_path = Path(ruta)
    try:
        metadata = parsear_nombre(ruta_path.name)
        texto = extraer_texto_completo(ruta_path)
        validador = obtener_validador(metadata["operador"], texto, metadata)

        if validador is None:
            _persistir_sin_validador(metadata)
            log.warning("Sin validador para operador=%s id=%s", metadata["operador"], metadata["id"])
            return

        ok, errores = validador.validar()
        hoja = obtener_hoja_destino(metadata["operador"])
        _persistir_resultado(metadata, validador, ok, errores, hoja)
        log.info("Validacion %s id=%s estado=%s", metadata["operador"], metadata["id"], "OK" if ok else "RECHAZADO")
    except Exception:
        log.exception("Error procesando PDF %s", ruta_path.name)
    finally:
        if eliminar_temp and ruta_path.exists():
            try:
                ruta_path.unlink()
            except OSError:
                log.warning("No se pudo eliminar archivo temporal %s", ruta_path)


def _persistir_resultado(metadata, validador, ok: bool, errores: list[str], hoja: str) -> None:
    fecha_pago = parse_fecha(validador.fecha_pago)
    nit_full = metadata["nit"]
    nit_9 = nit9(nit_full)
    anio_int = int(metadata["anio"])
    mes_int = int(metadata["mes"])
    estado = EstadoReporte.VALIDADO_OK if ok else EstadoReporte.RECHAZADO

    with SessionLocal() as db:
        if hoja == "Nomina":
            existente = db.get(ReporteNomina, metadata["id"])
            if existente:
                existente.estado = estado
                existente.fecha_pago = fecha_pago
                existente.rechazo = "; ".join(errores) if errores else None
                existente.tipo_planilla = validador.TIPO_DOC
            else:
                db.add(ReporteNomina(
                    id=metadata["id"],
                    nit=nit_full,
                    nit9=nit_9,
                    anio=anio_int,
                    mes_obligacion=mes_int,
                    estado=estado,
                    fecha_pago=fecha_pago,
                    tipo_planilla=validador.TIPO_DOC,
                    cantidad_validos=1 if ok else 0,
                    rechazo="; ".join(errores) if errores else None,
                ))
        else:
            existente = db.get(ReporteSS, metadata["id"])
            if existente:
                existente.estado = estado
                existente.fecha_pago = fecha_pago
                existente.operador = validador.OPERADOR
                existente.tipo_planilla = validador.TIPO_DOC
                existente.rechazo = "; ".join(errores) if errores else None
            else:
                db.add(ReporteSS(
                    id=metadata["id"],
                    nit=nit_full,
                    nit9=nit_9,
                    anio=anio_int,
                    mes_obligacion=mes_int,
                    operador=validador.OPERADOR,
                    tipo_planilla=validador.TIPO_DOC,
                    estado=estado,
                    fecha_pago=fecha_pago,
                    fecha_recepcion=datetime.utcnow(),
                    cantidad_validos=1 if ok else 0,
                    rechazo="; ".join(errores) if errores else None,
                ))
        db.commit()


def _persistir_sin_validador(metadata) -> None:
    nit_full = metadata["nit"]
    with SessionLocal() as db:
        db.merge(ReporteSS(
            id=metadata["id"],
            nit=nit_full,
            nit9=nit9(nit_full),
            anio=int(metadata["anio"]),
            mes_obligacion=int(metadata["mes"]),
            operador=metadata["operador"],
            estado=EstadoReporte.RECHAZADO,
            fecha_recepcion=datetime.utcnow(),
            rechazo=f"Sin validador registrado para operador '{metadata['operador']}'",
        ))
        db.commit()
