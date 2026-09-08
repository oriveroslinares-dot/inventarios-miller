"""
Modelos de base de datos (SQLAlchemy) para la plataforma de
TRIPLE AAA DE CARTAGENITA.

Convenciones:
- Las fechas se guardan en UTC.
- Campos monetarios / de medición que provienen de sistemas externos
  (SINFA, GBS) se dejan NULOS cuando el dato no existe todavía. La capa de
  presentación es responsable de mostrar "Dato faltante" en ese caso; el
  backend NUNCA inventa valores por defecto distintos de NULL.
"""
from datetime import datetime, date, time

from sqlalchemy import (
    String, Integer, Float, Boolean, ForeignKey, Text, DateTime, Date, Time,
    UniqueConstraint, Index
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


def utcnow() -> datetime:
    return datetime.utcnow()


# ---------------------------------------------------------------------------
# Catálogos / constantes de dominio (documentadas aquí; validadas en schemas.py)
# ---------------------------------------------------------------------------

TIPOS_USUARIO = ["Residencial", "Comercial", "Industrial", "Oficial", "Especial"]
ESTADOS_USUARIO = ["Activo", "Inactivo"]

TIPOS_RADICADO = ["PQR", "DANO", "SOLICITUD"]
ESTADOS_RADICADO = [
    "Recibido",
    "En revisión",
    "Asignado",
    "En proceso",
    "Pendiente de información",
    "Resuelto",
    "Cerrado",
    "Rechazado",
]
PRIORIDADES = ["Baja", "Media", "Alta", "Urgente"]

TIPOS_PQR = ["Petición", "Queja", "Reclamo", "Solicitud"]

TIPOS_DANO = [
    "Fuga de agua",
    "Daño de tubería",
    "Daño de medidor",
    "Alcantarillado",
    "Rebose",
    "Problema de aseo",
    "Otro",
]

ROLES_INTERNOS = ["ADMINISTRADOR", "FUNCIONARIO", "SUPERVISOR", "CONSULTA"]

TIPOS_TARIFA = [
    "Cargo fijo",
    "Consumo básico",
    "Consumo complementario",
    "Consumo suntuario",
]

PREFIJOS_RADICADO = {
    "PQR": "PQR",
    "DANO": "DANO",
    "SOLICITUD": "SOL",
}


# ---------------------------------------------------------------------------
# USUARIOS (ciudadanos / clientes del servicio)
# ---------------------------------------------------------------------------

class Usuario(Base):
    __tablename__ = "usuarios"

    id: Mapped[int] = mapped_column(primary_key=True)
    tipo_documento: Mapped[str] = mapped_column(String(10))  # CC, NIT, CE, TI, PA
    numero_documento: Mapped[str] = mapped_column(String(30), unique=True, index=True)
    nombre_completo: Mapped[str] = mapped_column(String(200))
    telefono: Mapped[str | None] = mapped_column(String(30), index=True)
    correo: Mapped[str | None] = mapped_column(String(150))
    direccion: Mapped[str | None] = mapped_column(String(250))
    municipio: Mapped[str | None] = mapped_column(String(120))
    barrio: Mapped[str | None] = mapped_column(String(120))
    tipo_usuario: Mapped[str] = mapped_column(String(30), default="Residencial")
    estrato: Mapped[int | None] = mapped_column(Integer)
    estado: Mapped[str] = mapped_column(String(20), default="Activo")
    fecha_registro: Mapped[datetime] = mapped_column(DateTime, default=utcnow)
    fecha_actualizacion: Mapped[datetime] = mapped_column(
        DateTime, default=utcnow, onupdate=utcnow
    )
    es_demo: Mapped[bool] = mapped_column(Boolean, default=False)

    radicados: Mapped[list["Radicado"]] = relationship(back_populates="usuario")


# ---------------------------------------------------------------------------
# USUARIOS INTERNOS (funcionarios / administradores del sistema)
# ---------------------------------------------------------------------------

class UsuarioInterno(Base):
    __tablename__ = "usuarios_internos"

    id: Mapped[int] = mapped_column(primary_key=True)
    nombre_completo: Mapped[str] = mapped_column(String(200))
    correo: Mapped[str] = mapped_column(String(150), unique=True, index=True)
    telefono: Mapped[str | None] = mapped_column(String(30))
    rol: Mapped[str] = mapped_column(String(30), default="CONSULTA")
    password_hash: Mapped[str] = mapped_column(String(255))
    activo: Mapped[bool] = mapped_column(Boolean, default=True)
    fecha_creacion: Mapped[datetime] = mapped_column(DateTime, default=utcnow)


# ---------------------------------------------------------------------------
# SERVICIOS
# ---------------------------------------------------------------------------

class Servicio(Base):
    __tablename__ = "servicios"

    id: Mapped[int] = mapped_column(primary_key=True)
    nombre: Mapped[str] = mapped_column(String(50), unique=True)  # Acueducto, Alcantarillado, Aseo
    descripcion: Mapped[str | None] = mapped_column(Text)
    estado: Mapped[str] = mapped_column(String(20), default="Activo")


# ---------------------------------------------------------------------------
# CONTADOR DE RADICADOS (soporte para numeración única y consecutiva)
# ---------------------------------------------------------------------------

class RadicadoCounter(Base):
    __tablename__ = "radicado_counters"
    __table_args__ = (UniqueConstraint("tipo", "anio", name="uq_counter_tipo_anio"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    tipo: Mapped[str] = mapped_column(String(20))
    anio: Mapped[int] = mapped_column(Integer)
    ultimo_numero: Mapped[int] = mapped_column(Integer, default=0)


# ---------------------------------------------------------------------------
# RADICADOS (entidad transversal: PQR, Daños, Solicitudes)
# ---------------------------------------------------------------------------

class Radicado(Base):
    __tablename__ = "radicados"

    id: Mapped[int] = mapped_column(primary_key=True)
    numero_radicado: Mapped[str] = mapped_column(String(30), unique=True, index=True)
    tipo: Mapped[str] = mapped_column(String(20))  # PQR | DANO | SOLICITUD
    usuario_id: Mapped[int | None] = mapped_column(ForeignKey("usuarios.id"))
    servicio_id: Mapped[int | None] = mapped_column(ForeignKey("servicios.id"))
    descripcion: Mapped[str] = mapped_column(Text)
    estado: Mapped[str] = mapped_column(String(40), default="Recibido")
    prioridad: Mapped[str] = mapped_column(String(20), default="Media")
    fecha_creacion: Mapped[datetime] = mapped_column(DateTime, default=utcnow, index=True)
    fecha_actualizacion: Mapped[datetime] = mapped_column(
        DateTime, default=utcnow, onupdate=utcnow
    )
    fecha_cierre: Mapped[datetime | None] = mapped_column(DateTime)
    funcionario_asignado_id: Mapped[int | None] = mapped_column(ForeignKey("usuarios_internos.id"))
    respuesta: Mapped[str | None] = mapped_column(Text)

    # canal de origen: WEB, WHATSAPP, TELEFONO, PRESENCIAL (preparado para el chatbot)
    canal_origen: Mapped[str] = mapped_column(String(20), default="WEB")
    es_demo: Mapped[bool] = mapped_column(Boolean, default=False)

    usuario: Mapped["Usuario | None"] = relationship(back_populates="radicados")
    servicio: Mapped["Servicio | None"] = relationship()
    funcionario_asignado: Mapped["UsuarioInterno | None"] = relationship()

    pqr: Mapped["PQR | None"] = relationship(back_populates="radicado", uselist=False)
    reporte_dano: Mapped["ReporteDano | None"] = relationship(back_populates="radicado", uselist=False)
    historial: Mapped[list["HistorialRadicado"]] = relationship(
        back_populates="radicado", order_by="HistorialRadicado.fecha_hora"
    )
    evidencias: Mapped[list["Evidencia"]] = relationship(back_populates="radicado")


class PQR(Base):
    __tablename__ = "pqr"

    id: Mapped[int] = mapped_column(primary_key=True)
    radicado_id: Mapped[int] = mapped_column(ForeignKey("radicados.id"), unique=True)
    tipo_pqr: Mapped[str] = mapped_column(String(20))  # Petición, Queja, Reclamo, Solicitud
    asunto: Mapped[str] = mapped_column(String(250))

    radicado: Mapped["Radicado"] = relationship(back_populates="pqr")


class ReporteDano(Base):
    __tablename__ = "reportes_danos"

    id: Mapped[int] = mapped_column(primary_key=True)
    radicado_id: Mapped[int] = mapped_column(ForeignKey("radicados.id"), unique=True)
    tipo_dano: Mapped[str] = mapped_column(String(50))
    direccion: Mapped[str] = mapped_column(String(250))
    barrio: Mapped[str | None] = mapped_column(String(120))
    fecha_hora_dano: Mapped[datetime] = mapped_column(DateTime, default=utcnow)
    latitud: Mapped[float | None] = mapped_column(Float)
    longitud: Mapped[float | None] = mapped_column(Float)

    radicado: Mapped["Radicado"] = relationship(back_populates="reporte_dano")


# ---------------------------------------------------------------------------
# HISTORIAL (trazabilidad de cada radicado)
# ---------------------------------------------------------------------------

class HistorialRadicado(Base):
    __tablename__ = "historial_radicados"

    id: Mapped[int] = mapped_column(primary_key=True)
    radicado_id: Mapped[int] = mapped_column(ForeignKey("radicados.id"), index=True)
    estado_anterior: Mapped[str | None] = mapped_column(String(40))
    estado_nuevo: Mapped[str] = mapped_column(String(40))
    comentario: Mapped[str | None] = mapped_column(Text)
    usuario_interno_id: Mapped[int | None] = mapped_column(ForeignKey("usuarios_internos.id"))
    realizado_por: Mapped[str] = mapped_column(String(100), default="Sistema")
    fecha: Mapped[date] = mapped_column(Date, default=date.today)
    hora: Mapped[time] = mapped_column(Time, default=lambda: datetime.utcnow().time())
    fecha_hora: Mapped[datetime] = mapped_column(DateTime, default=utcnow, index=True)

    radicado: Mapped["Radicado"] = relationship(back_populates="historial")
    usuario_interno: Mapped["UsuarioInterno | None"] = relationship()


# ---------------------------------------------------------------------------
# EVIDENCIAS (archivos adjuntos a un radicado)
# ---------------------------------------------------------------------------

class Evidencia(Base):
    __tablename__ = "evidencias"

    id: Mapped[int] = mapped_column(primary_key=True)
    radicado_id: Mapped[int] = mapped_column(ForeignKey("radicados.id"), index=True)
    tipo_archivo: Mapped[str] = mapped_column(String(50))
    nombre_archivo: Mapped[str] = mapped_column(String(255))
    ruta_archivo: Mapped[str] = mapped_column(String(500))
    tamano_bytes: Mapped[int | None] = mapped_column(Integer)
    fecha_carga: Mapped[datetime] = mapped_column(DateTime, default=utcnow)

    radicado: Mapped["Radicado"] = relationship(back_populates="evidencias")


# ---------------------------------------------------------------------------
# FACTURACIÓN (estructura preparada para ser alimentada desde SINFA)
# ---------------------------------------------------------------------------

class Factura(Base):
    __tablename__ = "facturas"

    id: Mapped[int] = mapped_column(primary_key=True)
    usuario_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"), index=True)
    periodo: Mapped[str | None] = mapped_column(String(20))  # ej: 2026-01
    fecha_facturacion: Mapped[date | None] = mapped_column(Date)
    fecha_vencimiento: Mapped[date | None] = mapped_column(Date)
    valor_total: Mapped[float | None] = mapped_column(Float)  # NULL => dato faltante
    estado: Mapped[str | None] = mapped_column(String(30))  # Pendiente, Pagada, Vencida
    fuente: Mapped[str] = mapped_column(String(20), default="SINFA")
    ultima_sincronizacion: Mapped[datetime | None] = mapped_column(DateTime)
    es_demo: Mapped[bool] = mapped_column(Boolean, default=False)


class Consumo(Base):
    __tablename__ = "consumos"

    id: Mapped[int] = mapped_column(primary_key=True)
    usuario_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"), index=True)
    periodo: Mapped[str | None] = mapped_column(String(20))
    lectura_anterior: Mapped[float | None] = mapped_column(Float)
    lectura_actual: Mapped[float | None] = mapped_column(Float)
    consumo_m3: Mapped[float | None] = mapped_column(Float)
    fuente: Mapped[str] = mapped_column(String(20), default="SINFA")
    ultima_sincronizacion: Mapped[datetime | None] = mapped_column(DateTime)
    es_demo: Mapped[bool] = mapped_column(Boolean, default=False)


class Pago(Base):
    __tablename__ = "pagos"

    id: Mapped[int] = mapped_column(primary_key=True)
    usuario_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"), index=True)
    factura_id: Mapped[int | None] = mapped_column(ForeignKey("facturas.id"))
    fecha: Mapped[date | None] = mapped_column(Date)
    valor: Mapped[float | None] = mapped_column(Float)
    medio_pago: Mapped[str | None] = mapped_column(String(50))
    fuente: Mapped[str] = mapped_column(String(20), default="SINFA")
    es_demo: Mapped[bool] = mapped_column(Boolean, default=False)


class Cartera(Base):
    __tablename__ = "cartera"

    id: Mapped[int] = mapped_column(primary_key=True)
    usuario_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"), unique=True, index=True)
    saldo: Mapped[float | None] = mapped_column(Float)  # NULL => dato faltante
    estado: Mapped[str | None] = mapped_column(String(30))  # Al día, En mora, Sin información
    fuente: Mapped[str] = mapped_column(String(20), default="SINFA")
    ultima_sincronizacion: Mapped[datetime | None] = mapped_column(DateTime)
    es_demo: Mapped[bool] = mapped_column(Boolean, default=False)


# ---------------------------------------------------------------------------
# TARIFAS (parametrizables desde el panel administrativo)
# ---------------------------------------------------------------------------

class Tarifa(Base):
    __tablename__ = "tarifas"

    id: Mapped[int] = mapped_column(primary_key=True)
    servicio_id: Mapped[int] = mapped_column(ForeignKey("servicios.id"))
    tipo_usuario: Mapped[str] = mapped_column(String(30))
    estrato: Mapped[int | None] = mapped_column(Integer)
    concepto: Mapped[str] = mapped_column(String(150))
    tipo_tarifa: Mapped[str] = mapped_column(String(50))
    valor: Mapped[float | None] = mapped_column(Float)  # NULL => "Dato faltante – pendiente de validación en SINFA"
    unidad: Mapped[str | None] = mapped_column(String(30))
    fecha_vigencia: Mapped[date | None] = mapped_column(Date)
    estado: Mapped[str] = mapped_column(String(30), default="Referencial")  # Referencial | Confirmada en SINFA
    fuente: Mapped[str | None] = mapped_column(String(150))
    fecha_actualizacion: Mapped[datetime] = mapped_column(DateTime, default=utcnow, onupdate=utcnow)

    servicio: Mapped["Servicio"] = relationship()


# ---------------------------------------------------------------------------
# INVENTARIO (estructura preparada para GBS)
# ---------------------------------------------------------------------------

class Producto(Base):
    __tablename__ = "productos_inventario"

    id: Mapped[int] = mapped_column(primary_key=True)
    codigo: Mapped[str] = mapped_column(String(50), unique=True)
    nombre: Mapped[str] = mapped_column(String(200))
    categoria: Mapped[str] = mapped_column(String(100))
    unidad: Mapped[str | None] = mapped_column(String(30))
    existencia: Mapped[float | None] = mapped_column(Float)  # NULL => dato faltante
    costo_promedio: Mapped[float | None] = mapped_column(Float)
    stock_minimo: Mapped[float | None] = mapped_column(Float)
    punto_reorden: Mapped[float | None] = mapped_column(Float)
    ubicacion: Mapped[str | None] = mapped_column(String(150))
    proveedor: Mapped[str | None] = mapped_column(String(200))
    fuente: Mapped[str] = mapped_column(String(20), default="GBS")
    ultima_sincronizacion: Mapped[datetime | None] = mapped_column(DateTime)
    fecha_actualizacion: Mapped[datetime] = mapped_column(DateTime, default=utcnow, onupdate=utcnow)
    es_demo: Mapped[bool] = mapped_column(Boolean, default=False)


# ---------------------------------------------------------------------------
# PARÁMETROS DEL SISTEMA (tiempos legales, textos, configuración general)
# ---------------------------------------------------------------------------

class ParametroSistema(Base):
    __tablename__ = "parametros_sistema"

    id: Mapped[int] = mapped_column(primary_key=True)
    clave: Mapped[str] = mapped_column(String(100), unique=True)
    valor: Mapped[str | None] = mapped_column(Text)  # NULL => pendiente de configurar
    descripcion: Mapped[str | None] = mapped_column(Text)
    categoria: Mapped[str] = mapped_column(String(50), default="general")
    fecha_actualizacion: Mapped[datetime] = mapped_column(DateTime, default=utcnow, onupdate=utcnow)


# ---------------------------------------------------------------------------
# SEGURIDAD / AUDITORÍA
# ---------------------------------------------------------------------------

class RegistroAuditoria(Base):
    __tablename__ = "auditoria"

    id: Mapped[int] = mapped_column(primary_key=True)
    fecha_hora: Mapped[datetime] = mapped_column(DateTime, default=utcnow, index=True)
    usuario: Mapped[str] = mapped_column(String(150))  # correo interno, "anonimo" o "sistema"
    accion: Mapped[str] = mapped_column(String(100))
    entidad: Mapped[str | None] = mapped_column(String(50))
    entidad_id: Mapped[str | None] = mapped_column(String(50))
    ip: Mapped[str | None] = mapped_column(String(64))
    resultado: Mapped[str] = mapped_column(String(20))  # EXITOSO | RECHAZADO | ERROR
    detalle: Mapped[str | None] = mapped_column(Text)


# ---------------------------------------------------------------------------
# CHATBOT / WHATSAPP (preparación para integración con Meta Cloud API)
# ---------------------------------------------------------------------------

class SesionChatbot(Base):
    __tablename__ = "sesiones_chatbot"

    id: Mapped[int] = mapped_column(primary_key=True)
    telefono: Mapped[str] = mapped_column(String(30), unique=True, index=True)
    estado_conversacion: Mapped[str] = mapped_column(String(50), default="MENU_PRINCIPAL")
    contexto_json: Mapped[str | None] = mapped_column(Text)  # datos temporales del flujo, en JSON
    usuario_id: Mapped[int | None] = mapped_column(ForeignKey("usuarios.id"))
    fecha_actualizacion: Mapped[datetime] = mapped_column(DateTime, default=utcnow, onupdate=utcnow)


class MensajeWhatsApp(Base):
    __tablename__ = "mensajes_whatsapp"

    id: Mapped[int] = mapped_column(primary_key=True)
    telefono: Mapped[str] = mapped_column(String(30), index=True)
    direccion: Mapped[str] = mapped_column(String(10))  # entrante | saliente
    contenido: Mapped[str] = mapped_column(Text)
    tipo_mensaje: Mapped[str] = mapped_column(String(20), default="texto")
    wa_message_id: Mapped[str | None] = mapped_column(String(100))
    fecha_hora: Mapped[datetime] = mapped_column(DateTime, default=utcnow, index=True)
