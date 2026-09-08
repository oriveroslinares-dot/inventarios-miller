"""
Carga de datos base (catálogos indispensables) y datos DEMO claramente
identificados como datos de prueba.

- `seed_base`: se ejecuta siempre al iniciar la aplicación. Crea los
  servicios (Acueducto, Alcantarillado, Aseo), el usuario administrador
  inicial y los parámetros del sistema (inicialmente vacíos/pendientes).
- `seed_demo`: solo se ejecuta si `LOAD_DEMO_DATA=true` y todavía no existen
  datos de prueba. Todo registro creado aquí se marca `es_demo=True` para
  que nunca se confunda con información real de TRIPLE AAA.
"""
import logging
from datetime import date, datetime, timedelta

from sqlalchemy.orm import Session

from app.config import settings
from app.models import (
    Servicio, UsuarioInterno, ParametroSistema, Usuario, Factura, Consumo,
    Cartera, Producto, Radicado, Tarifa,
)
from app.security import hash_password
from app.schemas import PQRCreate, DanoCreate
from app.services.radicados import crear_pqr, crear_reporte_dano

logger = logging.getLogger("seed")

SERVICIOS_INICIALES = [
    ("Acueducto", "Suministro de agua potable."),
    ("Alcantarillado", "Recolección y disposición de aguas residuales y pluviales."),
    ("Aseo", "Recolección, transporte y disposición final de residuos sólidos."),
]

PARAMETROS_INICIALES = [
    ("tiempo_respuesta_peticion_dias", None, "Tiempo legal de respuesta a una Petición (pendiente de definir por TRIPLE AAA).", "tiempos_legales"),
    ("tiempo_respuesta_queja_dias", None, "Tiempo legal de respuesta a una Queja (pendiente de definir por TRIPLE AAA).", "tiempos_legales"),
    ("tiempo_respuesta_reclamo_dias", None, "Tiempo legal de respuesta a un Reclamo (pendiente de definir por TRIPLE AAA).", "tiempos_legales"),
    ("tiempo_atencion_dano_urgente_horas", None, "Tiempo objetivo de atención para daños urgentes (pendiente de definir).", "tiempos_legales"),
]


def seed_base(db: Session) -> None:
    if db.query(Servicio).count() == 0:
        for nombre, descripcion in SERVICIOS_INICIALES:
            db.add(Servicio(nombre=nombre, descripcion=descripcion, estado="Activo"))
        db.commit()
        logger.info("Servicios base creados: Acueducto, Alcantarillado, Aseo.")

    if db.query(UsuarioInterno).count() == 0:
        admin_password = settings.SECRET_KEY[:4] + "Admin#2026"
        admin = UsuarioInterno(
            nombre_completo="Administrador General",
            correo="admin@tripleaaacartagenita.gov.co",
            rol="ADMINISTRADOR",
            password_hash=hash_password("Admin#2026"),
        )
        db.add(admin)
        db.commit()
        logger.warning(
            "Se creó el usuario administrador inicial admin@tripleaaacartagenita.gov.co "
            "con la contraseña temporal 'Admin#2026'. CÁMBIELA de inmediato en un entorno real."
        )

    if db.query(ParametroSistema).count() == 0:
        for clave, valor, descripcion, categoria in PARAMETROS_INICIALES:
            db.add(ParametroSistema(clave=clave, valor=valor, descripcion=descripcion, categoria=categoria))
        db.commit()


def seed_demo(db: Session) -> None:
    if not settings.LOAD_DEMO_DATA:
        return
    if db.query(Usuario).filter(Usuario.es_demo.is_(True)).count() > 0:
        return  # ya se cargaron los datos de prueba

    servicios = {s.nombre: s for s in db.query(Servicio).all()}
    acueducto = servicios.get("Acueducto")
    alcantarillado = servicios.get("Alcantarillado")
    aseo = servicios.get("Aseo")

    usuarios_demo = [
        dict(tipo_documento="CC", numero_documento="1000000001", nombre_completo="María Fernanda Torres",
             telefono="3000000001", correo="maria.torres@demo.test", direccion="Cra 5 # 10-20",
             municipio="Cartagenita", barrio="Centro", tipo_usuario="Residencial", estrato=2),
        dict(tipo_documento="CC", numero_documento="1000000002", nombre_completo="Carlos Andrés Pérez",
             telefono="3000000002", correo="carlos.perez@demo.test", direccion="Cll 8 # 3-15",
             municipio="Cartagenita", barrio="La Esperanza", tipo_usuario="Residencial", estrato=3),
        dict(tipo_documento="NIT", numero_documento="900000003", nombre_completo="Comercial El Progreso SAS",
             telefono="3000000003", correo="contacto@elprogreso.demo.test", direccion="Av. Principal # 45-10",
             municipio="Cartagenita", barrio="Zona Comercial", tipo_usuario="Comercial", estrato=None),
        dict(tipo_documento="CC", numero_documento="1000000004", nombre_completo="Luisa Fernanda Gómez",
             telefono="3000000004", correo="luisa.gomez@demo.test", direccion="Cra 12 # 22-33",
             municipio="Cartagenita", barrio="San José", tipo_usuario="Residencial", estrato=1),
        dict(tipo_documento="CC", numero_documento="1000000005", nombre_completo="Jorge Iván Ramírez",
             telefono="3000000005", correo="jorge.ramirez@demo.test", direccion="Cll 15 # 6-40",
             municipio="Cartagenita", barrio="Villa Nueva", tipo_usuario="Residencial", estrato=4),
    ]
    usuarios = []
    for datos in usuarios_demo:
        usuario = Usuario(**datos, es_demo=True)
        db.add(usuario)
        usuarios.append(usuario)
    db.commit()
    for u in usuarios:
        db.refresh(u)

    # --- Facturación demo: algunos con datos completos, otro deliberadamente
    # sin datos para demostrar que el sistema NUNCA inventa información. ---
    hoy = date.today()
    facturas_demo = [
        dict(usuario=usuarios[0], periodo="2026-01", fecha_facturacion=hoy - timedelta(days=20),
             fecha_vencimiento=hoy + timedelta(days=10), valor_total=68500.0, estado="Pendiente"),
        dict(usuario=usuarios[1], periodo="2026-01", fecha_facturacion=hoy - timedelta(days=20),
             fecha_vencimiento=hoy + timedelta(days=10), valor_total=95200.0, estado="Pagada"),
        dict(usuario=usuarios[2], periodo="2026-01", fecha_facturacion=hoy - timedelta(days=20),
             fecha_vencimiento=hoy + timedelta(days=10), valor_total=310000.0, estado="Pendiente"),
        dict(usuario=usuarios[3], periodo=None, fecha_facturacion=None,
             fecha_vencimiento=None, valor_total=None, estado=None),  # Dato faltante intencional
        dict(usuario=usuarios[4], periodo="2026-01", fecha_facturacion=hoy - timedelta(days=20),
             fecha_vencimiento=hoy + timedelta(days=10), valor_total=54300.0, estado="Vencida"),
    ]
    for f in facturas_demo:
        db.add(Factura(
            usuario_id=f["usuario"].id, periodo=f["periodo"], fecha_facturacion=f["fecha_facturacion"],
            fecha_vencimiento=f["fecha_vencimiento"], valor_total=f["valor_total"], estado=f["estado"],
            fuente="SINFA", ultima_sincronizacion=None, es_demo=True,
        ))
        db.add(Cartera(
            usuario_id=f["usuario"].id,
            saldo=f["valor_total"] if f["estado"] == "Pendiente" else (0.0 if f["valor_total"] else None),
            estado="En mora" if f["estado"] == "Vencida" else ("Al día" if f["valor_total"] is not None else None),
            fuente="SINFA", es_demo=True,
        ))
        db.add(Consumo(
            usuario_id=f["usuario"].id, periodo=f["periodo"],
            lectura_anterior=120.0 if f["valor_total"] else None,
            lectura_actual=135.0 if f["valor_total"] else None,
            consumo_m3=15.0 if f["valor_total"] else None,
            fuente="SINFA", es_demo=True,
        ))
    db.commit()

    # --- PQR demo (3) ---
    pqr_demo = [
        PQRCreate(
            tipo_pqr="Petición", asunto="Solicitud de revisión de factura",
            descripcion="El usuario solicita revisión del valor facturado en el último periodo.",
            servicio_id=acueducto.id if acueducto else None, direccion="Cra 5 # 10-20",
            numero_documento=usuarios[0].numero_documento, tipo_documento="CC",
            nombre_completo=usuarios[0].nombre_completo, telefono=usuarios[0].telefono,
            correo=usuarios[0].correo, prioridad="Media", canal_origen="WEB",
        ),
        PQRCreate(
            tipo_pqr="Queja", asunto="Demora en atención telefónica",
            descripcion="El usuario manifiesta inconformidad con los tiempos de espera en atención telefónica.",
            servicio_id=None, direccion="Cll 8 # 3-15",
            numero_documento=usuarios[1].numero_documento, tipo_documento="CC",
            nombre_completo=usuarios[1].nombre_completo, telefono=usuarios[1].telefono,
            correo=usuarios[1].correo, prioridad="Baja", canal_origen="WEB",
        ),
        PQRCreate(
            tipo_pqr="Reclamo", asunto="Cobro de cargo fijo no reconocido",
            descripcion="El usuario reclama por un cargo fijo que no reconoce en su factura.",
            servicio_id=aseo.id if aseo else None, direccion="Av. Principal # 45-10",
            numero_documento=usuarios[2].numero_documento, tipo_documento="NIT",
            nombre_completo=usuarios[2].nombre_completo, telefono=usuarios[2].telefono,
            correo=usuarios[2].correo, prioridad="Alta", canal_origen="WEB",
        ),
    ]
    radicados_pqr = [crear_pqr(db, datos) for datos in pqr_demo]

    # --- Reportes de daños demo (3) ---
    danos_demo = [
        DanoCreate(
            tipo_dano="Fuga de agua", direccion="Cra 12 # 22-33", barrio="San José",
            descripcion="Fuga visible de agua potable sobre la vía pública.",
            servicio_id=acueducto.id if acueducto else None, prioridad="Alta",
            numero_documento=usuarios[3].numero_documento, tipo_documento="CC",
            nombre_completo=usuarios[3].nombre_completo, telefono=usuarios[3].telefono,
            correo=usuarios[3].correo, canal_origen="WEB",
        ),
        DanoCreate(
            tipo_dano="Alcantarillado", direccion="Cll 15 # 6-40", barrio="Villa Nueva",
            descripcion="Obstrucción de alcantarillado que genera rebose en la calle.",
            servicio_id=alcantarillado.id if alcantarillado else None, prioridad="Urgente",
            numero_documento=usuarios[4].numero_documento, tipo_documento="CC",
            nombre_completo=usuarios[4].nombre_completo, telefono=usuarios[4].telefono,
            correo=usuarios[4].correo, canal_origen="WEB",
        ),
        DanoCreate(
            tipo_dano="Problema de aseo", direccion="Centro", barrio="Centro",
            descripcion="No se realizó la recolección de residuos en la ruta habitual.",
            servicio_id=aseo.id if aseo else None, prioridad="Media",
            numero_documento=usuarios[0].numero_documento, tipo_documento="CC",
            nombre_completo=usuarios[0].nombre_completo, telefono=usuarios[0].telefono,
            correo=usuarios[0].correo, canal_origen="WEB",
        ),
    ]
    radicados_dano = [crear_reporte_dano(db, datos) for datos in danos_demo]

    # Marcar todos los radicados demo y agregar historial adicional para
    # simular avance de gestión en algunos casos.
    for r in radicados_pqr + radicados_dano:
        r.es_demo = True
    db.commit()

    from app.services.radicados import cambiar_estado_radicado
    cambiar_estado_radicado(
        db, radicados_pqr[0], estado_nuevo="En proceso",
        comentario="Asignado al área comercial para revisión de factura.",
        usuario_interno_id=None, realizado_por="Sistema (dato de prueba)",
    )
    cambiar_estado_radicado(
        db, radicados_dano[1], estado_nuevo="Asignado",
        comentario="Cuadrilla de alcantarillado asignada para atención en sitio.",
        usuario_interno_id=None, realizado_por="Sistema (dato de prueba)",
    )
    radicados_pqr[0].es_demo = True
    radicados_dano[1].es_demo = True
    db.commit()

    # --- Radicados adicionales para completar 5 (una solicitud genérica) ---
    solicitud = Radicado(
        numero_radicado=_numero_solicitud_demo(db),
        tipo="SOLICITUD", usuario_id=usuarios[1].id,
        servicio_id=acueducto.id if acueducto else None,
        descripcion="Solicitud de certificado de paz y salvo para trámite bancario.",
        estado="Recibido", prioridad="Baja", canal_origen="WEB", es_demo=True,
    )
    db.add(solicitud)
    db.commit()
    db.refresh(solicitud)
    from app.services.radicados import registrar_historial
    registrar_historial(db, solicitud, estado_nuevo="Recibido", comentario="Solicitud de prueba creada.")
    db.commit()

    # --- Inventario demo ---
    productos_demo = [
        dict(codigo="MED-001", nombre="Medidor de agua 1/2\"", categoria="Medidores y accesorios",
             unidad="unidad", existencia=42, costo_promedio=185000.0, stock_minimo=10, punto_reorden=15,
             ubicacion="Bodega principal", proveedor="Proveedor Demo SAS"),
        dict(codigo="TUB-010", nombre="Tubería PVC 4 pulgadas x 6m", categoria="Tuberías",
             unidad="unidad", existencia=15, costo_promedio=98000.0, stock_minimo=5, punto_reorden=8,
             ubicacion="Bodega principal", proveedor="Proveedor Demo SAS"),
        dict(codigo="QUI-002", nombre="Hipoclorito de sodio (galón)", categoria="Químicos para tratamiento",
             unidad="galón", existencia=8, costo_promedio=32000.0, stock_minimo=10, punto_reorden=12,
             ubicacion="Planta de tratamiento", proveedor="Proveedor Demo SAS"),
        dict(codigo="CON-005", nombre="Contenedor de residuos 240L", categoria="Contenedores",
             unidad="unidad", existencia=None, costo_promedio=None, stock_minimo=5, punto_reorden=8,
             ubicacion="Bodega de aseo", proveedor=None),  # Dato faltante intencional (pendiente GBS)
        dict(codigo="REP-020", nombre="Repuesto de bomba centrífuga", categoria="Repuestos de bombeo y mantenimiento",
             unidad="unidad", existencia=6, costo_promedio=450000.0, stock_minimo=3, punto_reorden=4,
             ubicacion="Bodega de mantenimiento", proveedor="Proveedor Demo SAS"),
    ]
    for p in productos_demo:
        db.add(Producto(**p, fuente="GBS", ultima_sincronizacion=None, es_demo=True))
    db.commit()

    # --- Tarifas demo (referenciales, no confirmadas en SINFA) ---
    if acueducto:
        for tipo_usuario, estrato in [("Residencial", 1), ("Residencial", 2), ("Residencial", 3), ("Comercial", None)]:
            db.add(Tarifa(
                servicio_id=acueducto.id, tipo_usuario=tipo_usuario, estrato=estrato,
                concepto="Cargo fijo acueducto", tipo_tarifa="Cargo fijo", valor=None, unidad="mes",
                estado="Referencial", fuente="Documento de trabajo TRIPLE AAA (pendiente de validar en SINFA)",
            ))
        db.commit()

    logger.warning(
        "DATOS DE PRUEBA cargados: 5 usuarios, 5 facturas, 3 PQR, 3 reportes de daño, "
        "1 solicitud adicional (5 radicados en total), historial de trazabilidad y 5 productos "
        "de inventario. Todos marcados es_demo=True para no confundirse con información real."
    )


def _numero_solicitud_demo(db: Session) -> str:
    from app.services.radicados import generar_numero_radicado
    return generar_numero_radicado(db, "SOLICITUD")
