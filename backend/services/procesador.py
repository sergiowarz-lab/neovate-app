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
from backend.models import EmpresaAliada, EstadoReporte, ReporteNomina, ReporteSS
from backend.services.cumplimiento import nit9, parse_fecha
from backend.services.validadores import (  # noqa: F401  — registra validadores
    aportes_en_linea, asopagos, compensar_miplanilla, enlace, nomina,
    simple_planilla, soi,
)
from backend.services.validadores.extractor import (
    PDFCorruptError,
    PDFEmptyError,
    PDFEncryptedError,
    PDFTimeoutError,
    extraer_texto_completo,
)
from backend.services.validadores.parser_nombre import parsear_nombre
from backend.services.validadores.registry import obtener_validador, obtener_hoja_destino

log = logging.getLogger("neovate.procesador")


def procesar_pdf(ruta: str, eliminar_temp: bool = True) -> None:
    """Procesa un PDF y persiste el resultado.

    Diseñado para correr dentro de fastapi.BackgroundTasks: cualquier excepción
    se registra en log y NO propaga (el cliente ya recibió su 202).
    """
    ruta_path = Path(ruta)
    reporte_id: str | None = None
    hoja: str = "SS"
    try:
        metadata = parsear_nombre(ruta_path.name)
        reporte_id = metadata["id"]
        texto = extraer_texto_completo(ruta_path)
        validador = obtener_validador(metadata["operador"], texto, metadata)
        hoja = obtener_hoja_destino(metadata["operador"])

        if validador is None:
            _persistir_sin_validador(metadata)
            log.warning("Sin validador para operador=%s id=%s", metadata["operador"], metadata["id"])
            return

        ok, errores = validador.validar()
        _persistir_resultado(metadata, validador, ok, errores, hoja)
        log.info("Validacion %s id=%s estado=%s", metadata["operador"], metadata["id"], "OK" if ok else "RECHAZADO")

        _notificar_planilla_subida(metadata, ok)

        if ok:
            _notificar_mora_si_aplica(metadata["nit"][:9])

    except PDFEncryptedError as exc:
        log.warning("PDF protegido %s: %s", ruta_path.name, exc)
        if reporte_id:
            _marcar_error(reporte_id, hoja, str(exc))
    except PDFEmptyError as exc:
        log.warning("PDF sin texto %s: %s", ruta_path.name, exc)
        if reporte_id:
            _marcar_error(reporte_id, hoja, str(exc))
    except PDFCorruptError as exc:
        log.warning("PDF corrupto %s: %s", ruta_path.name, exc)
        if reporte_id:
            _marcar_error(reporte_id, hoja, str(exc))
    except PDFTimeoutError as exc:
        log.error("Timeout extrayendo PDF %s: %s", ruta_path.name, exc)
        if reporte_id:
            _marcar_error(
                reporte_id, hoja,
                "El archivo tardó demasiado en procesarse. "
                "Verifique que el PDF no esté dañado o protegido e intente de nuevo.",
            )
    except Exception:
        log.exception("Error inesperado procesando PDF %s", ruta_path.name)
        if reporte_id:
            _marcar_error(reporte_id, hoja)
    finally:
        if eliminar_temp and ruta_path.exists():
            try:
                ruta_path.unlink()
            except OSError:
                log.warning("No se pudo eliminar archivo temporal %s", ruta_path)


def procesar_texto_ocr(
    reporte_id: str,
    nit_val: str,
    operador: str,
    mes: str,
    anio: str,
    timestamp: str,
    texto: str,
) -> None:
    """Procesa texto extraído por OCR (móvil) en lugar de un PDF."""
    metadata = {
        "id": reporte_id,
        "nit": nit_val,
        "operador": operador,
        "mes": mes,
        "anio": anio,
        "timestamp": timestamp,
    }
    hoja = obtener_hoja_destino(operador)
    try:
        validador = obtener_validador(operador, texto, metadata)
        if validador is None:
            _persistir_sin_validador(metadata)
            log.warning("OCR sin validador para operador=%s id=%s", operador, reporte_id)
            return

        ok, errores = validador.validar()
        _persistir_resultado(metadata, validador, ok, errores, hoja)
        log.info("OCR Validacion %s id=%s estado=%s", operador, reporte_id, "OK" if ok else "RECHAZADO")
    except Exception:
        log.exception("Error procesando OCR id=%s", reporte_id)
        _marcar_error(reporte_id, hoja)


def _marcar_error(
    reporte_id: str,
    hoja: str,
    mensaje: str = "Error interno al procesar el archivo",
) -> None:
    """Marca el registro PROCESANDO como RECHAZADO cuando hay una excepción inesperada."""
    with SessionLocal() as db:
        if hoja == "Nomina":
            rep = db.get(ReporteNomina, reporte_id)
        else:
            rep = db.get(ReporteSS, reporte_id)
        if rep and rep.estado == EstadoReporte.PROCESANDO:
            rep.estado = EstadoReporte.RECHAZADO
            rep.rechazo = mensaje
            db.commit()


def _notificar_mora_si_aplica(nit9: str) -> None:
    """Dispara notificaciones push si la empresa está actualmente en mora."""
    try:
        from backend.services.mora_checker import verificar_mora_empresa
        verificar_mora_empresa(nit9)
    except Exception:
        log.exception("Error verificando mora para nit9=%s", nit9)


def _asegurar_empresa(db, nit_full: str, nit_9: str) -> None:
    if not db.query(EmpresaAliada).filter(EmpresaAliada.nit9 == nit_9).first():
        db.add(EmpresaAliada(nit=nit_full, nit9=nit_9, nombre_empresa=f"Empresa {nit_9}", activa=True))
        db.flush()


def _persistir_resultado(metadata, validador, ok: bool, errores: list[str], hoja: str) -> None:
    fecha_pago = parse_fecha(validador.fecha_pago)
    nit_full = metadata["nit"]
    nit_9 = nit9(nit_full)
    anio_int = int(metadata["anio"])
    mes_int = int(metadata["mes"])
    estado = EstadoReporte.VALIDADO_OK if ok else EstadoReporte.RECHAZADO

    with SessionLocal() as db:
        _asegurar_empresa(db, nit_full, nit_9)
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


def _notificar_planilla_subida(metadata: dict, ok: bool) -> None:
    """Dispara push a todos los admins informando del resultado de la planilla."""
    try:
        from backend.services.push_service import notificar_planilla_subida
        from backend.services.cumplimiento import nit9 as _nit9
        from backend.core.database import SessionLocal
        from backend.models import EmpresaAliada

        nit_9 = _nit9(metadata["nit"])
        with SessionLocal() as db:
            empresa = db.query(EmpresaAliada).filter(EmpresaAliada.nit9 == nit_9).first()
            nombre = empresa.nombre_empresa if empresa else metadata["nit"]

        estado = "Validado_ok" if ok else "Rechazado"
        notificar_planilla_subida(
            nit=metadata["nit"],
            nombre_empresa=nombre,
            operador=metadata["operador"],
            mes=metadata["mes"],
            anio=metadata["anio"],
            estado=estado,
        )
    except Exception:
        log.exception("Error enviando push de planilla subida")


def _persistir_sin_validador(metadata) -> None:
    nit_full = metadata["nit"]
    nit_9 = nit9(nit_full)
    with SessionLocal() as db:
        _asegurar_empresa(db, nit_full, nit_9)
        db.merge(ReporteSS(
            id=metadata["id"],
            nit=nit_full,
            nit9=nit_9,
            anio=int(metadata["anio"]),
            mes_obligacion=int(metadata["mes"]),
            operador=metadata["operador"],
            estado=EstadoReporte.RECHAZADO,
            fecha_recepcion=datetime.utcnow(),
            rechazo=f"Sin validador registrado para operador '{metadata['operador']}'",
        ))
        db.commit()
