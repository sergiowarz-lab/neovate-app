"""Extracción de texto completo de un PDF (en mayúsculas).

Usa pdfminer.six directamente (ya instalado como dependencia de pdfplumber)
en lugar de la API de alto nivel de pdfplumber, que es más lenta para PDFs
con tablas densas. Incluye timeout de 45 segundos y detección de casos
especiales: PDF escaneado, protegido con contraseña o corrupto.
"""

import logging
import threading
from pathlib import Path

log = logging.getLogger("neovate.extractor")

# Mínimo de caracteres para considerar que se extrajo texto real
_MIN_CHARS = 50


class PDFTimeoutError(Exception):
    """El PDF no pudo extraerse dentro del tiempo límite."""


class PDFEncryptedError(Exception):
    """El PDF está protegido con contraseña."""


class PDFEmptyError(Exception):
    """El PDF no contiene texto seleccionable (probable documento escaneado)."""


class PDFCorruptError(Exception):
    """El PDF está dañado o no es un archivo PDF válido."""


# Alias interno para compatibilidad con código anterior
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
    from pdfminer.pdfdocument import PDFPasswordIncorrect
    from pdfminer.pdfpage import PDFTextExtractionNotAllowed
    try:
        return extract_text(ruta).upper()
    except PDFPasswordIncorrect:
        raise PDFEncryptedError("El PDF está protegido con contraseña")
    except PDFTextExtractionNotAllowed:
        raise PDFEncryptedError("El PDF tiene restricciones de copiado de texto (DRM)")
    except Exception as exc:
        # Detectar PDFs corruptos por mensaje de la excepción
        msg = str(exc).lower()
        if any(k in msg for k in ("invalid pdf", "not a pdf", "startxref", "eof marker")):
            raise PDFCorruptError(f"Archivo PDF inválido o corrupto: {exc}")
        raise


def _extraer_con_pdfplumber(ruta: str) -> str:
    import pdfplumber
    texto = ""
    with pdfplumber.open(ruta) as pdf:
        for pagina in pdf.pages:
            texto += pagina.extract_text() or ""
    return texto.upper()


def extraer_texto_completo(ruta_pdf: str | Path, timeout: int = 45) -> str:
    """Extrae el texto de un PDF y lo devuelve en mayúsculas.

    Lanza:
        PDFEncryptedError — PDF con contraseña o DRM
        PDFEmptyError     — PDF escaneado sin texto seleccionable
        PDFCorruptError   — Archivo inválido o dañado
        PDFTimeoutError   — Ambos extractores superaron el timeout
    """
    ruta = str(ruta_pdf)
    nombre = Path(ruta).name

    # Errores que no tienen solución con un segundo extractor — fallan rápido
    errores_definitivos = (PDFEncryptedError, PDFCorruptError)

    # Intento 1: pdfminer (más rápido para texto nativo)
    try:
        texto = _con_timeout(lambda: _extraer_con_pdfminer(ruta), timeout)
        log.info("pdfminer extrajo %s (%d chars)", nombre, len(texto))
        if len(texto.strip()) < _MIN_CHARS:
            log.warning("pdfminer devolvió texto muy corto en %s — intentando pdfplumber", nombre)
            raise ValueError("texto vacío")
        return texto
    except errores_definitivos:
        raise  # no tiene sentido intentar pdfplumber
    except PDFTimeoutError:
        log.warning("pdfminer superó %ss en %s — intentando pdfplumber", timeout, nombre)
    except Exception as exc:
        log.warning("pdfminer falló en %s (%s) — intentando pdfplumber", nombre, exc)

    # Intento 2: pdfplumber como fallback
    try:
        texto = _con_timeout(lambda: _extraer_con_pdfplumber(ruta), timeout)
        log.info("pdfplumber extrajo %s (%d chars)", nombre, len(texto))
        if len(texto.strip()) < _MIN_CHARS:
            raise PDFEmptyError(
                "El PDF no contiene texto seleccionable. "
                "Si es un documento escaneado, no es compatible con el sistema."
            )
        return texto
    except PDFEmptyError:
        raise
    except PDFTimeoutError:
        log.error("pdfplumber también superó %ss en %s", timeout, nombre)
        raise
    except Exception as exc:
        log.error("pdfplumber también falló en %s: %s", nombre, exc)
        raise PDFCorruptError(f"No se pudo leer el archivo PDF: {exc}")
