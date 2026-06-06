"""Endpoints para suscripciones Web Push (VAPID)."""

import json

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from backend.api.deps import get_current_user
from backend.core.config import settings
from backend.core.database import get_db
from backend.models import PushSubscription, Usuario


router = APIRouter(prefix="/api/push", tags=["push"])


class SubscriptionPayload(BaseModel):
    subscription: dict


@router.get("/vapid-public-key")
def vapid_public_key() -> dict:
    """Devuelve la clave pública VAPID para que el frontend pueda suscribirse."""
    if not settings.VAPID_PUBLIC_KEY:
        raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE, "Push notifications no configuradas")
    return {"public_key": settings.VAPID_PUBLIC_KEY}


@router.post("/subscribe", status_code=status.HTTP_201_CREATED)
def suscribirse(
    payload: SubscriptionPayload,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    """Registra o actualiza la suscripción push del usuario actual."""
    sub_json = json.dumps(payload.subscription)

    # Evitar duplicados: si ya existe esta suscripción para el usuario, no hace nada
    existente = db.query(PushSubscription).filter(
        PushSubscription.username == current_user.username,
        PushSubscription.subscription_json == sub_json,
    ).first()

    if not existente:
        db.add(PushSubscription(
            username=current_user.username,
            subscription_json=sub_json,
        ))
        db.commit()

    return {"mensaje": "Suscripción registrada"}


@router.delete("/unsubscribe", status_code=status.HTTP_204_NO_CONTENT)
def desuscribirse(
    payload: SubscriptionPayload,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> None:
    """Elimina la suscripción push del usuario."""
    sub_json = json.dumps(payload.subscription)
    sub = db.query(PushSubscription).filter(
        PushSubscription.username == current_user.username,
        PushSubscription.subscription_json == sub_json,
    ).first()
    if sub:
        db.delete(sub)
        db.commit()
