from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Tarifa, UsuarioInterno
from app.schemas import TarifaOut, TarifaCreate
from app.security import requiere_rol, registrar_auditoria, ip_del_request
from app.services import sinfa as sinfa_service

router = APIRouter(prefix="/api/tarifas", tags=["Tarifas"])


@router.get("", response_model=list[TarifaOut])
def listar_tarifas(
    db: Session = Depends(get_db),
    servicio_id: int | None = Query(None),
    tipo_usuario: str | None = Query(None),
    estrato: int | None = Query(None),
):
    q = db.query(Tarifa)
    if servicio_id:
        q = q.filter(Tarifa.servicio_id == servicio_id)
    if tipo_usuario:
        q = q.filter(Tarifa.tipo_usuario == tipo_usuario)
    if estrato is not None:
        q = q.filter(Tarifa.estrato == estrato)
    return q.order_by(Tarifa.servicio_id, Tarifa.concepto).all()


@router.post("", response_model=TarifaOut)
def crear_tarifa(
    datos: TarifaCreate,
    request: Request,
    db: Session = Depends(get_db),
    usuario_actual: UsuarioInterno = Depends(requiere_rol("ADMINISTRADOR", "SUPERVISOR")),
):
    """
    Crea/actualiza una tarifa parametrizable. Los valores cargados manualmente
    quedan como 'Referencial' hasta ser confirmados oficialmente en SINFA
    (estado='Confirmada en SINFA'), tal como exige la regla de no presentar
    valores proyectados como tarifas vigentes.
    """
    tarifa = Tarifa(**datos.model_dump())
    db.add(tarifa)
    db.commit()
    db.refresh(tarifa)

    registrar_auditoria(
        db, usuario=usuario_actual.correo, accion="CREAR_TARIFA", resultado="EXITOSO",
        entidad="Tarifa", entidad_id=tarifa.id, ip=ip_del_request(request),
    )
    return tarifa


@router.get("/sinfa/estado")
def estado_sinfa():
    return sinfa_service.estado_integracion()
