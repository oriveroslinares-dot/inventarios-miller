from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Usuario, UsuarioInterno
from app.schemas import UsuarioCreate, UsuarioOut
from app.security import requiere_rol, registrar_auditoria, ip_del_request, get_current_user

router = APIRouter(prefix="/api/usuarios", tags=["Usuarios"])


@router.post("", response_model=UsuarioOut)
def crear_usuario(
    datos: UsuarioCreate,
    request: Request,
    db: Session = Depends(get_db),
    usuario_actual: UsuarioInterno = Depends(requiere_rol("ADMINISTRADOR", "FUNCIONARIO", "SUPERVISOR")),
):
    existente = db.query(Usuario).filter(Usuario.numero_documento == datos.numero_documento).first()
    if existente:
        raise HTTPException(status_code=409, detail="Ya existe un usuario con ese número de documento.")

    usuario = Usuario(**datos.model_dump())
    db.add(usuario)
    db.commit()
    db.refresh(usuario)

    registrar_auditoria(
        db, usuario=usuario_actual.correo, accion="CREAR_USUARIO", resultado="EXITOSO",
        entidad="Usuario", entidad_id=usuario.id, ip=ip_del_request(request),
    )
    return usuario


@router.get("", response_model=list[UsuarioOut])
def listar_usuarios(
    db: Session = Depends(get_db),
    usuario_actual: UsuarioInterno = Depends(requiere_rol("ADMINISTRADOR", "FUNCIONARIO", "SUPERVISOR", "CONSULTA")),
    skip: int = 0,
    limit: int = 100,
):
    return db.query(Usuario).order_by(Usuario.id.desc()).offset(skip).limit(limit).all()


@router.get("/{usuario_id}", response_model=UsuarioOut)
def obtener_usuario(
    usuario_id: int,
    db: Session = Depends(get_db),
    usuario_actual: UsuarioInterno = Depends(requiere_rol("ADMINISTRADOR", "FUNCIONARIO", "SUPERVISOR", "CONSULTA")),
):
    usuario = db.get(Usuario, usuario_id)
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado.")
    return usuario
