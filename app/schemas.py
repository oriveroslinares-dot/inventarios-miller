"""Schemas Pydantic para request/response de la API REST."""
from datetime import datetime, date
from typing import Optional, Any

from pydantic import BaseModel, Field, EmailStr, field_validator

from app.models import (
    TIPOS_USUARIO, TIPOS_RADICADO, ESTADOS_RADICADO, PRIORIDADES,
    TIPOS_PQR, TIPOS_DANO, ROLES_INTERNOS, TIPOS_TARIFA,
)

DATO_FALTANTE = "Dato faltante"
DATO_FALTANTE_SINFA = "Dato faltante – pendiente de validación en SINFA."
DATO_FALTANTE_GBS = "Dato faltante – pendiente de sincronización con GBS."


def _validar_opcion(valor: str, opciones: list[str], campo: str) -> str:
    if valor not in opciones:
        raise ValueError(f"{campo} inválido. Opciones válidas: {', '.join(opciones)}")
    return valor


# ---------------------------------------------------------------------------
# USUARIOS
# ---------------------------------------------------------------------------

class UsuarioCreate(BaseModel):
    tipo_documento: str = Field(..., examples=["CC"])
    numero_documento: str
    nombre_completo: str
    telefono: Optional[str] = None
    correo: Optional[str] = None
    direccion: Optional[str] = None
    municipio: Optional[str] = None
    barrio: Optional[str] = None
    tipo_usuario: str = "Residencial"
    estrato: Optional[int] = None

    @field_validator("tipo_usuario")
    @classmethod
    def check_tipo_usuario(cls, v):
        return _validar_opcion(v, TIPOS_USUARIO, "tipo_usuario")


class UsuarioOut(BaseModel):
    id: int
    tipo_documento: str
    numero_documento: str
    nombre_completo: str
    telefono: Optional[str]
    correo: Optional[str]
    direccion: Optional[str]
    municipio: Optional[str]
    barrio: Optional[str]
    tipo_usuario: str
    estrato: Optional[int]
    estado: str
    fecha_registro: datetime
    fecha_actualizacion: datetime
    es_demo: bool

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# RADICADOS
# ---------------------------------------------------------------------------

class HistorialOut(BaseModel):
    id: int
    estado_anterior: Optional[str]
    estado_nuevo: str
    comentario: Optional[str]
    realizado_por: str
    fecha: date
    hora: Any
    fecha_hora: datetime

    model_config = {"from_attributes": True}


class EvidenciaOut(BaseModel):
    id: int
    tipo_archivo: str
    nombre_archivo: str
    fecha_carga: datetime

    model_config = {"from_attributes": True}


class RadicadoOut(BaseModel):
    id: int
    numero_radicado: str
    tipo: str
    usuario_id: Optional[int]
    servicio_id: Optional[int]
    descripcion: str
    estado: str
    prioridad: str
    fecha_creacion: datetime
    fecha_actualizacion: datetime
    fecha_cierre: Optional[datetime]
    funcionario_asignado_id: Optional[int]
    respuesta: Optional[str]
    canal_origen: str
    es_demo: bool

    model_config = {"from_attributes": True}


class RadicadoDetalleOut(RadicadoOut):
    historial: list[HistorialOut] = []
    evidencias: list[EvidenciaOut] = []


class ConsultaRadicadoIn(BaseModel):
    numero_radicado: str
    numero_documento: Optional[str] = None  # validación adicional opcional


class CambioEstadoIn(BaseModel):
    estado_nuevo: str
    comentario: Optional[str] = None
    funcionario_asignado_id: Optional[int] = None
    respuesta: Optional[str] = None

    @field_validator("estado_nuevo")
    @classmethod
    def check_estado(cls, v):
        return _validar_opcion(v, ESTADOS_RADICADO, "estado_nuevo")


# ---------------------------------------------------------------------------
# PQR
# ---------------------------------------------------------------------------

class PQRCreate(BaseModel):
    tipo_pqr: str
    asunto: str
    descripcion: str
    servicio_id: Optional[int] = None
    direccion: Optional[str] = None
    prioridad: str = "Media"

    # Identificación del usuario (ciudadano). Si no existe, se puede crear.
    numero_documento: str
    tipo_documento: str = "CC"
    nombre_completo: Optional[str] = None
    telefono: Optional[str] = None
    correo: Optional[str] = None

    canal_origen: str = "WEB"

    @field_validator("tipo_pqr")
    @classmethod
    def check_tipo_pqr(cls, v):
        return _validar_opcion(v, TIPOS_PQR, "tipo_pqr")

    @field_validator("prioridad")
    @classmethod
    def check_prioridad(cls, v):
        return _validar_opcion(v, PRIORIDADES, "prioridad")


# ---------------------------------------------------------------------------
# DAÑOS
# ---------------------------------------------------------------------------

class DanoCreate(BaseModel):
    tipo_dano: str
    direccion: str
    barrio: Optional[str] = None
    descripcion: str
    servicio_id: Optional[int] = None
    latitud: Optional[float] = None
    longitud: Optional[float] = None
    prioridad: str = "Media"

    numero_documento: str
    tipo_documento: str = "CC"
    nombre_completo: Optional[str] = None
    telefono: Optional[str] = None
    correo: Optional[str] = None

    canal_origen: str = "WEB"

    @field_validator("tipo_dano")
    @classmethod
    def check_tipo_dano(cls, v):
        return _validar_opcion(v, TIPOS_DANO, "tipo_dano")

    @field_validator("prioridad")
    @classmethod
    def check_prioridad(cls, v):
        return _validar_opcion(v, PRIORIDADES, "prioridad")


# ---------------------------------------------------------------------------
# FACTURACIÓN
# ---------------------------------------------------------------------------

class FacturaOut(BaseModel):
    id: int
    periodo: Optional[str]
    fecha_facturacion: Optional[date]
    fecha_vencimiento: Optional[date]
    valor_total: Optional[float]
    estado: Optional[str]
    fuente: str
    ultima_sincronizacion: Optional[datetime]

    model_config = {"from_attributes": True}


class CarteraOut(BaseModel):
    saldo: Optional[float]
    estado: Optional[str]
    fuente: str
    ultima_sincronizacion: Optional[datetime]

    model_config = {"from_attributes": True}


class ConsumoOut(BaseModel):
    periodo: Optional[str]
    lectura_anterior: Optional[float]
    lectura_actual: Optional[float]
    consumo_m3: Optional[float]
    fuente: str
    ultima_sincronizacion: Optional[datetime]

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# TARIFAS
# ---------------------------------------------------------------------------

class TarifaOut(BaseModel):
    id: int
    servicio_id: int
    tipo_usuario: str
    estrato: Optional[int]
    concepto: str
    tipo_tarifa: str
    valor: Optional[float]
    unidad: Optional[str]
    fecha_vigencia: Optional[date]
    estado: str
    fuente: Optional[str]
    fecha_actualizacion: datetime

    model_config = {"from_attributes": True}


class TarifaCreate(BaseModel):
    servicio_id: int
    tipo_usuario: str
    estrato: Optional[int] = None
    concepto: str
    tipo_tarifa: str
    valor: Optional[float] = None
    unidad: Optional[str] = None
    fecha_vigencia: Optional[date] = None
    estado: str = "Referencial"
    fuente: Optional[str] = None

    @field_validator("tipo_tarifa")
    @classmethod
    def check_tipo_tarifa(cls, v):
        return _validar_opcion(v, TIPOS_TARIFA, "tipo_tarifa")


# ---------------------------------------------------------------------------
# INVENTARIO
# ---------------------------------------------------------------------------

class ProductoOut(BaseModel):
    id: int
    codigo: str
    nombre: str
    categoria: str
    unidad: Optional[str]
    existencia: Optional[float]
    costo_promedio: Optional[float]
    stock_minimo: Optional[float]
    punto_reorden: Optional[float]
    ubicacion: Optional[str]
    proveedor: Optional[str]
    fuente: str
    ultima_sincronizacion: Optional[datetime]

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# AUTENTICACIÓN INTERNA
# ---------------------------------------------------------------------------

class LoginIn(BaseModel):
    correo: str
    password: str


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    rol: str
    nombre_completo: str


class UsuarioInternoCreate(BaseModel):
    nombre_completo: str
    correo: str
    telefono: Optional[str] = None
    rol: str = "CONSULTA"
    password: str

    @field_validator("rol")
    @classmethod
    def check_rol(cls, v):
        return _validar_opcion(v, ROLES_INTERNOS, "rol")


# ---------------------------------------------------------------------------
# WHATSAPP WEBHOOK (formato simplificado, compatible con Meta Cloud API)
# ---------------------------------------------------------------------------

class WhatsAppMensajeEntrante(BaseModel):
    telefono: str
    texto: str
    wa_message_id: Optional[str] = None
