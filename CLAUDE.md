# Guía de desarrollo — Sistema Neovate

## Stack tecnológico

| Capa | Tecnología |
|---|---|
| Backend | Python 3.12 + FastAPI + SQLAlchemy 2 |
| Base de datos | PostgreSQL (Azure Database en prod, SQLite en tests) |
| Migraciones | Alembic |
| Frontend | React 19 + TypeScript + Vite 8 + Tailwind CSS 4 |
| Tests backend | pytest + FastAPI TestClient |
| Tests frontend | Vitest + Testing Library |
| Deploy backend | Azure App Service Linux |
| Deploy frontend | Netlify (CI/CD desde GitHub main) |

## Comandos esenciales

```bash
# Backend
python -m uvicorn backend.main:app --reload --port 4000
pytest                          # todos los tests
pytest tests/test_validadores.py -v

# Frontend
cd frontend && npm run dev      # dev server en :5173
npm test                        # tests Vitest
npm run build                   # build producción
```

## Arquitectura de validadores

Cada operador tiene su validador en `backend/services/validadores/`. El patrón es:

```python
@registrar
class ValidadorNuevoOperador(ValidadorBase):
    OPERADOR = "NOMBRE OPERADOR"   # debe coincidir exactamente con el select del frontend
    TIPO_DOC = "RESUMEN"
    HOJA_EXCEL = "SS"              # "SS" o "Nomina"

    @classmethod
    def detectar(cls, texto: str) -> bool:
        return "TEXTO ÚNICO DEL PDF" in texto

    def validar(self) -> tuple[bool, list[str]]:
        errores = []
        if not self.validar_nit():
            errores.append("NIT no coincide con el del archivo")
        if not self.validar_periodo_universal():
            errores.append("Periodo de pensión no coincide")
        return (False, errores) if errores else (True, [])
```

Luego importarlo en `backend/services/procesador.py` para que se registre al iniciar.

## Agregar un nuevo operador (checklist)

- [ ] Crear `backend/services/validadores/nuevo_operador.py`
- [ ] Implementar `detectar()` y `validar()`
- [ ] Importar el módulo en `backend/services/procesador.py`
- [ ] Agregar tests en `tests/test_validadores.py`
- [ ] El frontend lo detecta automáticamente desde `/api/planillas/operadores`

## Variables de entorno requeridas

### Backend (`backend/.env`)
```
DATABASE_URL=postgresql://...
SECRET_KEY=clave-segura-32-chars
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=480
CORS_ORIGINS=http://localhost:5173,https://neovate-app.netlify.app
```

### Frontend (`frontend/.env.local`)
```
VITE_API_URL=http://localhost:4000/api
```

## Extracción de PDFs

El extractor usa **PyMuPDF (fitz)** como principal con **pdfplumber** como fallback.
Ambos tienen timeout de 45 segundos. Si el PDF tarda más, se marca `RECHAZADO`.

`backend/services/validadores/extractor.py`

## Base de datos

- Los modelos están en `backend/models.py`
- Las migraciones en `backend/alembic/`
- Para crear una migración: `alembic revision --autogenerate -m "descripcion"`
- Para aplicarla: `alembic upgrade head`
- En producción Alembic corre automáticamente al iniciar la app (`main.py → lifespan`)

## Deploy

Todo deploy se hace con `git push origin main`. No hay pasos manuales.

- **Netlify** detecta cambios en `frontend/` y reconstruye
- **Azure** requiere configuración de GitHub Actions o az CLI

### Variables críticas en Azure (App Service → Environment variables)
```
DATABASE_URL
SECRET_KEY
CORS_ORIGINS    ← incluir siempre https://neovate-app.netlify.app
```

## Errores frecuentes

| Síntoma | Causa | Solución |
|---|---|---|
| Login falla con CORS error | `CORS_ORIGINS` no incluye Netlify en Azure | Agregar URL en env vars y reiniciar |
| App en Azure no arranca | `DATABASE_URL` incorrecto o DB no accesible | Verificar connection string y firewall |
| PDF queda en `Procesando` forever | pdfplumber colgado (PDF complejo) | PyMuPDF resuelve esto; timeout de 45s |
| Estado `Procesando` sin cambiar | Background task falló antes de setear `reporte_id` | Revisar logs Azure → Log stream |
