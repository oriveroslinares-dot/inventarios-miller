from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Request, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Radicado, Usuario, UsuarioInterno, ESTADOS_RADICADO, TIPOS_RADICADO
from app.schemas import (
    RadicadoOut, RadicadoDetalleOut, CambioEstadoIn,
)
from app.services.radicados import generar_numero_radicado, registrar_historial, cambiar_estado_radicado
from app.security import (
    requiere_rol, get_current_user_optional, registrar_auditoria, ip_del_request,
)
from pydantic import BaseModel, field_validator

router = APIRouter(prefix="/api/radicados", tags=["Radicados"])


class SolicitudCreate(BaseModel):
    descripcion: str
    numero_documento: str
    tipo_documento: str = "CC"
    nombre_completo: str | None = None
    telefono: str | None = None
    correo: str | None = None
    servicio_id: int | None = None
    prioridad: str = "Media"
    canal_origen: str = "WEB"


@router.post("", response_model=RadicadoOut)
def crear_solicitud(datos: SolicitudCreate, request: Request, db: Session = Depends(get_db)):
    """Crea una solicitud genérica (tipo SOLICITUD) y genera su radicado único."""
    from app.services.radicados import obtener_o_crear_usuario

    usuario = obtener_o_crear_usuario(
        db, datos.numero_documento, datos.tipo_documento, datos.nombre_completo,
        datos.telefono, datos.correo,
    )
    numero = generar_numero_radicado(db, "SOLICITUD")
    radicado = Radicado(
        numero_radicado=numero,
        tipo="SOLICITUD",
        usuario_id=usuario.id,
        servicio_id=datos.servicio_id,
        descripcion=datos.descripcion,
        estado="Recibido",
        prioridad=datos.prioridad,
        canal_origen=datos.canal_origen,
    )
    db.add(radicado)
    db.flush()
    registrar_historial(db, radicado, estado_nuevo="Recibido", comentario="Solicitud creada.")
    db.commit()
    db.refresh(radicado)

    registrar_auditoria(
        db, usuario="anonimo", accion="CREAR_SOLICITUD", resultado="EXITOSO",
        entidad="Radicado", entidad_id=radicado.id, ip=ip_del_request(request),
    )
    return radicado


@router.get("", response_model=list[RadicadoOut])
def listar_radicados(
    db: Session = Depends(get_db),
    usuario_actual: UsuarioInterno = Depends(
        requiere_rol("ADMINISTRADOR", "FUNCIONARIO", "SUPERVISOR", "CONSULTA")
    ),
    tipo: str | None = Query(None),
    estado: str | None = Query(None),
    servicio_id: int | None = Query(None),
    prioridad: str | None = Query(None),
    usuario_id: int | None = Query(None),
    desde: datetime | None = Query(None),
    hasta: datetime | None = Query(None),
    skip: int = 0,
    limit: int = 200,
):
    q = db.query(Radicado)
    if tipo:
        q = q.filter(Radicado.tipo == tipo)
    if estado:
        q = q.filter(Radicado.estado == estado)
    if servicio_id:
        q = q.filter(Radicado.servicio_id == servicio_id)
    if prioridad:
        q = q.filter(Radicado.prioridad == prioridad)
    if usuario_id:
        q = q.filter(Radicado.usuario_id == usuario_id)
    if desde:
        q = q.filter(Radicado.fecha_creacion >= desde)
    if hasta:
        q = q.filter(Radicado.fecha_creacion <= hasta)
    return q.order_by(Radicado.fecha_creacion.desc()).offset(skip).limit(limit).all()


@router.get("/{numero_radicado}", response_model=RadicadoDetalleOut)
def consultar_radicado(
    numero_radicado: str,
    request: Request,
    numero_documento: str | None = Query(None, description="Validación adicional opcional"),
    db: Session = Depends(get_db),
):
    """Consulta pública del estado de un radicado por su número."""
    radicado = (
        db.query(Radicado)
        .filter(Radicado.numero_radicado == numero_radicado.strip().upper())
        .first()
    )
    ip = ip_del_request(request)
    if not radicado:
        registrar_auditoria(
            db, usuario="anonimo", accion="CONSULTAR_RADICADO", resultado="RECHAZADO",
            entidad="Radicado", entidad_id=numero_radicado, ip=ip, detalle="No encontrado",
        )
        raise HTTPException(status_code=404, detail="Radicado no encontrado.")

    if numero_documento:
        usuario = db.get(Usuario, radicado.usuario_id) if radicado.usuario_id else None
        if not usuario or usuario.numero_documento != numero_documento:
            registrar_auditoria(
                db, usuario="anonimo", accion="CONSULTAR_RADICADO", resultado="RECHAZADO",
                entidad="Radicado", entidad_id=radicado.id, ip=ip,
                detalle="Documento de validación no coincide.",
            )
            raise HTTPException(status_code=403, detail="El documento no coincide con el radicado.")

    registrar_auditoria(
        db, usuario="anonimo", accion="CONSULTAR_RADICADO", resultado="EXITOSO",
        entidad="Radicado", entidad_id=radicado.id, ip=ip,
    )
    return radicado


@router.patch("/{numero_radicado}/estado", response_model=RadicadoDetalleOut)
def cambiar_estado(
    numero_radicado: str,
    datos: CambioEstadoIn,
    request: Request,
    db: Session = Depends(get_db),
    usuario_actual: UsuarioInterno = Depends(
        requiere_rol("ADMINISTRADOR", "FUNCIONARIO", "SUPERVISOR")
    ),
):
    radicado = (
        db.query(Radicado)
        .filter(Radicado.numero_radicado == numero_radicado.strip().upper())
        .first()
    )
    if not radicado:
        raise HTTPException(status_code=404, detail="Radicado no encontrado.")

    radicado = cambiar_estado_radicado(
        db, radicado,
        estado_nuevo=datos.estado_nuevo,
        comentario=datos.comentario,
        usuario_interno_id=usuario_actual.id,
        realizado_por=usuario_actual.nombre_completo,
        funcionario_asignado_id=datos.funcionario_asignado_id,
        respuesta=datos.respuesta,
    )
    registrar_auditoria(
        db, usuario=usuario_actual.correo, accion="CAMBIAR_ESTADO_RADICADO", resultado="EXITOSO",
        entidad="Radicado", entidad_id=radicado.id, ip=ip_del_request(request),
        detalle=f"Nuevo estado: {datos.estado_nuevo}",
    )
    return radicado
