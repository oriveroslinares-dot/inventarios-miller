"""Panel administrativo (renderizado en servidor con Jinja2) para funcionarios."""
from datetime import datetime

from fastapi import APIRouter, Depends, Request, Form, Response
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.models import (
    Usuario, UsuarioInterno, Radicado, Servicio, Tarifa, Producto,
    ParametroSistema, Factura, Cartera, Consumo, ESTADOS_RADICADO,
    TIPOS_RADICADO, PRIORIDADES, TIPOS_TARIFA, ROLES_INTERNOS, TIPOS_USUARIO,
)
from app.security import (
    get_current_user_optional, verify_password, crear_token, hash_password,
    registrar_auditoria, ip_del_request, COOKIE_NAME,
)
from app.services.radicados import cambiar_estado_radicado
from app.services import sinfa as sinfa_service
from app.services import gbs as gbs_service

router = APIRouter(prefix="/admin", tags=["Panel administrativo"])
templates = Jinja2Templates(directory="templates")


def _ctx(request: Request, usuario_actual, **extra) -> dict:
    base = {"request": request, "es_admin": True, "usuario_actual": usuario_actual}
    base.update(extra)
    return base


def _requiere_sesion(request: Request, db: Session):
    """Retorna el usuario interno autenticado o None (para redirigir a login)."""
    return get_current_user_optional(request, db)


@router.get("/login")
def login_form(request: Request, db: Session = Depends(get_db)):
    if _requiere_sesion(request, db):
        return RedirectResponse("/admin", status_code=303)
    return templates.TemplateResponse("login.html", {"request": request, "es_admin": False})


@router.post("/login")
def login_submit(
    request: Request, response: Response, db: Session = Depends(get_db),
    correo: str = Form(...), password: str = Form(...),
):
    ip = ip_del_request(request)
    usuario = db.query(UsuarioInterno).filter(UsuarioInterno.correo == correo).first()
    if not usuario or not usuario.activo or not verify_password(password, usuario.password_hash):
        registrar_auditoria(db, usuario=correo, accion="LOGIN", resultado="RECHAZADO", ip=ip)
        return templates.TemplateResponse(
            "login.html",
            {"request": request, "es_admin": False, "error": "Correo o contraseña inválidos."},
            status_code=401,
        )
    token = crear_token(usuario)
    registrar_auditoria(db, usuario=usuario.correo, accion="LOGIN", resultado="EXITOSO", ip=ip)
    resp = RedirectResponse("/admin", status_code=303)
    resp.set_cookie(COOKIE_NAME, token, httponly=True, samesite="lax", max_age=60 * 60 * 8)
    return resp


@router.post("/logout")
def logout(response: Response):
    resp = RedirectResponse("/admin/login", status_code=303)
    resp.delete_cookie(COOKIE_NAME)
    return resp


@router.get("")
def dashboard(request: Request, db: Session = Depends(get_db)):
    usuario_actual = _requiere_sesion(request, db)
    if not usuario_actual:
        return RedirectResponse("/admin/login", status_code=303)

    estados_abiertos = ["Recibido", "En revisión", "Asignado", "En proceso", "Pendiente de información"]
    estados_cerrados = ["Resuelto", "Cerrado", "Rechazado"]

    def contar(**filtros):
        q = db.query(func.count(Radicado.id))
        for campo, valor in filtros.items():
            if campo == "estado_in":
                q = q.filter(Radicado.estado.in_(valor))
            else:
                q = q.filter(getattr(Radicado, campo) == valor)
        return q.scalar() or 0

    stats = {
        "pqr_total": contar(tipo="PQR"),
        "pqr_abiertas": contar(tipo="PQR", estado_in=estados_abiertos),
        "pqr_en_proceso": contar(tipo="PQR", estado="En proceso"),
        "pqr_cerradas": contar(tipo="PQR", estado_in=estados_cerrados),
        "danos_total": contar(tipo="DANO"),
        "danos_pendientes": contar(tipo="DANO", estado_in=estados_abiertos),
        "solicitudes_total": contar(tipo="SOLICITUD"),
    }
    recientes = db.query(Radicado).order_by(Radicado.fecha_creacion.desc()).limit(10).all()
    return templates.TemplateResponse(
        "admin/dashboard.html", _ctx(request, usuario_actual, stats=stats, recientes=recientes)
    )


# ---------------------------------------------------------------------------
# USUARIOS
# ---------------------------------------------------------------------------

@router.get("/usuarios")
def usuarios_list(request: Request, db: Session = Depends(get_db)):
    usuario_actual = _requiere_sesion(request, db)
    if not usuario_actual:
        return RedirectResponse("/admin/login", status_code=303)
    usuarios = db.query(Usuario).order_by(Usuario.id.desc()).limit(300).all()
    return templates.TemplateResponse(
        "admin/usuarios.html",
        _ctx(request, usuario_actual, usuarios=usuarios, tipos_usuario=TIPOS_USUARIO),
    )


@router.post("/usuarios")
def usuarios_crear(
    request: Request, db: Session = Depends(get_db),
    tipo_documento: str = Form(...), numero_documento: str = Form(...),
    nombre_completo: str = Form(...), telefono: str = Form(""), correo: str = Form(""),
    direccion: str = Form(""), municipio: str = Form(""), barrio: str = Form(""),
    tipo_usuario: str = Form("Residencial"), estrato: str = Form(""),
):
    usuario_actual = _requiere_sesion(request, db)
    if not usuario_actual:
        return RedirectResponse("/admin/login", status_code=303)

    existente = db.query(Usuario).filter(Usuario.numero_documento == numero_documento).first()
    if existente:
        return RedirectResponse(
            "/admin/usuarios?mensaje=Ya existe un usuario con ese documento.&tipo=error", status_code=303
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
        db, usuario=usuario_actual.correo, accion="CREAR_USUARIO", resultado="EXITOSO",
        entidad="Usuario", entidad_id=usuario.id, ip=ip_del_request(request),
    )
    return RedirectResponse("/admin/usuarios?mensaje=Usuario creado correctamente.", status_code=303)


# ---------------------------------------------------------------------------
# RADICADOS / PQR / DAÑOS
# ---------------------------------------------------------------------------

@router.get("/radicados")
def radicados_list(
    request: Request, db: Session = Depends(get_db),
    tipo: str = "", estado: str = "", prioridad: str = "", servicio_id: str = "",
    desde: str = "", hasta: str = "",
):
    usuario_actual = _requiere_sesion(request, db)
    if not usuario_actual:
        return RedirectResponse("/admin/login", status_code=303)

    q = db.query(Radicado)
    if tipo:
        q = q.filter(Radicado.tipo == tipo)
    if estado:
        q = q.filter(Radicado.estado == estado)
    if prioridad:
        q = q.filter(Radicado.prioridad == prioridad)
    if servicio_id:
        q = q.filter(Radicado.servicio_id == int(servicio_id))
    if desde:
        q = q.filter(Radicado.fecha_creacion >= datetime.fromisoformat(desde))
    if hasta:
        q = q.filter(Radicado.fecha_creacion <= datetime.fromisoformat(hasta))

    radicados = q.order_by(Radicado.fecha_creacion.desc()).limit(300).all()
    servicios = db.query(Servicio).all()
    return templates.TemplateResponse(
        "admin/radicados.html",
        _ctx(
            request, usuario_actual, radicados=radicados, servicios=servicios,
            tipos=TIPOS_RADICADO, estados=ESTADOS_RADICADO, prioridades=PRIORIDADES,
            filtros={"tipo": tipo, "estado": estado, "prioridad": prioridad, "servicio_id": servicio_id},
        ),
    )


@router.get("/radicados/{numero_radicado}")
def radicado_detalle(numero_radicado: str, request: Request, db: Session = Depends(get_db)):
    usuario_actual = _requiere_sesion(request, db)
    if not usuario_actual:
        return RedirectResponse("/admin/login", status_code=303)

    radicado = db.query(Radicado).filter(Radicado.numero_radicado == numero_radicado).first()
    if not radicado:
        return RedirectResponse("/admin/radicados?mensaje=Radicado no encontrado.&tipo=error", status_code=303)

    funcionarios = db.query(UsuarioInterno).filter(UsuarioInterno.activo.is_(True)).all()
    return templates.TemplateResponse(
        "admin/radicado_detalle.html",
        _ctx(
            request, usuario_actual, radicado=radicado, estados=ESTADOS_RADICADO,
            funcionarios=funcionarios,
        ),
    )


@router.post("/radicados/{numero_radicado}/estado")
def radicado_cambiar_estado(
    numero_radicado: str, request: Request, db: Session = Depends(get_db),
    estado_nuevo: str = Form(...), comentario: str = Form(""),
    funcionario_asignado_id: str = Form(""), respuesta: str = Form(""),
):
    usuario_actual = _requiere_sesion(request, db)
    if not usuario_actual:
        return RedirectResponse("/admin/login", status_code=303)

    radicado = db.query(Radicado).filter(Radicado.numero_radicado == numero_radicado).first()
    if not radicado:
        return RedirectResponse("/admin/radicados?mensaje=Radicado no encontrado.&tipo=error", status_code=303)

    cambiar_estado_radicado(
        db, radicado, estado_nuevo=estado_nuevo, comentario=comentario or None,
        usuario_interno_id=usuario_actual.id, realizado_por=usuario_actual.nombre_completo,
        funcionario_asignado_id=int(funcionario_asignado_id) if funcionario_asignado_id else None,
        respuesta=respuesta or None,
    )
    registrar_auditoria(
        db, usuario=usuario_actual.correo, accion="CAMBIAR_ESTADO_RADICADO", resultado="EXITOSO",
        entidad="Radicado", entidad_id=radicado.id, ip=ip_del_request(request),
        detalle=f"Nuevo estado: {estado_nuevo}",
    )
    return RedirectResponse(
        f"/admin/radicados/{numero_radicado}?mensaje=Estado actualizado.", status_code=303
    )


# ---------------------------------------------------------------------------
# FACTURACIÓN (el funcionario ya está autenticado; no requiere segundo factor)
# ---------------------------------------------------------------------------

@router.get("/facturacion")
def facturacion(request: Request, db: Session = Depends(get_db), numero_documento: str = ""):
    usuario_actual = _requiere_sesion(request, db)
    if not usuario_actual:
        return RedirectResponse("/admin/login", status_code=303)

    usuario = None
    facturas, cartera, consumos = [], None, []
    if numero_documento:
        usuario = db.query(Usuario).filter(Usuario.numero_documento == numero_documento).first()
        if usuario:
            facturas = db.query(Factura).filter(Factura.usuario_id == usuario.id).order_by(
                Factura.fecha_facturacion.desc()
            ).all()
            cartera = db.query(Cartera).filter(Cartera.usuario_id == usuario.id).first()
            consumos = db.query(Consumo).filter(Consumo.usuario_id == usuario.id).order_by(
                Consumo.periodo.desc()
            ).all()
        registrar_auditoria(
            db, usuario=usuario_actual.correo, accion="CONSULTAR_FACTURACION",
            resultado="EXITOSO" if usuario else "RECHAZADO",
            entidad="Usuario", entidad_id=numero_documento, ip=ip_del_request(request),
        )

    return templates.TemplateResponse(
        "admin/facturacion.html",
        _ctx(
            request, usuario_actual, usuario=usuario, facturas=facturas, cartera=cartera,
            consumos=consumos, numero_documento=numero_documento,
            sinfa_estado=sinfa_service.estado_integracion(),
        ),
    )


# ---------------------------------------------------------------------------
# TARIFAS
# ---------------------------------------------------------------------------

@router.get("/tarifas")
def tarifas_list(request: Request, db: Session = Depends(get_db)):
    usuario_actual = _requiere_sesion(request, db)
    if not usuario_actual:
        return RedirectResponse("/admin/login", status_code=303)
    tarifas = db.query(Tarifa).order_by(Tarifa.servicio_id, Tarifa.concepto).all()
    servicios = db.query(Servicio).all()
    return templates.TemplateResponse(
        "admin/tarifas.html",
        _ctx(
            request, usuario_actual, tarifas=tarifas, servicios=servicios,
            tipos_tarifa=TIPOS_TARIFA, tipos_usuario=TIPOS_USUARIO,
            sinfa_estado=sinfa_service.estado_integracion(),
        ),
    )


@router.post("/tarifas")
def tarifas_crear(
    request: Request, db: Session = Depends(get_db),
    servicio_id: int = Form(...), tipo_usuario: str = Form(...), estrato: str = Form(""),
    concepto: str = Form(...), tipo_tarifa: str = Form(...), valor: str = Form(""),
    unidad: str = Form(""), fuente: str = Form(""),
):
    usuario_actual = _requiere_sesion(request, db)
    if not usuario_actual:
        return RedirectResponse("/admin/login", status_code=303)

    tarifa = Tarifa(
        servicio_id=servicio_id, tipo_usuario=tipo_usuario,
        estrato=int(estrato) if estrato else None, concepto=concepto, tipo_tarifa=tipo_tarifa,
        valor=float(valor) if valor else None, unidad=unidad or None,
        estado="Referencial", fuente=fuente or "Documento de trabajo TRIPLE AAA (referencial)",
    )
    db.add(tarifa)
    db.commit()
    registrar_auditoria(
        db, usuario=usuario_actual.correo, accion="CREAR_TARIFA", resultado="EXITOSO",
        entidad="Tarifa", entidad_id=tarifa.id, ip=ip_del_request(request),
    )
    return RedirectResponse("/admin/tarifas?mensaje=Tarifa registrada como referencial.", status_code=303)


# ---------------------------------------------------------------------------
# INVENTARIO
# ---------------------------------------------------------------------------

@router.get("/inventario")
def inventario_list(request: Request, db: Session = Depends(get_db)):
    usuario_actual = _requiere_sesion(request, db)
    if not usuario_actual:
        return RedirectResponse("/admin/login", status_code=303)
    productos = db.query(Producto).order_by(Producto.categoria, Producto.nombre).all()
    return templates.TemplateResponse(
        "admin/inventario.html",
        _ctx(request, usuario_actual, productos=productos, gbs_estado=gbs_service.estado_integracion()),
    )


@router.post("/inventario/sincronizar")
def inventario_sincronizar(request: Request, db: Session = Depends(get_db)):
    usuario_actual = _requiere_sesion(request, db)
    if not usuario_actual:
        return RedirectResponse("/admin/login", status_code=303)
    resultado = gbs_service.sincronizar_inventario(db)
    registrar_auditoria(
        db, usuario=usuario_actual.correo, accion="SINCRONIZAR_INVENTARIO",
        resultado="EXITOSO" if resultado.ejecutado else "RECHAZADO",
        ip=ip_del_request(request), detalle=resultado.mensaje,
    )
    return RedirectResponse(f"/admin/inventario?mensaje={resultado.mensaje}", status_code=303)


# ---------------------------------------------------------------------------
# CONFIGURACIÓN (parámetros del sistema, funcionarios, estado de integraciones)
# ---------------------------------------------------------------------------

@router.get("/configuracion")
def configuracion(request: Request, db: Session = Depends(get_db)):
    usuario_actual = _requiere_sesion(request, db)
    if not usuario_actual:
        return RedirectResponse("/admin/login", status_code=303)

    parametros = db.query(ParametroSistema).order_by(ParametroSistema.categoria, ParametroSistema.clave).all()
    funcionarios = db.query(UsuarioInterno).all()
    from app.services import chatbot as chatbot_service

    return templates.TemplateResponse(
        "admin/configuracion.html",
        _ctx(
            request, usuario_actual, parametros=parametros, funcionarios=funcionarios,
            roles=ROLES_INTERNOS,
            whatsapp_configurado=settings.whatsapp_configured,
            sinfa_estado=sinfa_service.estado_integracion(),
            gbs_estado=gbs_service.estado_integracion(),
        ),
    )


@router.post("/configuracion/parametro")
def configuracion_parametro(
    request: Request, db: Session = Depends(get_db),
    clave: str = Form(...), valor: str = Form(""), descripcion: str = Form(""),
    categoria: str = Form("general"),
):
    usuario_actual = _requiere_sesion(request, db)
    if not usuario_actual or usuario_actual.rol != "ADMINISTRADOR":
        return RedirectResponse("/admin/login", status_code=303)

    parametro = db.query(ParametroSistema).filter(ParametroSistema.clave == clave).first()
    if parametro:
        parametro.valor = valor or None
        parametro.descripcion = descripcion or parametro.descripcion
    else:
        parametro = ParametroSistema(
            clave=clave, valor=valor or None, descripcion=descripcion or None, categoria=categoria
        )
        db.add(parametro)
    db.commit()
    registrar_auditoria(
        db, usuario=usuario_actual.correo, accion="ACTUALIZAR_PARAMETRO", resultado="EXITOSO",
        entidad="ParametroSistema", entidad_id=clave, ip=ip_del_request(request),
    )
    return RedirectResponse("/admin/configuracion?mensaje=Parámetro actualizado.", status_code=303)


@router.post("/configuracion/funcionario")
def configuracion_crear_funcionario(
    request: Request, db: Session = Depends(get_db),
    nombre_completo: str = Form(...), correo: str = Form(...), telefono: str = Form(""),
    rol: str = Form(...), password: str = Form(...),
):
    usuario_actual = _requiere_sesion(request, db)
    if not usuario_actual or usuario_actual.rol != "ADMINISTRADOR":
        return RedirectResponse("/admin/login", status_code=303)

    if db.query(UsuarioInterno).filter(UsuarioInterno.correo == correo).first():
        return RedirectResponse(
            "/admin/configuracion?mensaje=Ya existe un funcionario con ese correo.&tipo=error", status_code=303
        )

    funcionario = UsuarioInterno(
        nombre_completo=nombre_completo, correo=correo, telefono=telefono or None,
        rol=rol, password_hash=hash_password(password),
    )
    db.add(funcionario)
    db.commit()
    registrar_auditoria(
        db, usuario=usuario_actual.correo, accion="CREAR_FUNCIONARIO", resultado="EXITOSO",
        entidad="UsuarioInterno", entidad_id=funcionario.id, ip=ip_del_request(request),
    )
    return RedirectResponse("/admin/configuracion?mensaje=Funcionario creado.", status_code=303)
