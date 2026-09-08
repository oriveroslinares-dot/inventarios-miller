import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.config import settings
from app.database import Base, engine, SessionLocal
from app.seed import seed_base, seed_demo

from app.routers import (
    auth, usuarios, usuarios_internos, servicios, radicados, pqr, danos,
    evidencias, facturacion, tarifas, inventario, whatsapp, dashboard,
    admin, public,
)

logging.basicConfig(level=logging.INFO)


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed_base(db)
        seed_demo(db)
    finally:
        db.close()
    yield


app = FastAPI(
    title="TRIPLE AAA DE CARTAGENITA - Plataforma de Atención al Usuario",
    description=(
        "API y panel administrativo para la gestión de PQR, reportes de daños, "
        "radicados, facturación, tarifas e inventario, preparada para integrarse "
        "con WhatsApp Business Platform, SINFA y GBS."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")

# --- Routers de API REST ---
app.include_router(auth.router)
app.include_router(usuarios.router)
app.include_router(usuarios_internos.router)
app.include_router(servicios.router)
app.include_router(radicados.router)
app.include_router(pqr.router)
app.include_router(danos.router)
app.include_router(evidencias.router)
app.include_router(facturacion.router)
app.include_router(tarifas.router)
app.include_router(inventario.router)
app.include_router(whatsapp.router)
app.include_router(dashboard.router)

# --- Interfaz web (panel administrativo + portal público) ---
app.include_router(admin.router)
app.include_router(public.router)


@app.get("/api/salud", tags=["Salud"])
def salud():
    return {"estado": "ok", "aplicacion": settings.APP_NAME, "entorno": settings.ENVIRONMENT}
