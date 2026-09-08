from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import PQR, Radicado
from app.schemas import PQRCreate, RadicadoDetalleOut
from app.services.radicados import crear_pqr
from app.security import registrar_auditoria, ip_del_request

router = APIRouter(prefix="/api/pqr", tags=["PQR"])


@router.post("", response_model=RadicadoDetalleOut)
def crear_pqr_endpoint(datos: PQRCreate, request: Request, db: Session = Depends(get_db)):
    """Registra una PQR (Petición, Queja, Reclamo o Solicitud) y genera su radicado único."""
    radicado = crear_pqr(db, datos)
    registrar_auditoria(
        db, usuario="anonimo", accion="CREAR_PQR", resultado="EXITOSO",
        entidad="Radicado", entidad_id=radicado.id, ip=ip_del_request(request),
    )
    return radicado


@router.get("/{pqr_id}", response_model=RadicadoDetalleOut)
def obtener_pqr(pqr_id: int, db: Session = Depends(get_db)):
    pqr = db.get(PQR, pqr_id)
    if not pqr:
        raise HTTPException(status_code=404, detail="PQR no encontrada.")
    return db.get(Radicado, pqr.radicado_id)
