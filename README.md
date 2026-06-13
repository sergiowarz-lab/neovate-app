# Sistema Neovate — Validación y Seguimiento de Pagos SS

Sistema web para la **validación automática de planillas de Seguridad Social y Nómina** en Colombia. Permite a empresas y administradores cargar PDFs de planillas pagadas, verificar automáticamente su validez y hacer seguimiento del cumplimiento mensual.

---

## Tabla de Contenidos

- [Descripción general](#descripción-general)
- [Arquitectura](#arquitectura)
- [Operadores soportados](#operadores-soportados)
- [Requisitos](#requisitos)
- [Instalación local](#instalación-local)
- [Variables de entorno](#variables-de-entorno)
- [Correr tests](#correr-tests)
- [Deploy](#deploy)
- [Estructura del proyecto](#estructura-del-proyecto)

---

## Descripción general

El sistema recibe PDFs de planillas de SS/Nómina y los valida automáticamente verificando:

- ✅ Que el **NIT de la empresa** aparezca en el documento
- ✅ Que el **período (mes/año)** coincida con el declarado
- ✅ Que sea una planilla **tipo E (Empresa)**
- ✅ Que el operador declarado corresponda al formato del PDF

El resultado es inmediato: **Validado** o **Rechazado** con el motivo específico.

---

## Arquitectura

```
┌─────────────────────┐     HTTPS      ┌──────────────────────────┐
│  Frontend (React)   │ ◄────────────► │  Backend (FastAPI)        │
│  Netlify            │                │  Azure App Service Linux  │
│  neovate-app        │                │        │
└─────────────────────┘                └──────────────┬───────────┘
                                                      │
                                                      ▼
                                         ┌────────────────────────┐
                                         │  PostgreSQL             │
                                         │  Azure Database         │
                                         └────────────────────────┘
```

**Flujo de validación:**

1. Usuario sube PDF + datos del formulario (NIT, operador, mes, año)
2. Backend guarda el PDF, crea registro `PROCESANDO` y devuelve `202 Accepted`
3. Background task extrae texto con **PyMuPDF** y lo valida
4. Frontend hace polling cada 2 segundos hasta obtener `Validado_ok` o `Rechazado`

---

## Operadores soportados

| Operador | Tipos de documento |
|---|---|
| ASOPAGOS | Resumen Tipo 1 (Pagada), Resumen Tipo 2 (Generada) |
| APORTES EN LINEA | Resumen |
| COMPENSAR / MI PLANILLA | Resumen |
| ENLACE | Resumen |
| SOI | Resumen |
| SIMPLE PLANILLA / PAGO SIMPLE | Resumen |
| NOMINA | Único |

---

## Requisitos

| Herramienta | Versión mínima |
|---|---|
| Python | 3.12 |
| Node.js | 22 |
| PostgreSQL | 14 |

---

## Instalación local

### Backend

```bash
# Clonar repositorio
git clone https://github.com/sergiowarz-lab/neovate-app.git
cd neovate-app

# Crear entorno virtual e instalar dependencias
python -m venv .venv
.venv\Scripts\activate          # Windows
# source .venv/bin/activate     # Mac/Linux

pip install -r requirements-dev.txt

# Configurar variables de entorno
cp backend/.env.example backend/.env
# Editar backend/.env con tus credenciales

# Iniciar el servidor
python -m uvicorn backend.main:app --reload --port 4000
```

### Frontend

```bash
cd frontend
npm install
npm run dev
# Abre http://localhost:5173
```

---

## Variables de entorno

Crea `backend/.env` con las siguientes variables:

```env
# Base de datos
DATABASE_URL=postgresql://usuario:password@localhost:5432/neovate

# Seguridad
SECRET_KEY=cambia-esto-por-una-clave-segura-de-32-chars
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=480

# CORS
CORS_ORIGINS=http://localhost:5173,https://neovate-app.netlify.app
```

Para el frontend, crea `frontend/.env.local`:

```env
VITE_API_URL=http://localhost:4000/api
```

---

## Correr tests

### Backend (pytest)

```bash
# Desde la raíz del proyecto
pip install -r requirements-dev.txt
pytest                                # todos los tests
pytest tests/test_validadores.py -v   # solo validadores
pytest tests/test_api.py -v           # solo API
pytest tests/test_cumplimiento.py -v  # solo reglas de negocio
```

**Cobertura de tests backend:**

| Módulo | Tests | Qué verifica |
|---|---|---|
| `test_validadores.py` | 25+ | Detección, NIT, período, tipo E, resultado completo |
| `test_api.py` | 15+ | Login, upload, polling, autenticación |
| `test_cumplimiento.py` | 12+ | Plazos SS/Nómina, parse de fechas |

### Frontend (Vitest)

```bash
cd frontend
npm install
npm test            # ejecuta una vez
npm run test:watch  # modo watch durante desarrollo
```

**Cobertura de tests frontend:**

| Componente | Tests | Qué verifica |
|---|---|---|
| `SubirPlanilla` | 8 | Render, validaciones, flujo upload, manejo errores |

---

## Deploy

### Frontend → Netlify

Conectado automáticamente a GitHub. Cada push a `main` dispara un deploy.

```bash
git push origin main
# Netlify detecta el cambio y hace deploy en ~1-2 min
```

Variables de entorno en Netlify → Site settings → Environment variables:
```
VITE_API_URL = https://neovate-api.azurewebsites.net/api
```

### Backend → Azure App Service

```bash
git push origin main   # GitHub Actions hace el deploy automático
```

Variables de entorno en Azure → App Service → Settings → Environment variables:
```
DATABASE_URL  = postgresql://...
SECRET_KEY    = ...
CORS_ORIGINS  = http://localhost:5173,https://neovate-app.netlify.app
```

---

## Estructura del proyecto

```
neovate-app/
├── backend/
│   ├── api/                    # Endpoints FastAPI (auth, planillas, reportes...)
│   ├── core/                   # Configuración, DB, seguridad
│   ├── models.py               # Modelos SQLAlchemy
│   ├── schemas/                # Schemas Pydantic
│   ├── services/
│   │   ├── validadores/        # Validadores por operador + extractor PDF
│   │   ├── procesador.py       # Pipeline de validación en background
│   │   └── cumplimiento.py     # Reglas de plazos SS/Nómina
│   └── main.py                 # Punto de entrada FastAPI
├── frontend/
│   └── src/
│       ├── pages/              # Vistas (SubirPlanilla, Historial, Dashboard...)
│       ├── components/         # Componentes reutilizables
│       ├── auth/               # Contexto y hooks de autenticación
│       └── test/               # Tests Vitest
├── tests/                      # Tests pytest del backend
├── netlify.toml                # Configuración deploy Netlify
├── pytest.ini                  # Configuración pytest
├── requirements.txt            # Dependencias producción
└── requirements-dev.txt        # Dependencias desarrollo + testing
```

---

## Licencia

Proyecto privado — Neovate © 2025
