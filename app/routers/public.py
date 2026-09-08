"""Portal público para ciudadanos (renderizado en servidor con Jinja2)."""
from fastapi import APIRouter, Depends, Request, Form, UploadFile, File
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import (
    Servicio, Radicado, Usuario, TIPOS_DANO, TIPOS_PQR, TIPOS_USUARIO,
)
from app.security import registrar_auditoria, ip_del_request
from app.services.radicados import crear_pqr, crear_reporte_dano
from app.services.evidencias import guardar_evidencia
from app.schemas import PQRCreate, DanoCreate

router = APIRouter(tags=["Portal público"])
templates = Jinja2Templates(directory="templates")


def _ctx(request: Request, **extra) -> dict:
    base = {"request": request, "es_admin": False}
    base.update(extra)
    return base


@router.get("/")
def home(request: Request, db: Session = Depends(get_db)):
    servicios = db.query(Servicio).all()
    return templates.TemplateResponse("public/home.html", _ctx(request, servicios=servicios))


# ---------------------------------------------------------------------------
# REPORTAR DAÑO
# ---------------------------------------------------------------------------

@router.get("/reportar-dano")
def reportar_dano_form(request: Request, db: Session = Depends(get_db)):
    servicios = db.query(Servicio).all()
    return templates.TemplateResponse(
        "public/reportar_dano.html", _ctx(request, servicios=servicios, tipos_dano=TIPOS_DANO)
    )


@router.post("/reportar-dano")
async def reportar_dano_submit(
    request: Request, db: Session = Depends(get_db),
    tipo_dano: str = Form(...), direccion: str = Form(...), barrio: str = Form(""),
    descripcion: str = Form(...), servicio_id: str = Form(""),
    numero_documento: str = Form(...), tipo_documento: str = Form("CC"),
    nombre_completo: str = Form(""), telefono: str = Form(""), correo: str = Form(""),
    latitud: str = Form(""), longitud: str = Form(""),
    fotografia: UploadFile | None = File(None),
):
    datos = DanoCreate(
        tipo_dano=tipo_dano, direccion=direccion, barrio=barrio or None, descripcion=descripcion,
        servicio_id=int(servicio_id) if servicio_id else None,
        numero_documento=numero_documento, tipo_documento=tipo_documento,
        nombre_completo=nombre_completo or None, telefono=telefono or None, correo=correo or None,
        latitud=float(latitud) if latitud else None, longitud=float(longitud) if longitud else None,
        canal_origen="WEB",
    )
    radicado = crear_reporte_dano(db, datos)

    if fotografia is not None and fotografia.filename:
        contenido = await fotografia.read()
        if contenido:
            guardar_evidencia(db, radicado.id, fotografia.filename, contenido)

    registrar_auditoria(
        db, usuario="anonimo", accion="CREAR_DANO", resultado="EXITOSO",
        entidad="Radicado", entidad_id=radicado.id, ip=ip_del_request(request),
    )
    return RedirectResponse(f"/confirmacion/{radicado.numero_radicado}", status_code=303)


# ---------------------------------------------------------------------------
# PRESENTAR PQR
# ---------------------------------------------------------------------------

@router.get("/presentar-pqr")
def presentar_pqr_form(request: Request, db: Session = Depends(get_db)):
    servicios = db.query(Servicio).all()
    return templates.TemplateResponse(
        "public/presentar_pqr.html", _ctx(request, servicios=servicios, tipos_pqr=TIPOS_PQR)
    )


@router.post("/presentar-pqr")
async def presentar_pqr_submit(
    request: Request, db: Session = Depends(get_db),
    tipo_pqr: str = Form(...), asunto: str = Form(...), descripcion: str = Form(...),
    servicio_id: str = Form(""), direccion: str = Form(""),
    numero_documento: str = Form(...), tipo_documento: str = Form("CC"),
    nombre_completo: str = Form(""), telefono: str = Form(""), correo: str = Form(""),
    evidencia_archivo: UploadFile | None = File(None),
):
    datos = PQRCreate(
        tipo_pqr=tipo_pqr, asunto=asunto, descripcion=descripcion,
        servicio_id=int(servicio_id) if servicio_id else None, direccion=direccion or None,
        numero_documento=numero_documento, tipo_documento=tipo_documento,
        nombre_completo=nombre_completo or None, telefono=telefono or None, correo=correo or None,
        canal_origen="WEB",
    )
    radicado = crear_pqr(db, datos)

    if evidencia_archivo is not None and evidencia_archivo.filename:
        contenido = await evidencia_archivo.read()
        if contenido:
            guardar_evidencia(db, radicado.id, evidencia_archivo.filename, contenido)

    registrar_auditoria(
        db, usuario="anonimo", accion="CREAR_PQR", resultado="EXITOSO",
        entidad="Radicado", entidad_id=radicado.id, ip=ip_del_request(request),
    )
    return RedirectResponse(f"/confirmacion/{radicado.numero_radicado}", status_code=303)


@router.get("/confirmacion/{numero_radicado}")
def confirmacion(numero_radicado: str, request: Request, db: Session = Depends(get_db)):
    radicado = db.query(Radicado).filter(Radicado.numero_radicado == numero_radicado).first()
    return templates.TemplateResponse("public/confirmacion.html", _ctx(request, radicado=radicado))


# ---------------------------------------------------------------------------
# CONSULTAR RADICADO
# ---------------------------------------------------------------------------

@router.get("/consultar-radicado")
def consultar_radicado_form(request: Request, numero_radicado: str = "", db: Session = Depends(get_db)):
    radicado = None
    buscado = False
    if numero_radicado:
        buscado = True
        radicado = (
            db.query(Radicado)
            .filter(Radicado.numero_radicado == numero_radicado.strip().upper())
            .first()
        )
        registrar_auditoria(
            db, usuario="anonimo", accion="CONSULTAR_RADICADO",
            resultado="EXITOSO" if radicado else "RECHAZADO",
            entidad="Radicado", entidad_id=numero_radicado, ip=ip_del_request(request),
        )
    return templates.TemplateResponse(
        "public/consultar_radicado.html",
        _ctx(request, radicado=radicado, buscado=buscado, numero_radicado=numero_radicado),
    )


# ---------------------------------------------------------------------------
# REGISTRAR USUARIO
# ---------------------------------------------------------------------------

@router.get("/registrar-usuario")
def registrar_usuario_form(request: Request):
    return templates.TemplateResponse(
        "public/registrar_usuario.html", _ctx(request, tipos_usuario=TIPOS_USUARIO)
    )


@router.post("/registrar-usuario")
def registrar_usuario_submit(
    request: Request, db: Session = Depends(get_db),
    tipo_documento: str = Form(...), numero_documento: str = Form(...),
    nombre_completo: str = Form(...), telefono: str = Form(""), correo: str = Form(""),
    direccion: str = Form(""), municipio: str = Form("Cartagenita"), barrio: str = Form(""),
    tipo_usuario: str = Form("Residencial"), estrato: str = Form(""),
):
    existente = db.query(Usuario).filter(Usuario.numero_documento == numero_documento).first()
    if existente:
        return templates.TemplateResponse(
            "public/registrar_usuario.html",
            _ctx(request, tipos_usuario=TIPOS_USUARIO, error="Ya existe un usuario registrado con ese número de documento."),
            status_code=409,
        )

    usuario = Usuario(
        tipo_documento=tipo_documento, numero_documento=numero_documento,
        nombre_completo=nombre_completo, telefono=telefono or None, correo=correo or None,
        direccion=direccion or None, municipio=municipio or None, barrio=barrio or None,
        tipo_usuario=tipo_usuario, estrato=int(estrato) if estrato else None,
    )
    db.add(usuario)
    db.commit()
    registrar_auditoria(
        db, usuario="anonimo", accion="REGISTRAR_USUARIO", resultado="EXITOSO",
        entidad="Usuario", entidad_id=usuario.id, ip=ip_del_request(request),
    )
    return RedirectResponse(
        "/?mensaje=Registro exitoso. Ya puedes reportar daños o presentar PQR.", status_code=303
    )
