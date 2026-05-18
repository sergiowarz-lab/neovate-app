from datetime import date, datetime

from pydantic import BaseModel, ConfigDict

from backend.models import EstadoReporte


class ReporteSSOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    nit: str
    nit9: str
    anio: int
    mes_obligacion: int
    operador: str | None
    aliado: str | None
    quien_envia: str | None
    tipo_planilla: str | None
    estado: EstadoReporte
    fecha_pago: date | None
    fecha_recepcion: datetime | None
    cantidad_validos: int | None
    rechazo: str | None


class ReporteNominaOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    nit: str
    nit9: str
    aliado: str | None
    anio: int
    mes_obligacion: int
    estado: EstadoReporte
    fecha_pago: date | None
    tipo_planilla: str | None
    cantidad_validos: int | None
    rechazo: str | None


class UploadResponse(BaseModel):
    """202 Accepted: la validación se procesa en segundo plano."""

    reporte_id: str
    operador_detectado: str | None = None
    hoja_destino: str
    mensaje: str = "PDF recibido y encolado para validación"
