"""Extracción de texto completo de un PDF (en mayúsculas)."""

from pathlib import Path

import pdfplumber


def extraer_texto_completo(ruta_pdf: str | Path) -> str:
    texto = ""
    with pdfplumber.open(str(ruta_pdf)) as pdf:
        for pagina in pdf.pages:
            texto += pagina.extract_text() or ""
    return texto.upper()
