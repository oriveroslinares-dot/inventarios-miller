"""Guardado de archivos de evidencia (fotografías/documentos) asociados a un radicado."""
import uuid
from pathlib import Path

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.config import settings
from app.models import Evidencia

EXTENSIONES_PERMITIDAS = {".jpg", ".jpeg", ".png", ".pdf", ".webp", ".heic", ".doc", ".docx"}


def guardar_evidencia(db: Session, radicado_id: int, filename: str, contenido: bytes) -> Evidencia:
    extension = Path(filename or "").suffix.lower()
    if extension not in EXTENSIONES_PERMITIDAS:
        raise HTTPException(
            status_code=400,
            detail=f"Tipo de archivo no permitido. Extensiones válidas: {', '.join(sorted(EXTENSIONES_PERMITIDAS))}",
        )
    tamano_mb = len(contenido) / (1024 * 1024)
    if tamano_mb > settings.MAX_UPLOAD_SIZE_MB:
        raise HTTPException(
            status_code=400,
            detail=f"El archivo supera el tamaño máximo permitido ({settings.MAX_UPLOAD_SIZE_MB} MB).",
        )

    upload_dir = Path(settings.UPLOAD_DIR) / str(radicado_id)
    upload_dir.mkdir(parents=True, exist_ok=True)
    nombre_seguro = f"{uuid.uuid4().hex}{extension}"
    ruta_destino = upload_dir / nombre_seguro
    with open(ruta_destino, "wb") as f:
        f.write(contenido)

    evidencia = Evidencia(
        radicado_id=radicado_id,
        tipo_archivo=extension.lstrip("."),
        nombre_archivo=filename or nombre_seguro,
        ruta_archivo=str(ruta_destino),
        tamano_bytes=len(contenido),
    )
    db.add(evidencia)
    db.commit()
    db.refresh(evidencia)
    return evidencia
