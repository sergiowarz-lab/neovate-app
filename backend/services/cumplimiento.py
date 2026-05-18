"""Cálculo de plazos de Seguridad Social y Nómina del Sistema Neovate.

Portado del sistema legacy (cumplimiento/plazo_ss.py).

Reglas:
  - SS:     N-ésimo día hábil del mes siguiente + 5 días calendario (N según últimos
            2 dígitos de los primeros 9 dígitos del NIT).
  - Nómina: día 5 calendario del mes siguiente (igual para todas las empresas).
"""

from __future__ import annotations

from datetime import date, datetime, timedelta

try:
    import holidays as _holidays_lib  # type: ignore
    _HOLIDAYS_OK = True
except ImportError:
    _HOLIDAYS_OK = False


SS_RANGOS: list[tuple[tuple[int, int], int]] = [
    ((0, 7), 2), ((8, 14), 3), ((15, 21), 4), ((22, 28), 5),
    ((29, 35), 6), ((36, 42), 7), ((43, 49), 8), ((50, 56), 9),
    ((57, 63), 10), ((64, 69), 11), ((70, 75), 12), ((76, 81), 13),
    ((82, 87), 14), ((88, 93), 15), ((94, 99), 16),
]

_cache_feriados: dict[int, set] = {}


def nit9(nit) -> str:
    digits = "".join(c for c in str(nit) if c.isdigit())
    return digits[:9]


def _feriados(year: int) -> set:
    if year not in _cache_feriados:
        if _HOLIDAYS_OK:
            _cache_feriados[year] = set(
                _holidays_lib.country_holidays("CO", years=[year, year + 1])
            )
        else:
            _cache_feriados[year] = set()
    return _cache_feriados[year]


def _n_dia_habil(year: int, month: int, n: int, feriados: set) -> date:
    d = date(year, month, 1)
    cnt = 0
    while d.month == month:
        if d.weekday() < 5 and d not in feriados:
            cnt += 1
            if cnt == n:
                return d
        d += timedelta(days=1)
    raise ValueError(f"No hay {n} dias habiles en {year}-{month:02d}")


def obtener_plazo_nomina(year: int, month: int) -> date:
    """Día 5 calendario del mes siguiente al período."""
    if month == 12:
        return date(year + 1, 1, 5)
    return date(year, month + 1, 5)


def obtener_plazo_ss(nit, year: int, month: int) -> date | None:
    base9 = nit9(nit)
    if len(base9) < 2:
        return None

    ult2 = int(base9[-2:])
    next_month = month + 1 if month < 12 else 1
    next_year = year if month < 12 else year + 1
    fer = _feriados(year)

    for (lo, hi), n in SS_RANGOS:
        if lo <= ult2 <= hi:
            try:
                asignada = _n_dia_habil(next_year, next_month, n, fer)
                return asignada + timedelta(days=5)
            except ValueError:
                return None
    return None


def parse_fecha(v) -> date | None:
    """Convierte string/date/datetime a date. None si falla."""
    if v is None:
        return None
    if isinstance(v, datetime):
        return v.date()
    if isinstance(v, date):
        return v
    s = str(v).strip()
    for fmt in ("%d/%m/%Y", "%Y-%m-%d", "%Y/%m/%d", "%d-%m-%Y"):
        try:
            return datetime.strptime(s, fmt).date()
        except ValueError:
            pass
    return None
