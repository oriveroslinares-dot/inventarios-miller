from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Usuario, Factura, Cartera, Consumo
from app.schemas import FacturaOut, CarteraOut, ConsumoOut
from app.security import registrar_auditoria, ip_del_request
from app.services import sinfa as sinfa_service

router = APIRouter(prefix="/api", tags=["Facturación"])


def _validar_identidad(
    db: Session, request: Request, numero_documento: str, telefono: str | None
) -> Usuario:
    """
    La información financiera es sensible: no se entrega a cualquiera que
    conozca solo el número de documento. Se exige un segundo dato de
    validación (teléfono registrado) y se audita cada intento.
    """
    ip = ip_del_request(request)
    usuario = db.query(Usuario).filter(Usuario.numero_documento == numero_documento).first()

    if not usuario:
        registrar_auditoria(
            db, usuario="anonimo", accion="CONSULTAR_FACTURACION", resultado="RECHAZADO",
            entidad="Usuario", entidad_id=numero_documento, ip=ip, detalle="Usuario no encontrado.",
        )
        raise HTTPException(status_code=404, detail="Usuario no encontrado.")

    if not telefono or usuario.telefono != telefono:
        registrar_auditoria(
            db, usuario="anonimo", accion="CONSULTAR_FACTURACION", resultado="RECHAZADO",
            entidad="Usuario", entidad_id=usuario.id, ip=ip,
            detalle="Dato de validación (teléfono) no coincide.",
        )
        raise HTTPException(
            status_code=403,
            detail="Debe proporcionar el teléfono registrado como dato adicional de validación.",
        )

    registrar_auditoria(
        db, usuario="anonimo", accion="CONSULTAR_FACTURACION", resultado="EXITOSO",
        entidad="Usuario", entidad_id=usuario.id, ip=ip,
    )
    return usuario


@router.get("/facturas/{numero_documento}", response_model=list[FacturaOut])
def consultar_facturas(
    numero_documento: str,
    request: Request,
    telefono: str = Query(..., description="Teléfono registrado, como validación de identidad"),
    db: Session = Depends(get_db),
):
    usuario = _validar_identidad(db, request, numero_documento, telefono)
    facturas = (
        db.query(Factura)
        .filter(Factura.usuario_id == usuario.id)
        .order_by(Factura.fecha_facturacion.desc())
        .all()
    )
    return facturas


@router.get("/cartera/{numero_documento}", response_model=CarteraOut)
def consultar_cartera(
    numero_documento: str,
    request: Request,
    telefono: str = Query(..., description="Teléfono registrado, como validación de identidad"),
    db: Session = Depends(get_db),
):
    usuario = _validar_identidad(db, request, numero_documento, telefono)
    cartera = db.query(Cartera).filter(Cartera.usuario_id == usuario.id).first()
    if not cartera:
        return CarteraOut(saldo=None, estado=None, fuente="SINFA", ultima_sincronizacion=None)
    return cartera


@router.get("/consumos/{numero_documento}", response_model=list[ConsumoOut])
def consultar_consumos(
    numero_documento: str,
    request: Request,
    telefono: str = Query(..., description="Teléfono registrado, como validación de identidad"),
    db: Session = Depends(get_db),
):
    usuario = _validar_identidad(db, request, numero_documento, telefono)
    consumos = (
        db.query(Consumo)
        .filter(Consumo.usuario_id == usuario.id)
        .order_by(Consumo.periodo.desc())
        .all()
    )
    return consumos


@router.get("/sinfa/estado")
def estado_sinfa():
    return sinfa_service.estado_integracion()
