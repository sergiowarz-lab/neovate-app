"""
Tests para las reglas de negocio de plazos de SS y Nómina.

Verifica que los cálculos de fechas límite sean correctos
según la tabla de NITs de la UGPP.

Para correr:
    pytest tests/test_cumplimiento.py -v
"""

from datetime import date
import pytest

from backend.services.cumplimiento import (
    nit9,
    parse_fecha,
    obtener_plazo_nomina,
    obtener_plazo_ss,
)


# ══════════════════════════════════════════════════════════════════════════════
# nit9 — extrae los primeros 9 dígitos
# ══════════════════════════════════════════════════════════════════════════════

class TestNit9:
    def test_nit_exacto_9_digitos(self):
        assert nit9("900434099") == "900434099"

    def test_nit_con_digito_verificacion(self):
        assert nit9("9004340997") == "900434009"

    def test_nit_con_guiones(self):
        assert nit9("900-434-099-7") == "900434099"

    def test_nit_con_puntos(self):
        assert nit9("900.434.099") == "900434099"

    def test_nit_corto_devuelve_lo_que_hay(self):
        assert nit9("12345") == "12345"


# ══════════════════════════════════════════════════════════════════════════════
# parse_fecha — convierte strings a date
# ══════════════════════════════════════════════════════════════════════════════

class TestParseFecha:
    def test_formato_iso(self):
        assert parse_fecha("2025-11-26") == date(2025, 11, 26)

    def test_formato_slash(self):
        assert parse_fecha("26/11/2025") == date(2025, 11, 26)

    def test_none_devuelve_none(self):
        assert parse_fecha(None) is None

    def test_texto_invalido_devuelve_none(self):
        assert parse_fecha("no-es-fecha") is None

    def test_date_pasa_directo(self):
        d = date(2025, 11, 26)
        assert parse_fecha(d) == d

    def test_datetime_convierte_a_date(self):
        from datetime import datetime
        dt = datetime(2025, 11, 26, 10, 30)
        assert parse_fecha(dt) == date(2025, 11, 26)


# ══════════════════════════════════════════════════════════════════════════════
# Plazo nómina — día 5 del mes siguiente
# ══════════════════════════════════════════════════════════════════════════════

class TestPlazoNomina:
    def test_mes_normal(self):
        assert obtener_plazo_nomina(2025, 10) == date(2025, 11, 5)

    def test_mes_diciembre_pasa_a_enero(self):
        assert obtener_plazo_nomina(2025, 12) == date(2026, 1, 5)

    def test_mes_enero(self):
        assert obtener_plazo_nomina(2025, 1) == date(2025, 2, 5)


# ══════════════════════════════════════════════════════════════════════════════
# Plazo SS — N-ésimo día hábil + 5 calendario
# ══════════════════════════════════════════════════════════════════════════════

class TestPlazoSS:
    def test_devuelve_fecha(self):
        resultado = obtener_plazo_ss("900434099", 2025, 10)
        assert resultado is not None
        assert isinstance(resultado, date)

    def test_plazo_es_posterior_al_periodo(self):
        resultado = obtener_plazo_ss("900434099", 2025, 10)
        assert resultado > date(2025, 10, 31)

    def test_nit_corto_devuelve_none(self):
        resultado = obtener_plazo_ss("1", 2025, 10)
        assert resultado is None

    def test_diciembre_calcula_para_enero(self):
        resultado = obtener_plazo_ss("900434099", 2025, 12)
        assert resultado is not None
        assert resultado.year == 2026
