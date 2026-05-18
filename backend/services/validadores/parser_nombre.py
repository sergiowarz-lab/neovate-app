"""Parser del nombre de archivo PDF Neovate.

Formato esperado:
    {ID} - {NIT} - {OPERADOR} - {MES} - {AÑO} - {TIMESTAMP}.pdf
    {ID} - {NIT_EMPRESA} - {NIT_SUB} - {OPERADOR} - {MES} - {AÑO} - {TIMESTAMP}.pdf

Portado del sistema legacy (core/parser_nombre.py) sin cambios funcionales.
"""

import re
import unicodedata

MESES = {
    "ENERO": "01", "FEBRERO": "02", "MARZO": "03", "ABRIL": "04",
    "MAYO": "05", "JUNIO": "06", "JULIO": "07", "AGOSTO": "08",
    "SEPTIEMBRE": "09", "OCTUBRE": "10", "NOVIEMBRE": "11", "DICIEMBRE": "12",
}


def _normalizar_operador(texto: str) -> str:
    nfd = unicodedata.normalize("NFD", texto)
    sin_tildes = "".join(c for c in nfd if unicodedata.category(c) != "Mn").upper()
    sin_tildes = re.sub(r"\.\w{2,4}\b", "", sin_tildes)
    sin_tildes = sin_tildes.replace("_", " ")
    sin_tildes = re.sub(r"\s+", " ", sin_tildes).strip()
    return sin_tildes


def parsear_nombre(nombre_archivo: str) -> dict:
    nombre = nombre_archivo.replace(".pdf", "").replace(".PDF", "")
    partes = [p.strip() for p in nombre.split(" - ")]

    if len(partes) == 6:
        id_archivo, nit_validar, operador, mes_texto, anio, timestamp = partes
    elif len(partes) == 7:
        id_archivo, nit_empresa, nit_sub, operador, mes_texto, anio, timestamp = partes
        nit_validar = nit_sub if nit_sub else nit_empresa
    else:
        raise ValueError(
            f"El nombre del archivo no cumple la estructura esperada "
            f"({len(partes)} partes): {nombre_archivo}"
        )

    mes_num = MESES.get(mes_texto.upper())
    if not mes_num:
        raise ValueError(f"Mes inválido en el nombre: {mes_texto!r}")

    return {
        "id": id_archivo,
        "nit": nit_validar,
        "operador": _normalizar_operador(operador),
        "mes": mes_num,
        "anio": anio,
        "timestamp": timestamp,
    }
