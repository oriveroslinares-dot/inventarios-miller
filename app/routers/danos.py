from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import ReporteDano, Radicado
from app.schemas import DanoCreate, RadicadoDetalleOut
from app.services.radicados import crear_reporte_dano
from app.security import registrar_auditoria, ip_del_request

router = APIRouter(prefix="/api/danos", tags=["Daños"])


@router.post("", response_model=RadicadoDetalleOut)
def crear_dano_endpoint(datos: DanoCreate, request: Request, db: Session = Depends(get_db)):
    """Registra un reporte de daño y genera su radicado único."""
    radicado = crear_reporte_dano(db, datos)
    registrar_auditoria(
        db, usuario="anonimo", accion="CREAR_DANO", resultado="EXITOSO",
        entidad="Radicado", entidad_id=radicado.id, ip=ip_del_request(request),
    )
    return radicado


@router.get("/{dano_id}", response_model=RadicadoDetalleOut)
def obtener_dano(dano_id: int, db: Session = Depends(get_db)):
    dano = db.get(ReporteDano, dano_id)
    if not dano:
        raise HTTPException(status_code=404, detail="Reporte de daño no encontrado.")
    return db.get(Radicado, dano.radicado_id)
