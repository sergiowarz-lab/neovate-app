import re

from backend.services.validadores.base import ValidadorBase
from backend.services.validadores.registry import registrar


@registrar
class ValidadorAportesResumen(ValidadorBase):
    """Aportes en Línea — Planilla Resumen (PILA consolidada tipo E)."""

    OPERADOR = "APORTES EN LINEA"
    TIPO_DOC = "RESUMEN"

    _MARCADORES = [
        "PLANILLA RESUMEN",
        "DATOS GENERALES DEL APORTANTE",
        "LIQUIDACION DETALLADA DE APORTES",
    ]

    @classmethod
    def detectar(cls, texto: str) -> bool:
        return all(m in texto for m in cls._MARCADORES)

    def validar_estructura(self) -> bool:
        return all(m in self.texto for m in self._MARCADORES)

    def validar_tipo_e(self) -> bool:
        return bool(re.search(r"\bE\s+\d{4}/\d{2}/\d{2}", self.texto))

    def validar_fecha_pago(self) -> bool:
        m = re.search(r"\bE\s+(\d{4}/\d{2}/\d{2})", self.texto)
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
        if not self.validar_estructura():
            errores.append("No corresponde a Planilla Resumen de Aportes en Línea")
        if not self.validar_tipo_e():
            errores.append("No es planilla Tipo E (Empresa)")
        return (False, errores) if errores else (True, [])


@registrar
class ValidadorAportesIndividual(ValidadorBase):
    """Aportes en Línea — Certificado Individual de Aportes."""

    OPERADOR = "APORTES EN LINEA"
    TIPO_DOC = "INDIVIDUAL"

    _MARCADORES = ["CERTIFICADO DE APORTES"]
    _EXCLUIR = "CERTIFICADO DE APORTES AL"  # excluye el certificado de Mi Planilla

    @classmethod
    def detectar(cls, texto: str) -> bool:
        return cls._MARCADORES[0] in texto and cls._EXCLUIR not in texto

    def validar_fecha_pago(self) -> bool:
        m = re.search(r"\bE\s+(\d{4}-\d{2}-\d{2})", self.texto)
        if not m:
            return False
        self.fecha_pago = m.group(1)
        return True

    def validar_periodo_pension(self) -> bool:
        periodo = f"{self.metadata['anio']}-{self.metadata['mes']}"

        m_afp = re.search(r"\b(2[23]\d{4}|25-14)\b[\s\S]{0,80}?(\d{4}-\d{2})", self.texto)
        if m_afp and m_afp.group(2) == periodo:
            return True
        m_arl = re.search(r"\bARL\b[\s\S]{0,100}?(\d{4}-\d{2})", self.texto)
        if m_arl and m_arl.group(1) == periodo:
            return True
        m_ccf = re.search(r"\bCCF[\s\S]{0,100}?(\d{4}-\d{2})", self.texto)
        if m_ccf and m_ccf.group(1) == periodo:
            return True
        return False

    def validar(self) -> tuple[bool, list[str]]:
        errores = []
        if not self.validar_nit():
            errores.append("NIT no coincide con el del archivo")
        if not self.validar_periodo_pension():
            errores.append("Periodo de pensión no coincide (se valida contra ARL/AFP, no EPS)")
        self.validar_fecha_pago()
        if "CERTIFICADO DE APORTES" not in self.texto:
            errores.append("No corresponde a Certificado Individual de Aportes en Línea")
        return (False, errores) if errores else (True, [])
