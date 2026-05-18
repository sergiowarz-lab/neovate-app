"""Upload asíncrono de planillas: encola validación con BackgroundTasks → 202."""

import shutil
import tempfile
from pathlib import Path

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, UploadFile, status
from fastapi.responses import JSONResponse

from backend.api.deps import get_current_user
from backend.schemas.reporte import UploadResponse
from backend.services.procesador import procesar_pdf
from backend.services.validadores.parser_nombre import parsear_nombre
from backend.services.validadores.registry import obtener_hoja_destino


router = APIRouter(
    prefix="/api/planillas",
    tags=["planillas"],
    dependencies=[Depends(get_current_user)],
)


_UPLOAD_TMP = Path(tempfile.gettempdir()) / "neovate_uploads"
_UPLOAD_TMP.mkdir(parents=True, exist_ok=True)


@router.post("/upload", response_class=JSONResponse, status_code=status.HTTP_202_ACCEPTED)
def upload(
    background: BackgroundTasks,
    archivo: UploadFile,
) -> JSONResponse:
    """Recibe un PDF, parsea nombre, encola validación, devuelve 202."""
    if not archivo.filename or not archivo.filename.lower().endswith(".pdf"):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Sólo se aceptan archivos .pdf")

    try:
        metadata = parsear_nombre(archivo.filename)
    except ValueError as exc:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, str(exc)) from exc

    destino = _UPLOAD_TMP / f"{metadata['id']}__{archivo.filename}"
    with destino.open("wb") as f:
        shutil.copyfileobj(archivo.file, f)

    background.add_task(procesar_pdf, str(destino), True)

    return JSONResponse(
        status_code=status.HTTP_202_ACCEPTED,
        content=UploadResponse(
            reporte_id=metadata["id"],
            operador_detectado=metadata["operador"],
            hoja_destino=obtener_hoja_destino(metadata["operador"]),
        ).model_dump(),
    )
