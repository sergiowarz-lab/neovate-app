# Sistema Neovate — Validación y Seguimiento de Pagos de Seguridad Social

Arquitectura multicapa API-First con FastAPI + PostgreSQL + React PWA.

## Estructura

```
proyecto_sistema_pagos/
├── backend/      FastAPI + SQLAlchemy + PostgreSQL
└── frontend/     React + Vite + PWA (WCAG 2.1 AA)
```

## Backend

Instalación (una sola vez):
```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Arrancar el servidor (importante: **desde la raíz del proyecto**, no desde `backend\`):
```powershell
cd C:\Users\sergi\OneDrive\Escritorio\proyecto_sistema_pagos
.\backend\.venv\Scripts\python.exe -m uvicorn backend.main:app --reload --port 4000
```

API disponible en `http://localhost:4000`.
Swagger UI en `http://localhost:4000/docs` (autoriza con `admin` / `admin123`).

### Migraciones de BD
```powershell
cd backend
.\.venv\Scripts\alembic.exe upgrade head
```

### Regenerar mockup data
```powershell
cd C:\Users\sergi\OneDrive\Escritorio\proyecto_sistema_pagos
.\backend\.venv\Scripts\python.exe -m backend.scripts.generate_mockup_data --yes
```

## Frontend

```powershell
cd frontend
npm install
npm run dev
```

UI disponible en `http://localhost:5173`.

## Variables de entorno

Copia `backend/.env.example` a `backend/.env` y ajusta los valores de conexión a PostgreSQL.
