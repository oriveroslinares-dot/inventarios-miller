"""
Servicio central de radicados.

Responsable de:
- Generar números de radicado únicos y consecutivos por tipo y año
  (ej: PQR-2026-000001, DANO-2026-000001, SOL-2026-000001).
- Registrar automáticamente el historial de cada cambio de estado.
- Buscar o crear el usuario (ciudadano) asociado a una PQR/daño/solicitud.
"""
from datetime import datetime, date
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models import (
    Radicado, RadicadoCounter, HistorialRadicado, Usuario, PQR, ReporteDano,
    PREFIJOS_RADICADO,
)


def _siguiente_consecutivo(db: Session, tipo: str, anio: int) -> int:
    """Incrementa de forma atómica el contador de un tipo+año y lo retorna.

    En motores que soportan bloqueo de fila (Postgres) se usa SELECT ... FOR
    UPDATE para evitar condiciones de carrera entre procesos concurrentes;
    SQLite no soporta ese bloqueo pero solo permite un escritor a la vez.
    """
    query = db.query(RadicadoCounter).filter(
        RadicadoCounter.tipo == tipo, RadicadoCounter.anio == anio
    )
    if db.bind.dialect.name != "sqlite":
        query = query.with_for_update()
    contador = query.first()
    if contador is None:
        contador = RadicadoCounter(tipo=tipo, anio=anio, ultimo_numero=0)
        db.add(contador)
        db.flush()
    contador.ultimo_numero += 1
    db.flush()
    return contador.ultimo_numero


def generar_numero_radicado(db: Session, tipo: str) -> str:
    """
    Genera un número de radicado único para el tipo dado.

    Garantiza unicidad de dos formas:
    1. Un contador consecutivo por (tipo, año).
    2. Reintento ante una eventual colisión, protegido por la restricción
       UNIQUE de la columna `numero_radicado` en la base de datos.
    """
    prefijo = PREFIJOS_RADICADO[tipo]
    anio = datetime.utcnow().year

    for _intento in range(5):
        consecutivo = _siguiente_consecutivo(db, tipo, anio)
        numero = f"{prefijo}-{anio}-{consecutivo:06d}"
        existe = db.query(Radicado).filter(Radicado.numero_radicado == numero).first()
        if not existe:
            return numero
    raise RuntimeError("No fue posible generar un número de radicado único tras varios intentos.")


def obtener_o_crear_usuario(
    db: Session,
    numero_documento: str,
    tipo_documento: str = "CC",
    nombre_completo: str | None = None,
    telefono: str | None = None,
    correo: str | None = None,
) -> Usuario:
    usuario = db.query(Usuario).filter(Usuario.numero_documento == numero_documento).first()
    if usuario:
        cambiado = False
        if telefono and usuario.telefono != telefono:
            usuario.telefono = telefono
            cambiado = True
        if correo and usuario.correo != correo:
            usuario.correo = correo
            cambiado = True
        if cambiado:
            db.flush()
        return usuario

    usuario = Usuario(
        tipo_documento=tipo_documento,
        numero_documento=numero_documento,
        nombre_completo=nombre_completo or "Usuario sin nombre registrado",
        telefono=telefono,
        correo=correo,
    )
    db.add(usuario)
    db.flush()
    return usuario


def registrar_historial(
    db: Session,
    radicado: Radicado,
    estado_nuevo: str,
    comentario: str | None = None,
    estado_anterior: str | None = None,
    usuario_interno_id: int | None = None,
    realizado_por: str = "Sistema",
) -> HistorialRadicado:
    ahora = datetime.utcnow()
    historial = HistorialRadicado(
        radicado_id=radicado.id,
        estado_anterior=estado_anterior,
        estado_nuevo=estado_nuevo,
        comentario=comentario,
        usuario_interno_id=usuario_interno_id,
        realizado_por=realizado_por,
        fecha=ahora.date(),
        hora=ahora.time(),
        fecha_hora=ahora,
    )
    db.add(historial)
    db.flush()
    return historial


def crear_pqr(db: Session, datos) -> Radicado:
    """Crea una PQR: genera el radicado, el registro PQR y el historial inicial."""
    usuario = obtener_o_crear_usuario(
        db,
        numero_documento=datos.numero_documento,
        tipo_documento=datos.tipo_documento,
        nombre_completo=datos.nombre_completo,
        telefono=datos.telefono,
        correo=datos.correo,
    )
    numero_radicado = generar_numero_radicado(db, "PQR")

    radicado = Radicado(
        numero_radicado=numero_radicado,
        tipo="PQR",
        usuario_id=usuario.id,
        servicio_id=datos.servicio_id,
        descripcion=datos.descripcion,
        estado="Recibido",
        prioridad=datos.prioridad,
        canal_origen=datos.canal_origen,
    )
    db.add(radicado)
    db.flush()

    pqr = PQR(radicado_id=radicado.id, tipo_pqr=datos.tipo_pqr, asunto=datos.asunto)
    db.add(pqr)
    db.flush()

    registrar_historial(
        db, radicado, estado_nuevo="Recibido",
        comentario="PQR radicada por el ciudadano.",
        realizado_por="Sistema",
    )
    db.commit()
    db.refresh(radicado)
    return radicado


def crear_reporte_dano(db: Session, datos) -> Radicado:
    """Crea un reporte de daño: genera el radicado, el registro de daño y el historial inicial."""
    usuario = obtener_o_crear_usuario(
        db,
        numero_documento=datos.numero_documento,
        tipo_documento=datos.tipo_documento,
        nombre_completo=datos.nombre_completo,
        telefono=datos.telefono,
        correo=datos.correo,
    )
    numero_radicado = generar_numero_radicado(db, "DANO")

    radicado = Radicado(
        numero_radicado=numero_radicado,
        tipo="DANO",
        usuario_id=usuario.id,
        servicio_id=datos.servicio_id,
        descripcion=datos.descripcion,
        estado="Recibido",
        prioridad=datos.prioridad,
        canal_origen=datos.canal_origen,
    )
    db.add(radicado)
    db.flush()

    dano = ReporteDano(
        radicado_id=radicado.id,
        tipo_dano=datos.tipo_dano,
        direccion=datos.direccion,
        barrio=datos.barrio,
        latitud=datos.latitud,
        longitud=datos.longitud,
    )
    db.add(dano)
    db.flush()

    registrar_historial(
        db, radicado, estado_nuevo="Recibido",
        comentario="Reporte de daño recibido.",
        realizado_por="Sistema",
    )
    db.commit()
    db.refresh(radicado)
    return radicado


def cambiar_estado_radicado(
    db: Session,
    radicado: Radicado,
    estado_nuevo: str,
    comentario: str | None,
    usuario_interno_id: int | None,
    realizado_por: str,
    funcionario_asignado_id: int | None = None,
    respuesta: str | None = None,
) -> Radicado:
    estado_anterior = radicado.estado
    radicado.estado = estado_nuevo
    if funcionario_asignado_id is not None:
        radicado.funcionario_asignado_id = funcionario_asignado_id
    if respuesta is not None:
        radicado.respuesta = respuesta
    if estado_nuevo in ("Resuelto", "Cerrado", "Rechazado"):
        radicado.fecha_cierre = datetime.utcnow()

    registrar_historial(
        db, radicado,
        estado_nuevo=estado_nuevo,
        estado_anterior=estado_anterior,
        comentario=comentario,
        usuario_interno_id=usuario_interno_id,
        realizado_por=realizado_por,
    )
    db.commit()
    db.refresh(radicado)
    return radicado
