"""
Seguridad: autenticación de usuarios internos (funcionarios/administradores),
control de roles y registro de auditoría.

- Las contraseñas se guardan con hash bcrypt (nunca en texto plano).
- La sesión de los funcionarios se maneja con un JWT firmado con SECRET_KEY,
  transportado en una cookie httponly para el panel administrativo, y
  también aceptado como Bearer token para consumo directo de la API.
- Toda acción sensible (login, consulta de facturación/cartera, cambios de
  estado) debe registrarse en la tabla de auditoría mediante `registrar_auditoria`.
"""
from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import Depends, HTTPException, status, Request
from jose import jwt, JWTError
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.models import UsuarioInterno, RegistroAuditoria

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

ALGORITHM = "HS256"
COOKIE_NAME = "triple_aaa_session"


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    return pwd_context.verify(password, password_hash)


def crear_token(usuario_interno: UsuarioInterno) -> str:
    expira = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {
        "sub": str(usuario_interno.id),
        "correo": usuario_interno.correo,
        "rol": usuario_interno.rol,
        "exp": expira,
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=ALGORITHM)


def _decodificar_token(token: str) -> Optional[dict]:
    try:
        return jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        return None


def obtener_token_de_request(request: Request) -> Optional[str]:
    auth = request.headers.get("Authorization")
    if auth and auth.lower().startswith("bearer "):
        return auth.split(" ", 1)[1]
    return request.cookies.get(COOKIE_NAME)


def get_current_user(
    request: Request, db: Session = Depends(get_db)
) -> UsuarioInterno:
    token = obtener_token_de_request(request)
    credenciales_invalidas = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credenciales inválidas o sesión expirada.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if not token:
        raise credenciales_invalidas
    payload = _decodificar_token(token)
    if not payload:
        raise credenciales_invalidas
    usuario = db.get(UsuarioInterno, int(payload["sub"]))
    if not usuario or not usuario.activo:
        raise credenciales_invalidas
    return usuario


def get_current_user_optional(
    request: Request, db: Session = Depends(get_db)
) -> Optional[UsuarioInterno]:
    try:
        return get_current_user(request, db)
    except HTTPException:
        return None


def requiere_rol(*roles_permitidos: str):
    def _verificador(usuario: UsuarioInterno = Depends(get_current_user)) -> UsuarioInterno:
        if usuario.rol not in roles_permitidos:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tiene permisos suficientes para esta acción.",
            )
        return usuario

    return _verificador


def registrar_auditoria(
    db: Session,
    usuario: str,
    accion: str,
    resultado: str = "EXITOSO",
    entidad: Optional[str] = None,
    entidad_id: Optional[str] = None,
    ip: Optional[str] = None,
    detalle: Optional[str] = None,
) -> None:
    registro = RegistroAuditoria(
        usuario=usuario,
        accion=accion,
        entidad=entidad,
        entidad_id=str(entidad_id) if entidad_id is not None else None,
        ip=ip,
        resultado=resultado,
        detalle=detalle,
    )
    db.add(registro)
    db.commit()


def ip_del_request(request: Request) -> Optional[str]:
    if request.client:
        return request.client.host
    return None
