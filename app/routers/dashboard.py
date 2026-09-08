from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Radicado, UsuarioInterno
from app.security import requiere_rol

router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])


@router.get("/resumen")
def resumen(
    db: Session = Depends(get_db),
    usuario_actual: UsuarioInterno = Depends(
        requiere_rol("ADMINISTRADOR", "FUNCIONARIO", "SUPERVISOR", "CONSULTA")
    ),
):
    def contar(tipo: str | None = None, estado: str | None = None) -> int:
        q = db.query(func.count(Radicado.id))
        if tipo:
            q = q.filter(Radicado.tipo == tipo)
        if estado:
            q = q.filter(Radicado.estado == estado)
        return q.scalar() or 0

    estados_abiertos = ["Recibido", "En revisión", "Asignado", "En proceso", "Pendiente de información"]
    estados_cerrados = ["Resuelto", "Cerrado", "Rechazado"]

    return {
        "pqr_total": contar(tipo="PQR"),
        "pqr_abiertas": db.query(func.count(Radicado.id)).filter(
            Radicado.tipo == "PQR", Radicado.estado.in_(estados_abiertos)
        ).scalar() or 0,
        "pqr_en_proceso": contar(tipo="PQR", estado="En proceso"),
        "pqr_cerradas": db.query(func.count(Radicado.id)).filter(
            Radicado.tipo == "PQR", Radicado.estado.in_(estados_cerrados)
        ).scalar() or 0,
        "danos_total": contar(tipo="DANO"),
        "danos_pendientes": db.query(func.count(Radicado.id)).filter(
            Radicado.tipo == "DANO", Radicado.estado.in_(estados_abiertos)
        ).scalar() or 0,
        "solicitudes_total": contar(tipo="SOLICITUD"),
        "radicados_recientes": [
            {
                "numero_radicado": r.numero_radicado, "tipo": r.tipo, "estado": r.estado,
                "fecha_creacion": r.fecha_creacion.isoformat(),
            }
            for r in db.query(Radicado).order_by(Radicado.fecha_creacion.desc()).limit(10).all()
        ],
    }
