"""Validadores de planillas Neovate.

Importar este paquete garantiza el registro de todos los validadores en el registry.
El orden de imports define la prioridad de detección.
"""

from backend.services.validadores import aportes_en_linea  # noqa: F401
from backend.services.validadores import compensar_miplanilla  # noqa: F401
from backend.services.validadores import asopagos  # noqa: F401
from backend.services.validadores import enlace  # noqa: F401
from backend.services.validadores import simple_planilla  # noqa: F401
from backend.services.validadores import soi  # noqa: F401
from backend.services.validadores import nomina  # noqa: F401
