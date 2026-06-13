"""Servicio de Web Push con VAPID para notificaciones de mora."""

from __future__ import annotations

import json
import logging
import time

from backend.core.config import settings
from backend.core.database import SessionLocal
from backend.models import PushSubscription, RolUsuario, Usuario

log = logging.getLogger("neovate.push")


def _get_webpush():
    try:
        from pywebpush import webpush, WebPushException
        return webpush, WebPushException
    except ImportError:
        log.warning("pywebpush no instalado — push deshabilitado")
        return None, None


def enviar_push(subscription_json: str, titulo: str, cuerpo: str, tag: str = "mora") -> bool:
    """Envía una notificación push a una suscripción."""
    webpush, WebPushException = _get_webpush()
    if webpush is None:
        return False

    if not settings.VAPID_PRIVATE_KEY or not settings.VAPID_PUBLIC_KEY:
        log.warning("VAPID keys no configuradas — push deshabilitado")
        return False

    try:
        sub = json.loads(subscription_json)
        webpush(
            subscription_info=sub,
            data=json.dumps({"title": titulo, "body": cuerpo, "tag": tag}),
            vapid_private_key=settings.VAPID_PRIVATE_KEY,
            vapid_claims={
                "sub": settings.VAPID_CLAIMS_SUB or "mailto:admin@neovate.co",
                "exp": int(time.time()) + 43200,
            },
        )
        return True
    except WebPushException as exc:
        log.warning("Push fallido: %s", exc)
        if exc.response and exc.response.status_code in (404, 410):
            # Suscripción expirada o inválida — limpiar
            _eliminar_suscripcion(subscription_json)
        return False
    except Exception:
        log.exception("Error inesperado en push")
        return False


def notificar_mora(nit9: str, nombre_empresa: str) -> int:
    """Notifica a todos los analistas y admins activos sobre una empresa en mora."""
    with SessionLocal() as db:
        usuarios = db.query(Usuario).filter(
            Usuario.activo.is_(True),
            Usuario.rol.in_([RolUsuario.ADMIN, RolUsuario.ANALISTA]),
        ).all()

        enviados = 0
        for user in usuarios:
            for sub in user.push_subscriptions:
                ok = enviar_push(
                    sub.subscription_json,
                    titulo="⚠️ Empresa en mora — Neovate",
                    cuerpo=f"{nombre_empresa} está en mora de Seguridad Social.",
                    tag=f"mora-{nit9}",
                )
                if ok:
                    enviados += 1
        return enviados


def notificar_planilla_subida(
    nit: str,
    nombre_empresa: str,
    operador: str,
    mes: str,
    anio: str,
    estado: str,
) -> int:
    """Notifica a todos los admins cuando se sube y procesa una planilla."""
    icono = "✅" if estado == "Validado_ok" else "❌"
    titulo = f"{icono} Planilla {estado.replace('_', ' ')} — Neovate"
    cuerpo = (
        f"{nombre_empresa} ({nit})\n"
        f"Operador: {operador} · Período: {mes}/{anio}"
    )
    tag = f"planilla-{nit}-{anio}-{mes}"

    with SessionLocal() as db:
        admins = db.query(Usuario).filter(
            Usuario.activo.is_(True),
            Usuario.rol == RolUsuario.ADMIN,
        ).all()

        enviados = 0
        for user in admins:
            for sub in user.push_subscriptions:
                if enviar_push(sub.subscription_json, titulo, cuerpo, tag):
                    enviados += 1
    return enviados


def _eliminar_suscripcion(subscription_json: str) -> None:
    with SessionLocal() as db:
        sub = db.query(PushSubscription).filter(
            PushSubscription.subscription_json == subscription_json
        ).first()
        if sub:
            db.delete(sub)
            db.commit()
