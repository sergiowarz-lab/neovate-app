"""
Tests de integración para los endpoints de la API REST.

Usa FastAPI TestClient con base de datos SQLite en memoria para
no afectar la base de datos de producción o desarrollo.

Para correr:
    pytest tests/test_api.py -v
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.main import app
from backend.core.database import get_db
from backend.models import Base, Usuario, RolUsuario
from backend.core.security import get_password_hash


# ─── Base de datos SQLite en memoria para tests ─────────────────────────────

SQLALCHEMY_TEST_URL = "sqlite:///./test_neovate.db"

engine_test = create_engine(
    SQLALCHEMY_TEST_URL, connect_args={"check_same_thread": False}
)
TestingSession = sessionmaker(bind=engine_test)


def override_get_db():
    db = TestingSession()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(autouse=True)
def setup_db():
    """Crea tablas antes de cada test y las elimina al final."""
    Base.metadata.create_all(bind=engine_test)
    db = TestingSession()
    db.add(Usuario(
        username="admin",
        email="admin@test.com",
        hashed_password=get_password_hash("admin123"),
        rol=RolUsuario.ADMIN,
        activo=True,
    ))
    db.commit()
    db.close()
    yield
    Base.metadata.drop_all(bind=engine_test)


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def token(client):
    """Obtiene un token JWT válido para el usuario admin."""
    resp = client.post("/api/auth/token", data={"username": "admin", "password": "admin123"})
    assert resp.status_code == 200
    return resp.json()["access_token"]


@pytest.fixture
def auth(token):
    """Headers de autorización listos para usar."""
    return {"Authorization": f"Bearer {token}"}


# ══════════════════════════════════════════════════════════════════════════════
# Salud del servidor
# ══════════════════════════════════════════════════════════════════════════════

class TestHealth:
    def test_health_ok(self, client):
        resp = client.get("/api/health")
        assert resp.status_code == 200
        assert resp.json()["status"] == "ok"


# ══════════════════════════════════════════════════════════════════════════════
# Autenticación
# ══════════════════════════════════════════════════════════════════════════════

class TestAuth:
    def test_login_exitoso(self, client):
        resp = client.post("/api/auth/token", data={"username": "admin", "password": "admin123"})
        assert resp.status_code == 200
        assert "access_token" in resp.json()

    def test_login_password_incorrecta(self, client):
        resp = client.post("/api/auth/token", data={"username": "admin", "password": "mal"})
        assert resp.status_code == 401

    def test_login_usuario_inexistente(self, client):
        resp = client.post("/api/auth/token", data={"username": "nadie", "password": "x"})
        assert resp.status_code == 401

    def test_endpoint_protegido_sin_token(self, client):
        resp = client.get("/api/planillas/operadores")
        assert resp.status_code == 401

    def test_endpoint_protegido_con_token(self, client, auth):
        resp = client.get("/api/planillas/operadores", headers=auth)
        assert resp.status_code == 200


# ══════════════════════════════════════════════════════════════════════════════
# Planillas — listado de operadores
# ══════════════════════════════════════════════════════════════════════════════

class TestOperadores:
    def test_lista_operadores_incluye_asopagos(self, client, auth):
        resp = client.get("/api/planillas/operadores", headers=auth)
        assert resp.status_code == 200
        ops = resp.json()
        assert "ASOPAGOS" in ops

    def test_lista_operadores_es_lista(self, client, auth):
        resp = client.get("/api/planillas/operadores", headers=auth)
        assert isinstance(resp.json(), list)


# ══════════════════════════════════════════════════════════════════════════════
# Planillas — upload
# ══════════════════════════════════════════════════════════════════════════════

class TestUpload:
    def _pdf_minimo(self) -> bytes:
        """PDF mínimo válido de 1 página en blanco."""
        return (
            b"%PDF-1.4\n1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj\n"
            b"2 0 obj<</Type/Pages/Kids[3 0 R]/Count 1>>endobj\n"
            b"3 0 obj<</Type/Page/MediaBox[0 0 612 792]/Parent 2 0 R>>endobj\n"
            b"xref\n0 4\n0000000000 65535 f\n0000000009 00000 n\n"
            b"0000000058 00000 n\n0000000115 00000 n\n"
            b"trailer<</Size 4/Root 1 0 R>>\nstartxref\n190\n%%EOF"
        )

    def test_upload_acepta_pdf_valido(self, client, auth):
        resp = client.post(
            "/api/planillas/upload",
            headers=auth,
            files={"archivo": ("test.pdf", self._pdf_minimo(), "application/pdf")},
            data={"nit": "900434099", "operador": "ASOPAGOS", "mes": "11", "anio": "2025"},
        )
        assert resp.status_code == 202
        body = resp.json()
        assert "reporte_id" in body
        assert body["hoja_destino"] == "SS"

    def test_upload_rechaza_no_pdf(self, client, auth):
        resp = client.post(
            "/api/planillas/upload",
            headers=auth,
            files={"archivo": ("doc.txt", b"texto plano", "text/plain")},
            data={"nit": "900434099", "operador": "ASOPAGOS", "mes": "11", "anio": "2025"},
        )
        assert resp.status_code == 400

    def test_upload_rechaza_nit_invalido(self, client, auth):
        resp = client.post(
            "/api/planillas/upload",
            headers=auth,
            files={"archivo": ("test.pdf", self._pdf_minimo(), "application/pdf")},
            data={"nit": "123", "operador": "ASOPAGOS", "mes": "11", "anio": "2025"},
        )
        assert resp.status_code == 400

    def test_upload_rechaza_operador_desconocido(self, client, auth):
        resp = client.post(
            "/api/planillas/upload",
            headers=auth,
            files={"archivo": ("test.pdf", self._pdf_minimo(), "application/pdf")},
            data={"nit": "900434099", "operador": "FANTASMA", "mes": "11", "anio": "2025"},
        )
        assert resp.status_code == 400

    def test_upload_sin_auth_rechaza(self, client):
        resp = client.post(
            "/api/planillas/upload",
            files={"archivo": ("test.pdf", self._pdf_minimo(), "application/pdf")},
            data={"nit": "900434099", "operador": "ASOPAGOS", "mes": "11", "anio": "2025"},
        )
        assert resp.status_code == 401


# ══════════════════════════════════════════════════════════════════════════════
# Planillas — polling de estado
# ══════════════════════════════════════════════════════════════════════════════

class TestStatus:
    def test_status_reporte_inexistente_404(self, client, auth):
        resp = client.get("/api/planillas/status/NOEEXISTE", headers=auth)
        assert resp.status_code == 404

    def test_status_reporte_recien_creado_procesando(self, client, auth):
        # Crear un reporte vía upload
        pdf = (
            b"%PDF-1.4\n1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj\n"
            b"2 0 obj<</Type/Pages/Kids[3 0 R]/Count 1>>endobj\n"
            b"3 0 obj<</Type/Page/MediaBox[0 0 612 792]/Parent 2 0 R>>endobj\n"
            b"xref\n0 4\n0000000000 65535 f\n0000000009 00000 n\n"
            b"0000000058 00000 n\n0000000115 00000 n\n"
            b"trailer<</Size 4/Root 1 0 R>>\nstartxref\n190\n%%EOF"
        )
        upload = client.post(
            "/api/planillas/upload",
            headers=auth,
            files={"archivo": ("test.pdf", pdf, "application/pdf")},
            data={"nit": "900434099", "operador": "ASOPAGOS", "mes": "11", "anio": "2025"},
        )
        reporte_id = upload.json()["reporte_id"]

        status = client.get(f"/api/planillas/status/{reporte_id}", headers=auth)
        assert status.status_code == 200
        assert status.json()["estado"] in ("Procesando", "Validado_ok", "Rechazado")
