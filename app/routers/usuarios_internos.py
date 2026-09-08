from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import UsuarioInterno
from app.schemas import UsuarioInternoCreate
from app.security import hash_password, requiere_rol, registrar_auditoria, ip_del_request

router = APIRouter(prefix="/api/usuarios-internos", tags=["Usuarios internos (funcionarios)"])


@router.get("")
def listar_funcionarios(
    db: Session = Depends(get_db),
    usuario_actual: UsuarioInterno = Depends(requiere_rol("ADMINISTRADOR", "SUPERVISOR")),
):
    funcionarios = db.query(UsuarioInterno).all()
    return [
        {
            "id": f.id, "nombre_completo": f.nombre_completo, "correo": f.correo,
            "rol": f.rol, "activo": f.activo,
        }
        for f in funcionarios
    ]


@router.post("")
def crear_funcionario(
    datos: UsuarioInternoCreate,
    request: Request,
    db: Session = Depends(get_db),
    usuario_actual: UsuarioInterno = Depends(requiere_rol("ADMINISTRADOR")),
):
    existente = db.query(UsuarioInterno).filter(UsuarioInterno.correo == datos.correo).first()
    if existente:
        raise HTTPException(status_code=409, detail="Ya existe un funcionario con ese correo.")

    funcionario = UsuarioInterno(
        nombre_completo=datos.nombre_completo,
        correo=datos.correo,
        telefono=datos.telefono,
        rol=datos.rol,
        password_hash=hash_password(datos.password),
    )
    db.add(funcionario)
    db.commit()
    db.refresh(funcionario)

    registrar_auditoria(
        db, usuario=usuario_actual.correo, accion="CREAR_FUNCIONARIO", resultado="EXITOSO",
        entidad="UsuarioInterno", entidad_id=funcionario.id, ip=ip_del_request(request),
    )
    return {"id": funcionario.id, "correo": funcionario.correo, "rol": funcionario.rol}
