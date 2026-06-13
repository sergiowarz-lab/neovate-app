"""
Tests para los validadores de planillas de Seguridad Social.

Cada test verifica una regla de negocio concreta:
  - detección correcta del tipo de documento
  - validación de NIT
  - validación de período
  - validación de tipo de planilla
  - resultado completo de validar()

Para correr:
    pytest tests/test_validadores.py -v
"""

import pytest

# Importar registra todos los validadores en el registry
from backend.services.validadores import (  # noqa: F401
    asopagos, aportes_en_linea, nomina,
)
from backend.services.validadores.asopagos import (
    ValidadorAsopagosResumenTipo1,
    ValidadorAsopagosResumenTipo2,
)
from backend.services.validadores.registry import (
    obtener_validador,
    listar_operadores,
    obtener_hoja_destino,
)
from backend.services.validadores.parser_nombre import parsear_nombre
from tests.conftest import (
    TEXTO_ASOPAGOS_PAGADA,
    TEXTO_ASOPAGOS_GENERADA,
    TEXTO_ASOPAGOS_TIPO_A,
    TEXTO_APORTES_RESUMEN,
    TEXTO_NOMINA,
)


# ══════════════════════════════════════════════════════════════════════════════
# Registry
# ══════════════════════════════════════════════════════════════════════════════

class TestRegistry:
    def test_operadores_registrados(self):
        ops = listar_operadores()
        assert "ASOPAGOS" in ops

    def test_hoja_asopagos_es_ss(self):
        assert obtener_hoja_destino("ASOPAGOS") == "SS"

    def test_hoja_nomina_es_nomina(self):
        assert obtener_hoja_destino("NOMINA") == "Nomina"

    def test_operador_desconocido_devuelve_ss(self):
        assert obtener_hoja_destino("OPERADOR_INEXISTENTE") == "SS"

    def test_obtener_validador_asopagos_pagada(self, meta_nov2025):
        v = obtener_validador("ASOPAGOS", TEXTO_ASOPAGOS_PAGADA, meta_nov2025)
        assert v is not None
        assert isinstance(v, ValidadorAsopagosResumenTipo1)

    def test_obtener_validador_asopagos_generada(self, meta_nov2025):
        v = obtener_validador("ASOPAGOS", TEXTO_ASOPAGOS_GENERADA, meta_nov2025)
        assert v is not None
        assert isinstance(v, ValidadorAsopagosResumenTipo2)

    def test_obtener_validador_operador_incorrecto_devuelve_none(self, meta_nov2025):
        v = obtener_validador("OPERADOR_X", TEXTO_ASOPAGOS_PAGADA, meta_nov2025)
        assert v is None


# ══════════════════════════════════════════════════════════════════════════════
# Asopagos — Resumen Tipo 1 (Planilla PAGADA)
# ══════════════════════════════════════════════════════════════════════════════

class TestAsopagosResumenTipo1:

    # Detección
    def test_detectar_texto_valido(self):
        assert ValidadorAsopagosResumenTipo1.detectar(TEXTO_ASOPAGOS_PAGADA) is True

    def test_detectar_texto_generada_falla(self):
        assert ValidadorAsopagosResumenTipo1.detectar(TEXTO_ASOPAGOS_GENERADA) is False

    def test_detectar_texto_vacio_falla(self):
        assert ValidadorAsopagosResumenTipo1.detectar("") is False

    # NIT
    def test_nit_correcto(self, meta_nov2025):
        v = ValidadorAsopagosResumenTipo1(meta_nov2025, TEXTO_ASOPAGOS_PAGADA)
        assert v.validar_nit() is True

    def test_nit_incorrecto(self, meta_nit_distinto):
        v = ValidadorAsopagosResumenTipo1(meta_nit_distinto, TEXTO_ASOPAGOS_PAGADA)
        assert v.validar_nit() is False

    # Período
    def test_periodo_correcto(self, meta_nov2025):
        v = ValidadorAsopagosResumenTipo1(meta_nov2025, TEXTO_ASOPAGOS_PAGADA)
        assert v.validar_periodo_universal() is True

    def test_periodo_incorrecto(self, meta_oct2025):
        texto_sin_oct = TEXTO_ASOPAGOS_PAGADA.replace("2025-10", "2025-09")
        v = ValidadorAsopagosResumenTipo1(meta_oct2025, texto_sin_oct)
        assert v.validar_periodo_universal() is False

    # Tipo E
    def test_tipo_e_correcto(self, meta_nov2025):
        v = ValidadorAsopagosResumenTipo1(meta_nov2025, TEXTO_ASOPAGOS_PAGADA)
        assert v.validar_tipo_e() is True

    def test_tipo_e_incorrecto(self, meta_nov2025):
        v = ValidadorAsopagosResumenTipo1(meta_nov2025, TEXTO_ASOPAGOS_TIPO_A)
        assert v.validar_tipo_e() is False

    # Fecha de pago
    def test_fecha_pago_extraida(self, meta_nov2025):
        v = ValidadorAsopagosResumenTipo1(meta_nov2025, TEXTO_ASOPAGOS_PAGADA)
        v.validar_fecha_pago()
        assert v.fecha_pago == "2025-11-26"

    def test_fecha_pago_ausente(self, meta_nov2025):
        texto_sin_fecha = "RESUMEN PLANILLA PAGADA\nNI 900434099\nPERIODO SALUD 2025-11\nTIPO PLANILLA E"
        v = ValidadorAsopagosResumenTipo1(meta_nov2025, texto_sin_fecha.upper())
        resultado = v.validar_fecha_pago()
        assert resultado is False

    # Validar completo
    def test_validar_documento_correcto(self, meta_nov2025):
        v = ValidadorAsopagosResumenTipo1(meta_nov2025, TEXTO_ASOPAGOS_PAGADA)
        ok, errores = v.validar()
        assert ok is True
        assert errores == []

    def test_validar_nit_falla(self, meta_nit_distinto):
        meta_nit_distinto["operador"] = "ASOPAGOS"
        v = ValidadorAsopagosResumenTipo1(meta_nit_distinto, TEXTO_ASOPAGOS_PAGADA)
        ok, errores = v.validar()
        assert ok is False
        assert any("NIT" in e for e in errores)

    def test_validar_tipo_incorrecto_falla(self, meta_nov2025):
        v = ValidadorAsopagosResumenTipo1(meta_nov2025, TEXTO_ASOPAGOS_TIPO_A)
        ok, errores = v.validar()
        assert ok is False
        assert any("tipo E" in e.lower() or "tipo" in e.lower() for e in errores)

    def test_validar_devuelve_multiples_errores(self, meta_nit_distinto):
        """Cuando NIT y período fallan, se reportan ambos errores."""
        texto_mal = "RESUMEN PLANILLA PAGADA\nNI 999999999\nPERIODO SALUD 2024-01\nTIPO PLANILLA A"
        v = ValidadorAsopagosResumenTipo1(meta_nit_distinto, texto_mal.upper())
        ok, errores = v.validar()
        assert ok is False
        assert len(errores) >= 2


# ══════════════════════════════════════════════════════════════════════════════
# Asopagos — Resumen Tipo 2 (Planilla GENERADA)
# ══════════════════════════════════════════════════════════════════════════════

class TestAsopagosResumenTipo2:

    def test_detectar_texto_valido(self):
        assert ValidadorAsopagosResumenTipo2.detectar(TEXTO_ASOPAGOS_GENERADA) is True

    def test_detectar_texto_pagada_falla(self):
        assert ValidadorAsopagosResumenTipo2.detectar(TEXTO_ASOPAGOS_PAGADA) is False

    def test_validar_documento_correcto(self, meta_nov2025):
        v = ValidadorAsopagosResumenTipo2(meta_nov2025, TEXTO_ASOPAGOS_GENERADA)
        ok, errores = v.validar()
        assert ok is True
        assert errores == []


# ══════════════════════════════════════════════════════════════════════════════
# Parser de nombres de archivo
# ══════════════════════════════════════════════════════════════════════════════

class TestParserNombre:

    def test_nombre_estandar_6_partes(self):
        nombre = "ABC12345 - 900434099 - ASOPAGOS - NOVIEMBRE - 2025 - 20261106120000.pdf"
        meta = parsear_nombre(nombre)
        assert meta["id"] == "ABC12345"
        assert meta["nit"] == "900434099"
        assert meta["operador"] == "ASOPAGOS"
        assert meta["mes"] == "11"
        assert meta["anio"] == "2025"

    def test_nombre_con_nit_sub_7_partes(self):
        nombre = "XYZ99999 - 900434099 - 123456789 - ENLACE - MARZO - 2025 - 20260306120000.pdf"
        meta = parsear_nombre(nombre)
        assert meta["nit"] == "123456789"
        assert meta["mes"] == "03"

    def test_mes_invalido_lanza_error(self):
        nombre = "ABC12345 - 900434099 - ASOPAGOS - MESRARO - 2025 - 20261106120000.pdf"
        with pytest.raises(ValueError, match="Mes inválido"):
            parsear_nombre(nombre)

    def test_pocas_partes_lanza_error(self):
        nombre = "ABC12345 - ASOPAGOS.pdf"
        with pytest.raises(ValueError):
            parsear_nombre(nombre)

    def test_mayusculas_y_minusculas(self):
        nombre = "ABC12345 - 900434099 - asopagos - noviembre - 2025 - 20261106120000.pdf"
        meta = parsear_nombre(nombre)
        assert meta["operador"] == "ASOPAGOS"
        assert meta["mes"] == "11"

    def test_todos_los_meses(self):
        meses = [
            ("ENERO", "01"), ("FEBRERO", "02"), ("MARZO", "03"), ("ABRIL", "04"),
            ("MAYO", "05"), ("JUNIO", "06"), ("JULIO", "07"), ("AGOSTO", "08"),
            ("SEPTIEMBRE", "09"), ("OCTUBRE", "10"), ("NOVIEMBRE", "11"), ("DICIEMBRE", "12"),
        ]
        for nombre_mes, num in meses:
            nombre = f"ID1 - 900000000 - ASOPAGOS - {nombre_mes} - 2025 - 20250101000000.pdf"
            assert parsear_nombre(nombre)["mes"] == num
