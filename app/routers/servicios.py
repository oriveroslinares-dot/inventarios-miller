from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Servicio

router = APIRouter(prefix="/api/servicios", tags=["Servicios"])


@router.get("")
def listar_servicios(db: Session = Depends(get_db)):
    servicios = db.query(Servicio).all()
    return [
        {"id": s.id, "nombre": s.nombre, "descripcion": s.descripcion, "estado": s.estado}
        for s in servicios
    ]
