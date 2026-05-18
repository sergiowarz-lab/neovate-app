"""Registry de validadores Neovate. Portado del sistema legacy."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from backend.services.validadores.base import ValidadorBase


_REGISTRY: dict[str, list[type]] = {}


def registrar(cls):
    if not cls.OPERADOR:
        raise ValueError(f"{cls.__name__} debe definir el atributo OPERADOR")
    clave = cls.OPERADOR.upper()
    _REGISTRY.setdefault(clave, []).append(cls)
    return cls


def obtener_validador(operador: str, texto: str, metadata: dict) -> "ValidadorBase | None":
    candidatos = _REGISTRY.get(operador.upper(), [])
    for cls in candidatos:
        if cls.detectar(texto):
            return cls(metadata, texto)
    return None


def obtener_hoja_destino(operador: str) -> str:
    """Devuelve 'SS' o 'Nomina' según el operador (la primera clase registrada manda)."""
    candidatos = _REGISTRY.get(operador.upper(), [])
    if candidatos:
        return candidatos[0].HOJA_EXCEL
    return "SS"


def listar_operadores() -> list[str]:
    return sorted(_REGISTRY.keys())
