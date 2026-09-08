from fastapi import APIRouter, Depends, HTTPException, status, Request, Response
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import UsuarioInterno
from app.schemas import LoginIn, TokenOut
from app.security import (
    verify_password, crear_token, registrar_auditoria, ip_del_request,
    COOKIE_NAME,
)

router = APIRouter(prefix="/api/auth", tags=["Autenticación"])


@router.post("/login", response_model=TokenOut)
def login(datos: LoginIn, request: Request, response: Response, db: Session = Depends(get_db)):
    usuario = db.query(UsuarioInterno).filter(UsuarioInterno.correo == datos.correo).first()
    ip = ip_del_request(request)

    if not usuario or not usuario.activo or not verify_password(datos.password, usuario.password_hash):
        registrar_auditoria(
            db, usuario=datos.correo, accion="LOGIN", resultado="RECHAZADO", ip=ip,
            detalle="Credenciales inválidas.",
        )
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Correo o contraseña inválidos.")

    token = crear_token(usuario)
    response.set_cookie(
        key=COOKIE_NAME, value=token, httponly=True, samesite="lax", max_age=60 * 60 * 8
    )
    registrar_auditoria(db, usuario=usuario.correo, accion="LOGIN", resultado="EXITOSO", ip=ip)
    return TokenOut(access_token=token, rol=usuario.rol, nombre_completo=usuario.nombre_completo)


@router.post("/logout")
def logout(response: Response):
    response.delete_cookie(COOKIE_NAME)
    return {"mensaje": "Sesión cerrada."}
