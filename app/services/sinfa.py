"""
SINFA INTEGRATION SERVICE
=========================

Capa de integración preparada para el sistema financiero/comercial SINFA de
TRIPLE AAA (facturación, consumos, cartera, pagos, tarifas, usuarios).

Estado actual: NO existe todavía una conexión real con SINFA. Esta capa NO
asume que existe una API disponible; se deja preparada para que, cuando se
defina el mecanismo real, solo sea necesario implementar `sincronizar_*`
sin tener que tocar el resto del sistema (rutas, panel administrativo, etc.).

Mecanismos de sincronización soportados a futuro (configurables por
SINFA_SYNC_MODE en variables de entorno):
    - API           : llamadas HTTP a la API de SINFA.
    - CSV           : archivos planos exportados periódicamente.
    - EXCEL         : archivos .xlsx exportados periódicamente.
    - DB_READONLY   : conexión de solo lectura a la base de datos de SINFA.
    - NONE          : sin integración (estado actual).

Mientras SINFA_SYNC_MODE sea "NONE", todas las consultas de facturación,
consumo y cartera deben mostrar explícitamente que el dato no está
disponible ("Dato faltante") en lugar de inventar valores.
"""
from datetime import datetime
from dataclasses import dataclass

from sqlalchemy.orm import Session

from app.config import settings
from app.models import Factura, Consumo, Cartera, Pago, Tarifa


@dataclass
class ResultadoSincronizacion:
    modo: str
    ejecutado: bool
    mensaje: str
    registros_actualizados: int = 0


def estado_integracion() -> dict:
    return {
        "servicio": "SINFA",
        "configurado": settings.sinfa_configured,
        "modo": settings.SINFA_SYNC_MODE,
        "mensaje": (
            "Integración con SINFA activa en modo "
            f"{settings.SINFA_SYNC_MODE}."
            if settings.sinfa_configured
            else "SINFA no está conectado todavía. Se requiere definir el "
            "mecanismo de integración (API / CSV / Excel / base de datos de "
            "solo lectura) autorizado por TRIPLE AAA."
        ),
    }


def sincronizar_facturacion(db: Session) -> ResultadoSincronizacion:
    """
    Punto único de entrada para sincronizar facturación/consumo/cartera/pagos
    desde SINFA. Hoy no hay fuente real conectada: no se modifica ningún
    registro y se informa el motivo con claridad.
    """
    if not settings.sinfa_configured:
        return ResultadoSincronizacion(
            modo=settings.SINFA_SYNC_MODE,
            ejecutado=False,
            mensaje=(
                "No se ejecutó la sincronización: SINFA_SYNC_MODE=NONE. "
                "Configure las credenciales/fuente de SINFA para habilitarla."
            ),
        )

    # --- Punto de extensión futuro ---
    # if settings.SINFA_SYNC_MODE == "API":
    #     datos = _consumir_api_sinfa()
    # elif settings.SINFA_SYNC_MODE == "CSV":
    #     datos = _leer_csv_sinfa()
    # ... etc, luego mapear `datos` a Factura/Consumo/Cartera/Pago y hacer commit.
    return ResultadoSincronizacion(
        modo=settings.SINFA_SYNC_MODE,
        ejecutado=False,
        mensaje="Modo de sincronización configurado pero conector aún no implementado.",
    )


def sincronizar_tarifas(db: Session) -> ResultadoSincronizacion:
    if not settings.sinfa_configured:
        return ResultadoSincronizacion(
            modo=settings.SINFA_SYNC_MODE,
            ejecutado=False,
            mensaje=(
                "No se ejecutó la sincronización de tarifas: SINFA no está "
                "conectado. Las tarifas cargadas manualmente permanecen como "
                "'Referencial' hasta ser confirmadas en SINFA."
            ),
        )
    return ResultadoSincronizacion(
        modo=settings.SINFA_SYNC_MODE,
        ejecutado=False,
        mensaje="Modo de sincronización configurado pero conector aún no implementado.",
    )


def formatear_factura(factura: Factura | None) -> dict:
    if factura is None or factura.valor_total is None:
        return {"disponible": False, "mensaje": "Dato faltante"}
    return {
        "disponible": True,
        "periodo": factura.periodo,
        "fecha_facturacion": factura.fecha_facturacion,
        "fecha_vencimiento": factura.fecha_vencimiento,
        "valor_total": factura.valor_total,
        "estado": factura.estado,
        "ultima_actualizacion": factura.ultima_sincronizacion,
    }


def formatear_cartera(cartera: Cartera | None) -> dict:
    if cartera is None or cartera.saldo is None:
        return {"disponible": False, "mensaje": "Información no disponible actualmente."}
    return {
        "disponible": True,
        "saldo": cartera.saldo,
        "estado": cartera.estado,
        "ultima_actualizacion": cartera.ultima_sincronizacion,
    }


def formatear_consumo(consumo: Consumo | None) -> dict:
    if consumo is None or consumo.consumo_m3 is None:
        return {"disponible": False, "mensaje": "Dato faltante"}
    return {
        "disponible": True,
        "periodo": consumo.periodo,
        "lectura_anterior": consumo.lectura_anterior,
        "lectura_actual": consumo.lectura_actual,
        "consumo_m3": consumo.consumo_m3,
        "ultima_actualizacion": consumo.ultima_sincronizacion,
    }


def formatear_tarifa(tarifa: Tarifa) -> dict:
    if tarifa.valor is None or tarifa.estado != "Confirmada en SINFA":
        return {
            "disponible": False,
            "mensaje": "Dato faltante – pendiente de validación en SINFA.",
            "concepto": tarifa.concepto,
        }
    return {
        "disponible": True,
        "concepto": tarifa.concepto,
        "valor": tarifa.valor,
        "unidad": tarifa.unidad,
        "fecha_vigencia": tarifa.fecha_vigencia,
        "fuente": tarifa.fuente,
    }
