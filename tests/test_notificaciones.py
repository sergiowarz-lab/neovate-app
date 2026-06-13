"""
Tests del sistema de notificaciones push Web Push (VAPID).

Cubre:
  - Endpoints de la API (/api/push/...)
  - push_service: enviar_push, notificar_mora
  - mora_checker: verificar_mora_empresa, verificar_todas_las_moras

Para correr:
    pytest tests/test_notificaciones.py -v
"""

import json
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.main import app
from backend.core.database import get_db
from backend.models import (
    Base, EstadoReporte, EstadoSeguimiento, EmpresaAliada,
    PushSubscription, RolUsuario, SeguimientoMensual, Usuario,
)
from backend.core.security import get_password_hash


# ─── DB en memoria ─────────────────────────────────────────────────────────────

SQLALCHEMY_TEST_URL = "sqlite:///./test_push.db"
engine_test = create_engine(SQLALCHEMY_TEST_URL, connect_args={"check_same_thread": False})
TestingSession = sessionmaker(bind=engine_test)


def override_get_db():
    db = TestingSession()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

SUSCRIPCION_EJEMPLO = {
    "endpoint": "https://fcm.googleapis.com/fcm/send/test-endpoint-123",
    "keys": {"p256dh": "clave-p256dh-ejemplo", "auth": "clave-auth-ejemplo"},
}


@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine_test)
    db = TestingSession()

    # Usuario admin con suscripción
    admin = Usuario(
        username="admin",
        email="admin@test.com",
        hashed_password=get_password_hash("admin123"),
        rol=RolUsuario.ADMIN,
        activo=True,
    )
    # Usuario empresa sin permisos de notificación (rol no recibe)
    empresa_user = Usuario(
        username="empresa1",
        email="empresa@test.com",
        hashed_password=get_password_hash("empresa123"),
        rol=RolUsuario.EMPRESA,
        activo=True,
        nit_empresa="900434099",
    )
    db.add_all([admin, empresa_user])
    db.flush()

    sub = PushSubscription(
        username="admin",
        subscription_json=json.dumps(SUSCRIPCION_EJEMPLO),
    )
    db.add(sub)

    empresa = EmpresaAliada(
        nit="9004340997",
        nit9="900434099",
        nombre_empresa="DALMARU INVERSIONES SAS",
        activa=True,
    )
    db.add(empresa)
    db.commit()
    db.close()
    yield
    Base.metadata.drop_all(bind=engine_test)


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def token_admin(client):
    resp = client.post("/api/auth/token", data={"username": "admin", "password": "admin123"})
    return resp.json()["access_token"]


@pytest.fixture
def auth_admin(token_admin):
    return {"Authorization": f"Bearer {token_admin}"}


@pytest.fixture
def token_empresa(client):
    resp = client.post("/api/auth/token", data={"username": "empresa1", "password": "empresa123"})
    return resp.json()["access_token"]


@pytest.fixture
def auth_empresa(token_empresa):
    return {"Authorization": f"Bearer {token_empresa}"}


# ══════════════════════════════════════════════════════════════════════════════
# GET /api/push/vapid-public-key
# ══════════════════════════════════════════════════════════════════════════════

class TestVapidPublicKey:
    def test_devuelve_clave_cuando_configurada(self, client, auth_admin):
        with patch("backend.api.push.settings") as mock_settings:
            mock_settings.VAPID_PUBLIC_KEY = "clave-publica-vapid-test"
            resp = client.get("/api/push/vapid-public-key", headers=auth_admin)
        assert resp.status_code == 200
        assert "public_key" in resp.json()

    def test_503_cuando_no_hay_clave(self, client, auth_admin):
        with patch("backend.api.push.settings") as mock_settings:
            mock_settings.VAPID_PUBLIC_KEY = ""
            resp = client.get("/api/push/vapid-public-key", headers=auth_admin)
        assert resp.status_code == 503

    def test_sin_auth_devuelve_401(self, client):
        resp = client.get("/api/push/vapid-public-key")
        assert resp.status_code == 401


# ══════════════════════════════════════════════════════════════════════════════
# POST /api/push/subscribe
# ══════════════════════════════════════════════════════════════════════════════

class TestSuscribirse:
    def test_suscripcion_nueva_exitosa(self, client, auth_admin):
        nueva_sub = {
            "endpoint": "https://fcm.googleapis.com/nueva",
            "keys": {"p256dh": "abc", "auth": "xyz"},
        }
        resp = client.post(
            "/api/push/subscribe",
            json={"subscription": nueva_sub},
            headers=auth_admin,
        )
        assert resp.status_code == 201
        assert "registrada" in resp.json()["mensaje"].lower()

    def test_suscripcion_duplicada_no_falla(self, client, auth_admin):
        # Misma suscripción dos veces → debe aceptar sin error
        payload = {"subscription": SUSCRIPCION_EJEMPLO}
        resp1 = client.post("/api/push/subscribe", json=payload, headers=auth_admin)
        resp2 = client.post("/api/push/subscribe", json=payload, headers=auth_admin)
        assert resp1.status_code == 201
        assert resp2.status_code == 201

    def test_sin_auth_devuelve_401(self, client):
        resp = client.post(
            "/api/push/subscribe",
            json={"subscription": SUSCRIPCION_EJEMPLO},
        )
        assert resp.status_code == 401


# ══════════════════════════════════════════════════════════════════════════════
# DELETE /api/push/unsubscribe
# ══════════════════════════════════════════════════════════════════════════════

class TestDesuscribirse:
    def test_elimina_suscripcion_existente(self, client, auth_admin):
        resp = client.request(
            "DELETE",
            "/api/push/unsubscribe",
            json={"subscription": SUSCRIPCION_EJEMPLO},
            headers=auth_admin,
        )
        assert resp.status_code == 204

    def test_suscripcion_inexistente_no_falla(self, client, auth_admin):
        sub_falsa = {"endpoint": "https://no.existe", "keys": {"p256dh": "x", "auth": "y"}}
        resp = client.request(
            "DELETE",
            "/api/push/unsubscribe",
            json={"subscription": sub_falsa},
            headers=auth_admin,
        )
        assert resp.status_code == 204


# ══════════════════════════════════════════════════════════════════════════════
# POST /api/push/test
# ══════════════════════════════════════════════════════════════════════════════

class TestNotificacionPrueba:
    def test_envia_notificacion_con_suscripcion_activa(self, client, auth_admin):
        with patch("backend.services.push_service.enviar_push", return_value=True):
            resp = client.post("/api/push/test", headers=auth_admin)
        assert resp.status_code == 200
        assert "1 dispositivo" in resp.json()["mensaje"]

    def test_404_cuando_usuario_sin_suscripciones(self, client, auth_empresa):
        resp = client.post("/api/push/test", headers=auth_empresa)
        assert resp.status_code == 404
        assert "suscripciones" in resp.json()["detail"].lower()

    def test_sin_auth_devuelve_401(self, client):
        resp = client.post("/api/push/test")
        assert resp.status_code == 401


# ══════════════════════════════════════════════════════════════════════════════
# push_service.enviar_push
# ══════════════════════════════════════════════════════════════════════════════

class TestEnviarPush:
    def test_retorna_false_sin_vapid_keys(self):
        from backend.services.push_service import enviar_push
        with patch("backend.services.push_service.settings") as mock_settings:
            mock_settings.VAPID_PRIVATE_KEY = ""
            mock_settings.VAPID_PUBLIC_KEY = ""
            result = enviar_push(json.dumps(SUSCRIPCION_EJEMPLO), "Título", "Cuerpo")
        assert result is False

    def test_retorna_true_cuando_push_exitoso(self):
        from backend.services.push_service import enviar_push
        with patch("backend.services.push_service.settings") as mock_settings:
            mock_settings.VAPID_PRIVATE_KEY = "clave-privada"
            mock_settings.VAPID_PUBLIC_KEY = "clave-publica"
            mock_settings.VAPID_CLAIMS_SUB = "mailto:test@test.com"
            with patch("backend.services.push_service._get_webpush") as mock_wp:
                mock_webpush = MagicMock()
                mock_wp.return_value = (mock_webpush, Exception)
                result = enviar_push(json.dumps(SUSCRIPCION_EJEMPLO), "Título", "Cuerpo")
        assert result is True

    def test_limpia_suscripcion_expirada_410(self):
        from backend.services.push_service import enviar_push

        mock_response = MagicMock()
        mock_response.status_code = 410

        class FakeWebPushException(Exception):
            def __init__(self):
                self.response = mock_response

        with patch("backend.services.push_service.settings") as mock_settings:
            mock_settings.VAPID_PRIVATE_KEY = "clave"
            mock_settings.VAPID_PUBLIC_KEY = "clave"
            mock_settings.VAPID_CLAIMS_SUB = "mailto:test@test.com"
            with patch("backend.services.push_service._get_webpush") as mock_wp:
                mock_webpush = MagicMock(side_effect=FakeWebPushException())
                mock_wp.return_value = (mock_webpush, FakeWebPushException)
                with patch("backend.services.push_service._eliminar_suscripcion") as mock_del:
                    result = enviar_push(json.dumps(SUSCRIPCION_EJEMPLO), "T", "B")
                    mock_del.assert_called_once()
        assert result is False


# ══════════════════════════════════════════════════════════════════════════════
# mora_checker
# ══════════════════════════════════════════════════════════════════════════════

class TestMoraChecker:
    def _crear_seguimiento(self, estado: EstadoSeguimiento):
        from datetime import date
        db = TestingSession()
        seg = SeguimientoMensual(
            nit9="900434099",
            anio=date.today().year,
            mes=date.today().month,
            nombre_empresa="DALMARU INVERSIONES SAS",
            ss_estado=estado,
        )
        db.merge(seg)
        db.commit()
        db.close()

    def test_no_notifica_si_empresa_no_esta_en_mora(self):
        self._crear_seguimiento(EstadoSeguimiento.CUMPLE)
        with patch("backend.services.push_service.notificar_mora") as mock_notif:
            from backend.services.mora_checker import verificar_mora_empresa
            verificar_mora_empresa("900434099")
            mock_notif.assert_not_called()

    def test_notifica_si_empresa_en_mora(self):
        self._crear_seguimiento(EstadoSeguimiento.EN_MORA)
        with patch("backend.services.push_service.notificar_mora", return_value=1) as mock_notif:
            from backend.services.mora_checker import verificar_mora_empresa
            verificar_mora_empresa("900434099")
            mock_notif.assert_called_once_with("900434099", "DALMARU INVERSIONES SAS")

    def test_verificar_todas_moras_llama_notificar_por_empresa(self):
        self._crear_seguimiento(EstadoSeguimiento.EN_MORA)
        with patch("backend.services.push_service.notificar_mora", return_value=1) as mock_notif:
            from backend.services.mora_checker import verificar_todas_las_moras
            verificar_todas_las_moras()
            assert mock_notif.call_count >= 1
