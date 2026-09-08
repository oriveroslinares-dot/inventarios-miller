from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Producto, UsuarioInterno
from app.schemas import ProductoOut
from app.security import requiere_rol, registrar_auditoria, ip_del_request
from app.services import gbs as gbs_service

router = APIRouter(prefix="/api/inventario", tags=["Inventario"])


@router.get("", response_model=list[ProductoOut])
def listar_inventario(
    db: Session = Depends(get_db),
    categoria: str | None = Query(None),
    codigo: str | None = Query(None),
):
    q = db.query(Producto)
    if categoria:
        q = q.filter(Producto.categoria == categoria)
    if codigo:
        q = q.filter(Producto.codigo == codigo)
    return q.order_by(Producto.categoria, Producto.nombre).all()


@router.post("/sincronizar")
def sincronizar_inventario(
    request: Request,
    db: Session = Depends(get_db),
    usuario_actual: UsuarioInterno = Depends(requiere_rol("ADMINISTRADOR", "SUPERVISOR")),
):
    resultado = gbs_service.sincronizar_inventario(db)
    registrar_auditoria(
        db, usuario=usuario_actual.correo, accion="SINCRONIZAR_INVENTARIO",
        resultado="EXITOSO" if resultado.ejecutado else "RECHAZADO",
        ip=ip_del_request(request), detalle=resultado.mensaje,
    )
    return resultado


@router.get("/gbs/estado")
def estado_gbs():
    return gbs_service.estado_integracion()
