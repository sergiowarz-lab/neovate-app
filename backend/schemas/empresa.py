from pydantic import BaseModel, ConfigDict


class EmpresaOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    nit: str
    nit9: str
    nombre_empresa: str
    primer_mes: int | None
    primer_anio: int | None
    ultimo_mes: int | None
    ultimo_anio: int | None
    activa: bool
