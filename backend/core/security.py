from datetime import datetime, timedelta, timezone

import bcrypt
from jose import jwt

from backend.core.config import settings


_MAX_BCRYPT_BYTES = 72


def _encode_for_bcrypt(plain: str) -> bytes:
    """bcrypt sólo procesa hasta 72 bytes — truncamos para evitar ValueError."""
    return plain.encode("utf-8")[:_MAX_BCRYPT_BYTES]


def hash_password(plain: str) -> str:
    return bcrypt.hashpw(_encode_for_bcrypt(plain), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(_encode_for_bcrypt(plain), hashed.encode("utf-8"))
    except ValueError:
        return False


def create_access_token(subject: str, extra_claims: dict | None = None) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.JWT_EXPIRE_MINUTES)
    payload: dict = {"sub": subject, "exp": expire}
    if extra_claims:
        payload.update(extra_claims)
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


def decode_token(token: str) -> dict:
    return jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
