from datetime import date

from pydantic import BaseModel, ConfigDict

from backend.models import EstadoSeguimiento


class SeguimientoMensualOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    nit9: str
    anio: int
    mes: int
    mes_nombre: str | None
    nombre_empresa: str | None

    ss_fecha_plazo: date | None
    ss_fecha_pago: date | None
    ss_estado: EstadoSeguimiento | None
    ss_dias_mora: int | None
    ss_fecha_verif: date | None

    nomina_fecha_plazo: date | None
    nomina_fecha_pago: date | None
    nomina_estado: EstadoSeguimiento | None
    nomina_dias_mora: int | None
    nomina_fecha_verif: date | None


class DashboardKPIs(BaseModel):
    total_empresas: int
    cumple: int
    en_mora: int
    pendiente: int
    periodo_anio: int
    periodo_mes: int
