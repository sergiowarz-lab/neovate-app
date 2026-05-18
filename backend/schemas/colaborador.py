from pydantic import BaseModel, ConfigDict

from backend.models import CoberturaFlag


class ColaboradorOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    cedula: str
    nombres: str | None
    apellidos: str | None
    nit_empresa: str
    cargo: str | None
    nombre_empresa_legible: str | None
    anio: int
    mes: int
    existe_planilla: CoberturaFlag | None
    novedad_retiro: CoberturaFlag | None
    existe_nomina: CoberturaFlag | None
