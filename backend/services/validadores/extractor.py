"""Extracción de texto completo de un PDF (en mayúsculas).

Usa pdfminer.six directamente (ya instalado como dependencia de pdfplumber)
en lugar de la API de alto nivel de pdfplumber, que es más lenta para PDFs
con tablas densas. Incluye timeout de 45 segundos para evitar cuelgues.
"""

import logging
import threading
from pathlib import Path

log = logging.getLogger("neovate.extractor")


class PDFTimeoutError(Exception):
    """El PDF no pudo extraerse dentro del tiempo límite."""


# Alias interno para compatibilidad
_TimeoutError = PDFTimeoutError


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
        raise PDFTimeoutError(
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
    nombre = Path(ruta).name

    # Intento 1: pdfminer (más rápido para texto nativo)
    try:
        texto = _con_timeout(lambda: _extraer_con_pdfminer(ruta), timeout)
        log.info("pdfminer extrajo %s (%d chars)", nombre, len(texto))
        return texto
    except PDFTimeoutError:
        log.warning("pdfminer superó %ss en %s — intentando pdfplumber", timeout, nombre)
    except Exception as exc:
        log.warning("pdfminer falló en %s (%s) — intentando pdfplumber", nombre, exc)

    # Intento 2: pdfplumber como fallback
    try:
        texto = _con_timeout(lambda: _extraer_con_pdfplumber(ruta), timeout)
        log.info("pdfplumber extrajo %s (%d chars)", nombre, len(texto))
        return texto
    except PDFTimeoutError:
        log.error("pdfplumber también superó %ss en %s — archivo no procesable", timeout, nombre)
        raise
    except Exception as exc:
        log.error("pdfplumber también falló en %s: %s", nombre, exc)
        raise
