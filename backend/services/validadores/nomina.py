"""Validador de Nómina interna del Sistema Neovate.

Rebranding: la cadena 'de Claro' en el mensaje de error fue reemplazada por 'de Neovate'.
Los marcadores de detección (_MARCADOR) NO se tocan — son patrones del PDF real.
"""

import re

from backend.services.validadores.base import ValidadorBase
from backend.services.validadores.registry import registrar


@registrar
class ValidadorNomina(ValidadorBase):
    """Nómina — Formato para Reporte de Nómina (plantilla interna)."""

    OPERADOR = "NOMINA"
    TIPO_DOC = "UNICO"
    HOJA_EXCEL = "Nomina"

    _MARCADOR = "FORMATO PARA REPORTE DE N"
    _MARCADOR_PROC = "REPORTE DE PAGOS LABORALES EMPRESAS ALIADAS"

    @classmethod
    def detectar(cls, texto: str) -> bool:
        return cls._MARCADOR in texto

    def validar_nit(self) -> bool:
        """El PDF puede renderizar el NIT con espacios entre dígitos."""
        nit = self.metadata["nit"]
        pattern = r"\s?".join(re.escape(c) for c in nit)
        return bool(re.search(pattern, self.texto))

    def validar_estructura(self) -> bool:
        return self._MARCADOR in self.texto and self._MARCADOR_PROC in self.texto

    def validar_periodo(self) -> bool:
        from backend.services.validadores.base import MESES_ES

        anio = self.metadata["anio"]
        mes = self.metadata["mes"]
        mes_nombre = MESES_ES.get(mes, "")

        m_mes = re.search(r"MES DEL REPORTE\s+(\w+)", self.texto)
        m_anio = re.search(r"A.O DEL REPORTE\s+(\d{4})", self.texto)

        if m_mes and m_anio:
            return m_mes.group(1).upper() == mes_nombre and m_anio.group(1) == anio
        return False

    def validar(self) -> tuple[bool, list[str]]:
        errores = []
        if not self.validar_nit():
            errores.append("NIT no coincide con el del archivo")
        if not self.validar_periodo():
            errores.append("Mes/año del reporte no coincide con el nombre del archivo")
        if not self.validar_estructura():
            errores.append("No corresponde al Formato para Reporte de Nómina de Neovate")
        return (False, errores) if errores else (True, [])
