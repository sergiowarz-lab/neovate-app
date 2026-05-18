"""Clase base de los validadores de planillas Neovate.

Portado desde el sistema legacy (validadores/base.py). Sin cambios funcionales.
"""

import re

MESES_ES = {
    "01": "ENERO",   "02": "FEBRERO",  "03": "MARZO",
    "04": "ABRIL",   "05": "MAYO",     "06": "JUNIO",
    "07": "JULIO",   "08": "AGOSTO",   "09": "SEPTIEMBRE",
    "10": "OCTUBRE", "11": "NOVIEMBRE", "12": "DICIEMBRE",
}


class ValidadorBase:
    OPERADOR: str | None = None
    TIPO_DOC: str | None = None
    HOJA_EXCEL: str = "SS"

    def __init__(self, metadata: dict, texto_pdf: str):
        self.metadata = metadata
        self.texto = texto_pdf
        self.fecha_pago: str | None = None

    @classmethod
    def detectar(cls, texto: str) -> bool:
        raise NotImplementedError(f"{cls.__name__} debe implementar detectar()")

    def validar_nit(self) -> bool:
        nit = self.metadata["nit"]
        if not nit:
            return False
        if nit in self.texto:
            return True
        pattern = r"[\s\.\-]*".join(re.escape(c) for c in nit)
        return bool(re.search(pattern, self.texto))

    def validar_periodo_universal(self) -> bool:
        anio = self.metadata["anio"]
        mes = self.metadata["mes"]
        periodo = f"{anio}-{mes}"
        mes_nombre = MESES_ES.get(mes, "")
        mes_num = str(int(mes))

        if re.search(rf"PENSI.NES?[\s\S]{{0,300}}?{re.escape(periodo)}", self.texto):
            return True
        if mes_nombre and re.search(rf"\b{mes_nombre}\b.{{0,50}}{anio}", self.texto):
            return True
        if periodo in self.texto:
            return True
        if re.search(rf"\b{mes_num}\s+{anio}\b", self.texto):
            return True
        return False

    def validar(self) -> tuple[bool, list[str]]:
        raise NotImplementedError(f"{self.__class__.__name__} debe implementar validar()")
