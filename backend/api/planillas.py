"""Upload de planillas con formulario explícito + polling de estado."""

import shutil
import tempfile
import uuid
from datetime import datetime
from pathlib import Path

from fastapi import APIRouter, BackgroundTasks, Depends, Form, HTTPException, UploadFile, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from backend.api.deps import get_current_user, require_can_upload
from backend.core.database import get_db
from backend.models import EmpresaAliada, EstadoReporte, ReporteNomina, ReporteSS, RolUsuario, Usuario
from backend.schemas.reporte import UploadResponse, UploadStatusResponse
from backend.services.procesador import procesar_pdf
from backend.services.validadores.parser_nombre import MESES
from backend.services.validadores.registry import listar_operadores, obtener_hoja_destino


router = APIRouter(
    prefix="/api/planillas",
    tags=["planillas"],
    dependencies=[Depends(get_current_user)],
)

_MESES_NUM_A_NOMBRE = {v: k for k, v in MESES.items()}

_UPLOAD_TMP = Path(tempfile.gettempdir()) / "neovate_uploads"
_UPLOAD_TMP.mkdir(parents=True, exist_ok=True)


@router.get("/operadores", response_model=list[str])
def listar_ops() -> list[str]:
    """Lista los operadores registrados en el sistema."""
    return listar_operadores()


@router.post("/upload", response_class=JSONResponse, status_code=status.HTTP_202_ACCEPTED)
def upload(
    background: BackgroundTasks,
    archivo: UploadFile,
    nit: str = Form(..., description="NIT de la empresa (9-15 dígitos)"),
    operador: str = Form(..., description="Operador de la planilla"),
    mes: str = Form(..., description="Mes en número (01-12)"),
    anio: int = Form(..., description="Año de la obligación"),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_can_upload),
) -> JSONResponse:
    """Recibe un PDF con los campos del formulario, construye el nombre estándar y encola validación."""
    if not archivo.filename or not archivo.filename.lower().endswith(".pdf"):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Solo se aceptan archivos .pdf")

    mes_str = mes.zfill(2)
    if mes_str not in _MESES_NUM_A_NOMBRE:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, f"Mes inválido: {mes}")
    mes_nombre = _MESES_NUM_A_NOMBRE[mes_str]

    nit_limpio = nit.strip().replace(" ", "").replace(".", "").replace("-", "")
    if not nit_limpio.isdigit() or not (9 <= len(nit_limpio) <= 15):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "NIT inválido (debe tener 9–15 dígitos)")

    operador_norm = operador.strip().upper()
    ops_validos = [o.upper() for o in listar_operadores()]
    if operador_norm not in ops_validos:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            f"Operador '{operador}' no reconocido. Válidos: {', '.join(listar_operadores())}",
        )

    reporte_id = str(uuid.uuid4())[:8].upper()
    timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
    nombre_normalizado = f"{reporte_id} - {nit_limpio} - {operador_norm} - {mes_nombre} - {anio} - {timestamp}.pdf"

    destino = _UPLOAD_TMP / nombre_normalizado
    with destino.open("wb") as f:
        shutil.copyfileobj(archivo.file, f)

    hoja = obtener_hoja_destino(operador_norm)
    nit9 = nit_limpio[:9]

    # Crear registro inicial con estado PROCESANDO para que el frontend pueda hacer polling
    _crear_registro_procesando(db, reporte_id, nit_limpio, nit9, mes_str, anio, operador_norm, hoja)

    background.add_task(procesar_pdf, str(destino), True)

    return JSONResponse(
        status_code=status.HTTP_202_ACCEPTED,
        content=UploadResponse(
            reporte_id=reporte_id,
            operador_detectado=operador_norm,
            hoja_destino=hoja,
        ).model_dump(),
    )


def _asegurar_empresa(db: Session, nit: str, nit9: str) -> None:
    """Crea la empresa en empresa_aliada si no existe (necesario para la FK de los reportes)."""
    if not db.query(EmpresaAliada).filter(EmpresaAliada.nit9 == nit9).first():
        db.add(EmpresaAliada(
            nit=nit,
            nit9=nit9,
            nombre_empresa=f"Empresa {nit9}",
            activa=True,
        ))
        db.flush()


def _crear_registro_procesando(
    db: Session,
    reporte_id: str,
    nit: str,
    nit9: str,
    mes: str,
    anio: int,
    operador: str,
    hoja: str,
) -> None:
    try:
        _asegurar_empresa(db, nit, nit9)
        if hoja == "Nomina":
            db.add(ReporteNomina(
                id=reporte_id,
                nit=nit,
                nit9=nit9,
                anio=anio,
                mes_obligacion=int(mes),
                estado=EstadoReporte.PROCESANDO,
            ))
        else:
            db.add(ReporteSS(
                id=reporte_id,
                nit=nit,
                nit9=nit9,
                anio=anio,
                mes_obligacion=int(mes),
                operador=operador,
                estado=EstadoReporte.PROCESANDO,
                fecha_recepcion=datetime.utcnow(),
            ))
        db.commit()
    except Exception:
        db.rollback()


@router.get("/status/{reporte_id}", response_model=UploadStatusResponse)
def estado_upload(reporte_id: str, db: Session = Depends(get_db)) -> UploadStatusResponse:
    """Polling del estado de procesamiento de una planilla subida."""
    rep_ss = db.get(ReporteSS, reporte_id)
    if rep_ss:
        return UploadStatusResponse(
            reporte_id=reporte_id,
            estado=rep_ss.estado,
            hoja_destino="SS",
            rechazo=rep_ss.rechazo,
        )
    rep_nom = db.get(ReporteNomina, reporte_id)
    if rep_nom:
        return UploadStatusResponse(
            reporte_id=reporte_id,
            estado=rep_nom.estado,
            hoja_destino="Nomina",
            rechazo=rep_nom.rechazo,
        )
    raise HTTPException(status.HTTP_404_NOT_FOUND, "Reporte no encontrado")


@router.post("/upload-ocr", response_class=JSONResponse, status_code=status.HTTP_202_ACCEPTED)
def upload_ocr(
    background: BackgroundTasks,
    nit: str = Form(...),
    operador: str = Form(...),
    mes: str = Form(...),
    anio: int = Form(...),
    texto_extraido: str = Form(..., description="Texto extraído por Tesseract.js en el cliente"),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_can_upload),
) -> JSONResponse:
    """Recibe texto OCR extraído en el cliente (móvil) y lo procesa con los validadores."""
    mes_str = mes.zfill(2)
    if mes_str not in _MESES_NUM_A_NOMBRE:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, f"Mes inválido: {mes}")

    nit_limpio = nit.strip().replace(" ", "").replace(".", "").replace("-", "")
    operador_norm = operador.strip().upper()

    reporte_id = str(uuid.uuid4())[:8].upper()
    timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
    hoja = obtener_hoja_destino(operador_norm)
    nit9 = nit_limpio[:9]

    _crear_registro_procesando(db, reporte_id, nit_limpio, nit9, mes_str, anio, operador_norm, hoja)

    from backend.services.procesador import procesar_texto_ocr
    background.add_task(
        procesar_texto_ocr,
        reporte_id,
        nit_limpio,
        operador_norm,
        mes_str,
        str(anio),
        timestamp,
        texto_extraido.upper(),
    )

    return JSONResponse(
        status_code=status.HTTP_202_ACCEPTED,
        content=UploadResponse(
            reporte_id=reporte_id,
            operador_detectado=operador_norm,
            hoja_destino=hoja,
        ).model_dump(),
    )
