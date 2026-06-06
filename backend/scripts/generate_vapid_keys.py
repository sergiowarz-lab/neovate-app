"""Genera claves VAPID para push notifications.

Uso:
    cd backend
    .venv\\Scripts\\python.exe -m backend.scripts.generate_vapid_keys

Copia las claves al archivo backend/.env:
    VAPID_PRIVATE_KEY=...
    VAPID_PUBLIC_KEY=...
"""

from py_vapid import Vapid

vapid = Vapid()
vapid.generate_keys()

print("=== Claves VAPID generadas ===")
print(f"VAPID_PRIVATE_KEY={vapid.private_key.private_bytes_raw().hex()}")
print(f"VAPID_PUBLIC_KEY={vapid.public_key.public_bytes_raw().hex()}")
print()
print("Copia estas líneas en backend/.env")
