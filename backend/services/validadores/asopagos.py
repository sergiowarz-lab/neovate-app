import re

from backend.services.validadores.base import ValidadorBase
from backend.services.validadores.registry import registrar


@registrar
class ValidadorAsopagosResumenTipo1(ValidadorBase):
    """Asopagos — Resumen tipo 1: Planilla PAGADA."""

    OPERADOR = "ASOPAGOS"
    TIPO_DOC = "RESUMEN_TIPO1"

    _MARCADOR = "RESUMEN PLANILLA PAGADA"

    @classmethod
    def detectar(cls, texto: str) -> bool:
        return cls._MARCADOR in texto

    def validar_tipo_e(self) -> bool:
        return bool(re.search(r"TIPO\s+PLANILLA[\s\S]{0,150}\bE\b", self.texto))

    def validar_fecha_pago(self) -> bool:
        m = re.search(r"\bE\s+(\d{4}-\d{2}-\d{2})", self.texto)
        if not m:
            m = re.search(r"(\d{4}-\d{2}-\d{2})", self.texto)
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


@registrar
class ValidadorAsopagosResumenTipo2(ValidadorBase):
    """Asopagos — Resumen tipo 2: Planilla GENERADA (pendiente de pago)."""

    OPERADOR = "ASOPAGOS"
    TIPO_DOC = "RESUMEN_TIPO2"

    _MARCADOR = "RESUMEN PLANILLA GENERADA"

    @classmethod
    def detectar(cls, texto: str) -> bool:
        return cls._MARCADOR in texto

    def validar_tipo_e(self) -> bool:
        return bool(re.search(r"TIPO\s+PLANILLA[\s\S]{0,150}\bE\b", self.texto))

    def validar_fecha_pago(self) -> bool:
        m = re.search(r"(\d{4}-\d{2}-\d{2})", self.texto)
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
