from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Request
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Evidencia, Radicado
from app.schemas import EvidenciaOut
from app.security import registrar_auditoria, ip_del_request
from app.services.evidencias import guardar_evidencia

router = APIRouter(prefix="/api/evidencias", tags=["Evidencias"])


@router.post("", response_model=EvidenciaOut)
async def cargar_evidencia(
    request: Request,
    radicado_id: int = Form(...),
    archivo: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    """Adjunta una fotografía o documento como evidencia de un radicado (PQR, daño o solicitud)."""
    radicado = db.get(Radicado, radicado_id)
    if not radicado:
        raise HTTPException(status_code=404, detail="El radicado indicado no existe.")

    contenido = await archivo.read()
    evidencia = guardar_evidencia(db, radicado_id, archivo.filename or "", contenido)

    registrar_auditoria(
        db, usuario="anonimo", accion="CARGAR_EVIDENCIA", resultado="EXITOSO",
        entidad="Radicado", entidad_id=radicado_id, ip=ip_del_request(request),
        detalle=f"Archivo: {evidencia.nombre_archivo}",
    )
    return evidencia


@router.get("/radicado/{radicado_id}", response_model=list[EvidenciaOut])
def listar_evidencias(radicado_id: int, db: Session = Depends(get_db)):
    return db.query(Evidencia).filter(Evidencia.radicado_id == radicado_id).all()
