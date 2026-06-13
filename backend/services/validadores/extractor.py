"""Extracción de texto completo de un PDF (en mayúsculas).

Usa pdfminer.six directamente (ya instalado como dependencia de pdfplumber)
en lugar de la API de alto nivel de pdfplumber, que es más lenta para PDFs
con tablas densas. Incluye timeout de 45 segundos para evitar cuelgues.
"""

import threading
from pathlib import Path


class _TimeoutError(Exception):
    pass


def _con_timeout(fn, timeout: int = 45):
    resultado: dict = {"valor": None, "error": None}

    def _run():
        try:
            resultado["valor"] = fn()
        except Exception as exc:
            resultado["error"] = exc

    hilo = threading.Thread(target=_run, daemon=True)
    hilo.start()
    hilo.join(timeout=timeout)

    if hilo.is_alive():
        raise _TimeoutError(
            f"Extracción del PDF superó {timeout}s — "
            "el archivo puede ser demasiado complejo o estar dañado"
        )
    if resultado["error"]:
        raise resultado["error"]
    return resultado["valor"]


def _extraer_con_pdfminer(ruta: str) -> str:
    from pdfminer.high_level import extract_text
    return extract_text(ruta).upper()


def _extraer_con_pdfplumber(ruta: str) -> str:
    import pdfplumber
    texto = ""
    with pdfplumber.open(ruta) as pdf:
        for pagina in pdf.pages:
            texto += pagina.extract_text() or ""
    return texto.upper()


def extraer_texto_completo(ruta_pdf: str | Path, timeout: int = 45) -> str:
    ruta = str(ruta_pdf)
    try:
        return _con_timeout(lambda: _extraer_con_pdfminer(ruta), timeout)
    except _TimeoutError:
        raise
    except Exception:
        return _con_timeout(lambda: _extraer_con_pdfplumber(ruta), timeout)
