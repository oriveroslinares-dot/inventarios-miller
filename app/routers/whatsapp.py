"""
Webhook de WhatsApp (Meta WhatsApp Business Platform / Cloud API).

Este router queda estructuralmente listo para conectarse con Meta:
- GET  /api/whatsapp/webhook  -> verificación del webhook (hub.challenge).
- POST /api/whatsapp/webhook  -> recepción de mensajes entrantes.

Mientras no existan credenciales reales (WHATSAPP_ACCESS_TOKEN,
WHATSAPP_PHONE_NUMBER_ID, WHATSAPP_VERIFY_TOKEN) configuradas como variables
de entorno, el envío de respuestas hacia Meta se omite y se deja constancia
en el log de mensajes salientes. La lógica conversacional (app/services/chatbot.py)
funciona igual y puede probarse mediante POST /api/whatsapp/test.
"""
import json
import logging

from fastapi import APIRouter, Depends, HTTPException, Request, Query, Response
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.models import MensajeWhatsApp
from app.schemas import WhatsAppMensajeEntrante
from app.services import chatbot as chatbot_service

logger = logging.getLogger("whatsapp")
router = APIRouter(prefix="/api/whatsapp", tags=["WhatsApp"])


@router.get("/webhook")
def verificar_webhook(
    hub_mode: str = Query(None, alias="hub.mode"),
    hub_verify_token: str = Query(None, alias="hub.verify_token"),
    hub_challenge: str = Query(None, alias="hub.challenge"),
):
    """Meta llama a este endpoint una sola vez para verificar el webhook."""
    if not settings.WHATSAPP_VERIFY_TOKEN:
        raise HTTPException(
            status_code=503,
            detail="WHATSAPP_VERIFY_TOKEN no está configurado. Defina las variables "
            "de entorno de WhatsApp antes de registrar el webhook en Meta.",
        )
    if hub_mode == "subscribe" and hub_verify_token == settings.WHATSAPP_VERIFY_TOKEN:
        return Response(content=hub_challenge, media_type="text/plain")
    raise HTTPException(status_code=403, detail="Token de verificación inválido.")


def _extraer_mensajes_meta(payload: dict) -> list[dict]:
    """Extrae (telefono, texto, wa_message_id) de un payload de Meta Cloud API."""
    mensajes = []
    for entrada in payload.get("entry", []):
        for cambio in entrada.get("changes", []):
            valor = cambio.get("value", {})
            for msg in valor.get("messages", []):
                telefono = msg.get("from")
                wa_message_id = msg.get("id")
                texto = None
                if msg.get("type") == "text":
                    texto = msg.get("text", {}).get("body")
                elif msg.get("type") == "interactive":
                    interactivo = msg.get("interactive", {})
                    if "button_reply" in interactivo:
                        texto = interactivo["button_reply"].get("title")
                    elif "list_reply" in interactivo:
                        texto = interactivo["list_reply"].get("title")
                if telefono and texto:
                    mensajes.append({
                        "telefono": telefono, "texto": texto, "wa_message_id": wa_message_id
                    })
    return mensajes


def enviar_mensaje_whatsapp(db: Session, telefono: str, texto: str) -> None:
    """
    Envía un mensaje saliente a través de la API de WhatsApp Cloud.

    Si no hay credenciales configuradas, no se realiza ninguna llamada HTTP
    real: el mensaje queda registrado como saliente para trazabilidad, y
    quien pruebe el sistema puede ver la respuesta generada por el chatbot.
    """
    db.add(MensajeWhatsApp(telefono=telefono, direccion="saliente", contenido=texto))
    db.commit()

    if not settings.whatsapp_configured:
        logger.info(
            "WhatsApp no configurado; mensaje NO enviado a Meta (modo simulación) -> %s: %s",
            telefono, texto,
        )
        return

    import httpx

    url = (
        f"https://graph.facebook.com/{settings.WHATSAPP_API_VERSION}/"
        f"{settings.WHATSAPP_PHONE_NUMBER_ID}/messages"
    )
    headers = {"Authorization": f"Bearer {settings.WHATSAPP_ACCESS_TOKEN}"}
    body = {
        "messaging_product": "whatsapp",
        "to": telefono,
        "type": "text",
        "text": {"body": texto},
    }
    try:
        with httpx.Client(timeout=10) as client:
            client.post(url, headers=headers, json=body)
    except httpx.HTTPError:
        logger.exception("Error enviando mensaje de WhatsApp a %s", telefono)


@router.post("/webhook")
async def recibir_webhook(request: Request, db: Session = Depends(get_db)):
    payload = await request.json()
    logger.info("Webhook de WhatsApp recibido: %s", json.dumps(payload)[:2000])

    for mensaje in _extraer_mensajes_meta(payload):
        db.add(MensajeWhatsApp(
            telefono=mensaje["telefono"], direccion="entrante",
            contenido=mensaje["texto"], wa_message_id=mensaje["wa_message_id"],
        ))
        db.commit()

        respuesta = chatbot_service.procesar_mensaje(db, mensaje["telefono"], mensaje["texto"])
        enviar_mensaje_whatsapp(db, mensaje["telefono"], respuesta)

    return {"status": "ok"}


@router.post("/test")
def probar_chatbot(datos: WhatsAppMensajeEntrante, db: Session = Depends(get_db)):
    """
    Endpoint de prueba para simular una conversación de WhatsApp sin depender
    de credenciales de Meta. Útil para validar la lógica del chatbot durante
    el desarrollo.
    """
    db.add(MensajeWhatsApp(telefono=datos.telefono, direccion="entrante", contenido=datos.texto))
    db.commit()
    respuesta = chatbot_service.procesar_mensaje(db, datos.telefono, datos.texto)
    db.add(MensajeWhatsApp(telefono=datos.telefono, direccion="saliente", contenido=respuesta))
    db.commit()
    return {"respuesta": respuesta}


@router.get("/estado")
def estado_whatsapp():
    return {
        "configurado": settings.whatsapp_configured,
        "mensaje": (
            "WhatsApp Business Platform conectado."
            if settings.whatsapp_configured
            else "WhatsApp no está conectado todavía. Configure "
            "WHATSAPP_ACCESS_TOKEN, WHATSAPP_PHONE_NUMBER_ID, "
            "WHATSAPP_BUSINESS_ACCOUNT_ID y WHATSAPP_VERIFY_TOKEN como variables "
            "de entorno, y registre el webhook en Meta for Developers."
        ),
    }
