"""Fixtures compartidos para todos los tests de Neovate."""

import pytest


# ─── Textos de muestra para validadores ────────────────────────────────────────

TEXTO_ASOPAGOS_PAGADA = """
RESUMEN PLANILLA PAGADA
IDENTIFICACION NI 900434099
DALMARU INVERSIONES SAS
PERIODO PENSION 2025-10
PERIODO SALUD  2025-11
TIPO PLANILLA E
FECHA PAGO 2025-11-26
ENTIDAD RECAUDO BANCOLOMBIA
ESTADO PLANILLA Pagada
""".upper()

TEXTO_ASOPAGOS_GENERADA = """
RESUMEN PLANILLA GENERADA
IDENTIFICACION NI 900434099
DALMARU INVERSIONES SAS
PERIODO PENSION 2025-10
PERIODO SALUD  2025-11
TIPO PLANILLA E
FECHA LIMITE PAGO 2025-11-26
""".upper()

TEXTO_ASOPAGOS_TIPO_A = """
RESUMEN PLANILLA PAGADA
IDENTIFICACION NI 900434099
PERIODO SALUD 2025-11
TIPO PLANILLA A
""".upper()

TEXTO_APORTES_RESUMEN = """
COMPROBANTE DE PAGO APORTES EN LINEA
NIT APORTANTE 900434099
PERIODO COTIZACION 2025-11
VALOR TOTAL PAGADO
FECHA DE PAGO 26/11/2025
""".upper()

TEXTO_NOMINA = """
FORMATO PARA REPORTE DE NOMINA
EMPRESA NIT 900434099
PERIODO NOVIEMBRE 2025
TOTAL TRABAJADORES
""".upper()


# ─── Metadata base ──────────────────────────────────────────────────────────────

@pytest.fixture
def meta_nov2025():
    """Metadata típica: NIT 900434099, Noviembre 2025."""
    return {
        "id": "TESTID01",
        "nit": "900434099",
        "operador": "ASOPAGOS",
        "mes": "11",
        "anio": "2025",
        "timestamp": "20261106120000",
    }


@pytest.fixture
def meta_oct2025():
    """Metadata con Octubre 2025 — período que NO coincide con Noviembre."""
    return {
        "id": "TESTID02",
        "nit": "900434099",
        "operador": "ASOPAGOS",
        "mes": "10",
        "anio": "2025",
        "timestamp": "20261006120000",
    }


@pytest.fixture
def meta_nit_distinto():
    """Metadata con NIT diferente al del PDF."""
    return {
        "id": "TESTID03",
        "nit": "111222333",
        "operador": "ASOPAGOS",
        "mes": "11",
        "anio": "2025",
        "timestamp": "20261106120000",
    }
