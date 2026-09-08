"""
Capa de lógica conversacional (chatbot) preparada para WhatsApp.

Esta capa es independiente del canal: recibe (telefono, texto) y retorna el
texto de respuesta, manteniendo el estado de la conversación en la tabla
`sesiones_chatbot`. El router de WhatsApp (`app/routers/whatsapp.py`) es el
único punto que debe conocer los detalles del formato de Meta Cloud API;
esta capa se puede probar de forma aislada y reutilizar para otros canales
(web chat, prueba por consola, etc.).

Reconoce 9 intenciones iniciales:
    1. Consultar factura
    2. Consultar saldo
    3. Consultar consumo
    4. Reportar daño
    5. Presentar PQR
    6. Consultar radicado
    7. Consultar tarifas
    8. Consultar información general
    9. Hablar con un asesor
"""
import json
from dataclasses import dataclass, field

from sqlalchemy.orm import Session

from app.models import (
    SesionChatbot, Servicio, Factura, Cartera, Consumo, Radicado,
    TIPOS_DANO, TIPOS_PQR,
)
from app.services import radicados as radicados_service
from app.services import sinfa as sinfa_service

MENU_PRINCIPAL = (
    "Hola, soy el asistente virtual de TRIPLE AAA.\n\n"
    "¿En qué podemos ayudarte?\n\n"
    "1. Consultar factura o saldo\n"
    "2. Reportar un daño\n"
    "3. Presentar una PQR\n"
    "4. Consultar un radicado\n"
    "5. Consultar tarifas\n"
    "6. Información sobre nuestros servicios\n"
    "7. Hablar con un asesor"
)

_PALABRAS_CLAVE_INTENCION = {
    "CONSULTAR_FACTURA": ["factura", "cuenta de cobro"],
    "CONSULTAR_SALDO": ["saldo", "cartera", "deuda", "debo"],
    "CONSULTAR_CONSUMO": ["consumo", "lectura", "medidor"],
    "REPORTAR_DANO": ["daño", "dano", "fuga", "rebose", "rota", "roto"],
    "PRESENTAR_PQR": ["pqr", "queja", "reclamo", "peticion", "petición"],
    "CONSULTAR_RADICADO": ["radicado"],
    "CONSULTAR_TARIFAS": ["tarifa", "tarifas", "precio"],
    "INFORMACION_GENERAL": ["informacion", "información", "servicios", "horario"],
    "HABLAR_ASESOR": ["asesor", "humano", "persona", "operador"],
}

_OPCION_MENU_A_INTENCION = {
    "1": "CONSULTAR_FACTURA",
    "2": "REPORTAR_DANO",
    "3": "PRESENTAR_PQR",
    "4": "CONSULTAR_RADICADO",
    "5": "CONSULTAR_TARIFAS",
    "6": "INFORMACION_GENERAL",
    "7": "HABLAR_ASESOR",
}


def reconocer_intencion(texto: str) -> str | None:
    texto_normalizado = texto.strip().lower()
    if texto_normalizado in _OPCION_MENU_A_INTENCION:
        return _OPCION_MENU_A_INTENCION[texto_normalizado]
    for intencion, palabras in _PALABRAS_CLAVE_INTENCION.items():
        if any(palabra in texto_normalizado for palabra in palabras):
            return intencion
    return None


def _get_or_create_sesion(db: Session, telefono: str) -> SesionChatbot:
    sesion = db.query(SesionChatbot).filter(SesionChatbot.telefono == telefono).first()
    if not sesion:
        sesion = SesionChatbot(telefono=telefono, estado_conversacion="MENU_PRINCIPAL", contexto_json="{}")
        db.add(sesion)
        db.commit()
        db.refresh(sesion)
    return sesion


def _contexto(sesion: SesionChatbot) -> dict:
    try:
        return json.loads(sesion.contexto_json or "{}")
    except json.JSONDecodeError:
        return {}


def _guardar_estado(db: Session, sesion: SesionChatbot, estado: str, contexto: dict):
    sesion.estado_conversacion = estado
    sesion.contexto_json = json.dumps(contexto, default=str)
    db.commit()


def _listar_tipos(opciones: list[str]) -> str:
    return "\n".join(f"{i + 1}. {op}" for i, op in enumerate(opciones))


def _reset_menu(db: Session, sesion: SesionChatbot) -> str:
    _guardar_estado(db, sesion, "MENU_PRINCIPAL", {})
    return MENU_PRINCIPAL


def procesar_mensaje(db: Session, telefono: str, texto: str) -> str:
    """Punto de entrada único: procesa un mensaje entrante y devuelve la respuesta."""
    sesion = _get_or_create_sesion(db, telefono)
    ctx = _contexto(sesion)
    estado = sesion.estado_conversacion
    texto_limpio = texto.strip()

    if texto_limpio.lower() in ("menu", "menú", "hola", "inicio", "salir", "cancelar"):
        return _reset_menu(db, sesion)

    # --- Estado inicial: menú principal ---
    if estado == "MENU_PRINCIPAL":
        intencion = reconocer_intencion(texto_limpio)
        return _iniciar_flujo(db, sesion, ctx, intencion)

    # --- Flujo: consultar factura / saldo ---
    if estado == "ESPERANDO_DOCUMENTO_FACTURA":
        return _flujo_consultar_factura(db, sesion, texto_limpio)

    # --- Flujo: consultar radicado ---
    if estado == "ESPERANDO_NUMERO_RADICADO":
        return _flujo_consultar_radicado(db, sesion, texto_limpio)

    # --- Flujo: reportar daño ---
    if estado.startswith("DANO_"):
        return _flujo_reportar_dano(db, sesion, ctx, estado, texto_limpio)

    # --- Flujo: presentar PQR ---
    if estado.startswith("PQR_"):
        return _flujo_presentar_pqr(db, sesion, ctx, estado, texto_limpio)

    # Estado desconocido: reiniciar
    return _reset_menu(db, sesion)


def _iniciar_flujo(db: Session, sesion: SesionChatbot, ctx: dict, intencion: str | None) -> str:
    if intencion in ("CONSULTAR_FACTURA", "CONSULTAR_SALDO", "CONSULTAR_CONSUMO"):
        _guardar_estado(db, sesion, "ESPERANDO_DOCUMENTO_FACTURA", {"intencion": intencion})
        return "Para consultar tu información de facturación, indícame tu número de documento."

    if intencion == "REPORTAR_DANO":
        _guardar_estado(db, sesion, "DANO_TIPO", {})
        return (
            "Vamos a registrar tu reporte de daño. Selecciona el tipo:\n\n"
            + _listar_tipos(TIPOS_DANO)
        )

    if intencion == "PRESENTAR_PQR":
        _guardar_estado(db, sesion, "PQR_TIPO", {})
        return "Vamos a radicar tu PQR. Selecciona el tipo:\n\n" + _listar_tipos(TIPOS_PQR)

    if intencion == "CONSULTAR_RADICADO":
        _guardar_estado(db, sesion, "ESPERANDO_NUMERO_RADICADO", {})
        return "Indícame el número de radicado que deseas consultar (ej: PQR-2026-000001)."

    if intencion == "CONSULTAR_TARIFAS":
        _guardar_estado(db, sesion, "MENU_PRINCIPAL", {})
        return (
            "Puedes consultar las tarifas vigentes en el panel de Tarifas de la "
            "plataforma web. Los valores no confirmados oficialmente en SINFA se "
            "muestran como 'Dato faltante – pendiente de validación en SINFA.'\n\n"
            + MENU_PRINCIPAL
        )

    if intencion == "INFORMACION_GENERAL":
        _guardar_estado(db, sesion, "MENU_PRINCIPAL", {})
        return (
            "TRIPLE AAA DE CARTAGENITA presta los servicios de Acueducto, "
            "Alcantarillado y Aseo. Escribe 'menu' en cualquier momento para "
            "volver a ver las opciones.\n\n" + MENU_PRINCIPAL
        )

    if intencion == "HABLAR_ASESOR":
        _guardar_estado(db, sesion, "MENU_PRINCIPAL", {})
        return (
            "Un asesor humano te atenderá en breve. Este caso quedará "
            "registrado para seguimiento."
        )

    return "No entendí tu mensaje.\n\n" + MENU_PRINCIPAL


def _flujo_consultar_factura(db: Session, sesion: SesionChatbot, numero_documento: str) -> str:
    from app.models import Usuario

    usuario = db.query(Usuario).filter(Usuario.numero_documento == numero_documento).first()
    if not usuario:
        _reset_menu(db, sesion)
        return (
            "No encontramos un usuario registrado con ese número de documento. "
            "Dato faltante.\n\n" + MENU_PRINCIPAL
        )

    factura = (
        db.query(Factura)
        .filter(Factura.usuario_id == usuario.id)
        .order_by(Factura.fecha_facturacion.desc())
        .first()
    )
    cartera = db.query(Cartera).filter(Cartera.usuario_id == usuario.id).first()

    info_factura = sinfa_service.formatear_factura(factura)
    info_cartera = sinfa_service.formatear_cartera(cartera)

    partes = [f"Hola {usuario.nombre_completo.split(' ')[0]}, esto encontramos:\n"]
    if info_factura["disponible"]:
        partes.append(
            f"Última factura ({info_factura['periodo']}): "
            f"${info_factura['valor_total']:,.0f} - Estado: {info_factura['estado']}"
        )
    else:
        partes.append("Factura: Dato faltante.")

    if info_cartera["disponible"]:
        partes.append(f"Saldo en cartera: ${info_cartera['saldo']:,.0f} ({info_cartera['estado']})")
    else:
        partes.append("Saldo en cartera: Información no disponible actualmente.")

    _reset_menu(db, sesion)
    return "\n".join(partes) + "\n\n" + MENU_PRINCIPAL


def _flujo_consultar_radicado(db: Session, sesion: SesionChatbot, numero_radicado: str) -> str:
    radicado = (
        db.query(Radicado)
        .filter(Radicado.numero_radicado == numero_radicado.strip().upper())
        .first()
    )
    _reset_menu(db, sesion)
    if not radicado:
        return f"No encontramos el radicado {numero_radicado}.\n\n" + MENU_PRINCIPAL

    respuesta = radicado.respuesta or "Aún no hay respuesta registrada."
    return (
        f"Radicado {radicado.numero_radicado}\n"
        f"Tipo: {radicado.tipo}\n"
        f"Estado: {radicado.estado}\n"
        f"Creado: {radicado.fecha_creacion.strftime('%Y-%m-%d %H:%M')}\n"
        f"Última actualización: {radicado.fecha_actualizacion.strftime('%Y-%m-%d %H:%M')}\n"
        f"Respuesta: {respuesta}\n\n" + MENU_PRINCIPAL
    )


def _flujo_reportar_dano(db: Session, sesion: SesionChatbot, ctx: dict, estado: str, texto: str) -> str:
    if estado == "DANO_TIPO":
        tipo = _resolver_opcion(texto, TIPOS_DANO)
        if not tipo:
            return "Opción no válida. Selecciona un número de la lista:\n\n" + _listar_tipos(TIPOS_DANO)
        ctx["tipo_dano"] = tipo
        _guardar_estado(db, sesion, "DANO_DIRECCION", ctx)
        return "Indícame la dirección donde ocurre el daño."

    if estado == "DANO_DIRECCION":
        ctx["direccion"] = texto
        _guardar_estado(db, sesion, "DANO_DESCRIPCION", ctx)
        return "Describe brevemente el daño."

    if estado == "DANO_DESCRIPCION":
        ctx["descripcion"] = texto
        _guardar_estado(db, sesion, "DANO_DOCUMENTO", ctx)
        return "Por último, indícame tu número de documento para registrar el caso."

    if estado == "DANO_DOCUMENTO":
        ctx["numero_documento"] = texto
        datos = _DatosDanoChatbot(
            tipo_dano=ctx["tipo_dano"],
            direccion=ctx["direccion"],
            descripcion=ctx["descripcion"],
            numero_documento=ctx["numero_documento"],
            telefono=sesion.telefono,
        )
        radicado = radicados_service.crear_reporte_dano(db, datos)
        _reset_menu(db, sesion)
        return (
            f"Tu reporte fue registrado con el radicado {radicado.numero_radicado}. "
            f"Estado: {radicado.estado}.\n\n" + MENU_PRINCIPAL
        )

    return _reset_menu(db, sesion)


def _flujo_presentar_pqr(db: Session, sesion: SesionChatbot, ctx: dict, estado: str, texto: str) -> str:
    if estado == "PQR_TIPO":
        tipo = _resolver_opcion(texto, TIPOS_PQR)
        if not tipo:
            return "Opción no válida. Selecciona un número de la lista:\n\n" + _listar_tipos(TIPOS_PQR)
        ctx["tipo_pqr"] = tipo
        _guardar_estado(db, sesion, "PQR_ASUNTO", ctx)
        return "Indícame el asunto de tu PQR."

    if estado == "PQR_ASUNTO":
        ctx["asunto"] = texto
        _guardar_estado(db, sesion, "PQR_DESCRIPCION", ctx)
        return "Describe con más detalle tu petición, queja, reclamo o solicitud."

    if estado == "PQR_DESCRIPCION":
        ctx["descripcion"] = texto
        _guardar_estado(db, sesion, "PQR_DOCUMENTO", ctx)
        return "Por último, indícame tu número de documento para registrar el caso."

    if estado == "PQR_DOCUMENTO":
        ctx["numero_documento"] = texto
        datos = _DatosPQRChatbot(
            tipo_pqr=ctx["tipo_pqr"],
            asunto=ctx["asunto"],
            descripcion=ctx["descripcion"],
            numero_documento=ctx["numero_documento"],
            telefono=sesion.telefono,
        )
        radicado = radicados_service.crear_pqr(db, datos)
        _reset_menu(db, sesion)
        return (
            f"Tu PQR fue registrada con el radicado {radicado.numero_radicado}. "
            f"Estado: {radicado.estado}.\n\n" + MENU_PRINCIPAL
        )

    return _reset_menu(db, sesion)


def _resolver_opcion(texto: str, opciones: list[str]) -> str | None:
    texto = texto.strip()
    if texto.isdigit():
        idx = int(texto) - 1
        if 0 <= idx < len(opciones):
            return opciones[idx]
        return None
    for op in opciones:
        if op.lower() == texto.lower():
            return op
    return None


@dataclass
class _DatosDanoChatbot:
    tipo_dano: str
    direccion: str
    descripcion: str
    numero_documento: str
    telefono: str | None = None
    tipo_documento: str = "CC"
    nombre_completo: str | None = None
    correo: str | None = None
    servicio_id: int | None = None
    latitud: float | None = None
    longitud: float | None = None
    prioridad: str = "Media"
    barrio: str | None = None
    canal_origen: str = "WHATSAPP"


@dataclass
class _DatosPQRChatbot:
    tipo_pqr: str
    asunto: str
    descripcion: str
    numero_documento: str
    telefono: str | None = None
    tipo_documento: str = "CC"
    nombre_completo: str | None = None
    correo: str | None = None
    servicio_id: int | None = None
    prioridad: str = "Media"
    direccion: str | None = None
    canal_origen: str = "WHATSAPP"
