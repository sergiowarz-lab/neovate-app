"""Punto de entrada FastAPI del Sistema Neovate."""

import logging

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.api import auth, colaboradores, empresas, planillas, push, reportes, seguimiento, usuarios
from backend.core.config import settings
from backend.services import validadores  # noqa: F401  — registra validadores al arrancar


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)

log = logging.getLogger("neovate.main")

scheduler = AsyncIOScheduler()


@asynccontextmanager
async def lifespan(app: FastAPI):
    from backend.services.mora_checker import verificar_todas_las_moras
    # Job diario a las 8:00 AM
    scheduler.add_job(verificar_todas_las_moras, "cron", hour=8, minute=0, id="mora_diaria")
    scheduler.start()
    log.info("Scheduler iniciado — job mora_diaria activo")
    yield
    scheduler.shutdown()
    log.info("Scheduler detenido")


app = FastAPI(
    title="Sistema Neovate API",
    description="API de validación y seguimiento de pagos de Seguridad Social",
    version="1.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(usuarios.router)
app.include_router(empresas.router)
app.include_router(reportes.router)
app.include_router(seguimiento.router)
app.include_router(colaboradores.router)
app.include_router(planillas.router)
app.include_router(push.router)


@app.get("/api/health", tags=["meta"])
def health() -> dict:
    return {"status": "ok", "service": "neovate-api", "version": "1.1.0"}
