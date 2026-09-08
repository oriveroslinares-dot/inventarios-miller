"""
GBS INTEGRATION SERVICE
=======================

Capa de integración preparada para el sistema de inventario/compras GBS
(existencias, compras, proveedores, costos, kardex).

Estado actual: NO existe todavía una conexión real con GBS. No se asume que
exista una API disponible. Mientras GBS_SYNC_MODE sea "NONE", el inventario
cargado manualmente se mantiene, y cualquier campo sin dato debe mostrarse
como "Dato faltante – pendiente de sincronización con GBS."
"""
from dataclasses import dataclass

from sqlalchemy.orm import Session

from app.config import settings
from app.models import Producto


@dataclass
class ResultadoSincronizacion:
    modo: str
    ejecutado: bool
    mensaje: str
    registros_actualizados: int = 0


def estado_integracion() -> dict:
    return {
        "servicio": "GBS",
        "configurado": settings.gbs_configured,
        "modo": settings.GBS_SYNC_MODE,
        "mensaje": (
            f"Integración con GBS activa en modo {settings.GBS_SYNC_MODE}."
            if settings.gbs_configured
            else "GBS no está conectado todavía. Se requiere definir el "
            "mecanismo de integración (API / CSV / Excel / base de datos de "
            "solo lectura) autorizado por TRIPLE AAA."
        ),
    }


def sincronizar_inventario(db: Session) -> ResultadoSincronizacion:
    if not settings.gbs_configured:
        return ResultadoSincronizacion(
            modo=settings.GBS_SYNC_MODE,
            ejecutado=False,
            mensaje=(
                "No se ejecutó la sincronización: GBS_SYNC_MODE=NONE. "
                "Configure las credenciales/fuente de GBS para habilitarla."
            ),
        )

    # --- Punto de extensión futuro ---
    # if settings.GBS_SYNC_MODE == "API":
    #     datos = _consumir_api_gbs()
    # elif settings.GBS_SYNC_MODE == "CSV":
    #     datos = _leer_csv_gbs()
    # ... etc, luego mapear `datos` a Producto y hacer commit.
    return ResultadoSincronizacion(
        modo=settings.GBS_SYNC_MODE,
        ejecutado=False,
        mensaje="Modo de sincronización configurado pero conector aún no implementado.",
    )


def formatear_producto(producto: Producto) -> dict:
    if producto.existencia is None:
        return {
            "disponible": False,
            "mensaje": "Dato faltante – pendiente de sincronización con GBS.",
            "nombre": producto.nombre,
            "codigo": producto.codigo,
        }
    return {
        "disponible": True,
        "codigo": producto.codigo,
        "nombre": producto.nombre,
        "categoria": producto.categoria,
        "existencia": producto.existencia,
        "unidad": producto.unidad,
        "costo_promedio": producto.costo_promedio,
        "stock_minimo": producto.stock_minimo,
        "punto_reorden": producto.punto_reorden,
        "ultima_actualizacion": producto.ultima_sincronizacion,
    }
