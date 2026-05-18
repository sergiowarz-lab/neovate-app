import re

from backend.services.validadores.base import ValidadorBase
from backend.services.validadores.registry import registrar


@registrar
class ValidadorEnlaceResumen(ValidadorBase):
    """Enlace Operativo — Planilla Resumen (Autoliquidación Consolidada)."""

    OPERADOR = "ENLACE"
    TIPO_DOC = "RESUMEN"

    _MARCADORES = ["AUTOLIQUIDACION", "CONSOLIDADA"]
    _EXCLUIR = "PAGOSIMPLE"

    @classmethod
    def detectar(cls, texto: str) -> bool:
        return all(m in texto for m in cls._MARCADORES) and cls._EXCLUIR not in texto

    def validar_tipo_e(self) -> bool:
        return bool(re.search(r"TIPO\s+PLANILLA\s*:\s*E", self.texto))

    def validar_fecha_pago(self) -> bool:
        m = re.search(r"PAGADO\s+(\d{2}/\d{2}/\d{4})", self.texto)
        if not m:
            return False
        self.fecha_pago = m.group(1)
        return True

    def validar(self) -> tuple[bool, list[str]]:
        errores = []
        if not self.validar_nit():
            errores.append("NIT no coincide con el del archivo")
        if not self.validar_periodo_universal():
            errores.append("Periodo de pensión no coincide")
        self.validar_fecha_pago()
        if not self.validar_tipo_e():
            errores.append("No es planilla tipo E (Empresa)")
        return (False, errores) if errores else (True, [])
