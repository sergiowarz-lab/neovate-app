import re

from backend.services.validadores.base import ValidadorBase
from backend.services.validadores.registry import registrar


@registrar
class ValidadorMiPlanillaResumenTipo1(ValidadorBase):
    """Mi Planilla (Compensar) — Resumen tipo 1: Planilla Integrada con TOTALES POR SUBSISTEMAS."""

    OPERADOR = "COMPENSAR MI PLANILLA"
    TIPO_DOC = "RESUMEN_TIPO1"

    _MARCADORES = [
        "PLANILLA INTEGRADA DE AUTOLIQUIDACION DE APORTES",
        "TOTALES POR SUBSISTEMAS",
    ]

    @classmethod
    def detectar(cls, texto: str) -> bool:
        return all(m in texto for m in cls._MARCADORES)

    def validar_estructura(self) -> bool:
        condiciones = [
            "PLANILLA INTEGRADA DE AUTOLIQUIDACION DE APORTES",
            "DATOS DEL APORTANTE",
            "DATOS DE LA PLANILLA",
            "TOTALES POR SUBSISTEMAS",
        ]
        return all(c in self.texto for c in condiciones)

    def validar_tipo_e(self) -> bool:
        return bool(re.search(r"\bE\b", self.texto))

    def validar_fecha_pago(self) -> bool:
        m = re.search(r"\bE\b[\s\S]{0,300}?(\d{2}/\d{2}/\d{4})", self.texto)
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
            errores.append("No corresponde a planilla PILA tipo 1 de MiPlanilla")
        if not self.validar_tipo_e():
            errores.append("No es planilla tipo E (Empresa)")
        return (False, errores) if errores else (True, [])


@registrar
class ValidadorMiPlanillaResumenTipo2(ValidadorBase):
    """Mi Planilla (Compensar) — Resumen tipo 2: Reporte de Planilla de Autoliquidación."""

    OPERADOR = "COMPENSAR MI PLANILLA"
    TIPO_DOC = "RESUMEN_TIPO2"

    _MARCADOR = "REPORTE DE LA PLANILLA DE AUTOLIQUIDACI"
    _EXCLUIR = "TOTALES POR SUBSISTEMAS"

    @classmethod
    def detectar(cls, texto: str) -> bool:
        return cls._MARCADOR in texto and cls._EXCLUIR not in texto

    def validar_tipo_e(self) -> bool:
        return bool(re.search(r"\bE\s+\d{2}\s+\d{2}\s+\d{4}", self.texto))

    def validar_fecha_pago(self) -> bool:
        m = re.search(r"\bE\s+(\d{2})\s+(\d{2})\s+(\d{4})", self.texto)
        if not m:
            return False
        self.fecha_pago = f"{m.group(1)}/{m.group(2)}/{m.group(3)}"
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
class ValidadorMiPlanillaIndividual(ValidadorBase):
    """Mi Planilla (Compensar) — Certificado Individual de Cotización."""

    OPERADOR = "COMPENSAR MI PLANILLA"
    TIPO_DOC = "INDIVIDUAL"

    _MARCADOR = "CERTIFICADO DE APORTES AL"

    @classmethod
    def detectar(cls, texto: str) -> bool:
        return cls._MARCADOR in texto

    def validar_fecha_pago(self) -> bool:
        m = re.search(r"\b(\d{2}/\d{2}/\d{4})\b", self.texto)
        if not m:
            return False
        self.fecha_pago = m.group(1)
        return True

    def validar_periodo_pension(self) -> bool:
        periodo = f"{self.metadata['anio']}-{self.metadata['mes']}"
        m = re.search(r"PENSIONES\s+(\d{4}-\d{2})", self.texto)
        if m and m.group(1) == periodo:
            return True
        if re.search(rf"PENSI.N[\s\S]{{0,200}}?{re.escape(periodo)}", self.texto):
            return True
        return False

    def validar(self) -> tuple[bool, list[str]]:
        errores = []
        if not self.validar_nit():
            errores.append("NIT no coincide con el del archivo")
        if not self.validar_periodo_pension():
            errores.append("Periodo de pensión no coincide")
        self.validar_fecha_pago()
        if "CERTIFICADO DE APORTES AL" not in self.texto:
            errores.append("No corresponde a Certificado Individual de MiPlanilla (Compensar)")
        return (False, errores) if errores else (True, [])
