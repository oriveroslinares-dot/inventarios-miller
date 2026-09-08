"""
Pruebas de la capa de servicios de radicados: numeración única, generación
de PQR/daños, historial de trazabilidad y cambios de estado.
"""
from app.models import Servicio, Radicado, PQR, ReporteDano, HistorialRadicado
from app.schemas import PQRCreate, DanoCreate
from app.services.radicados import (
    generar_numero_radicado, crear_pqr, crear_reporte_dano, cambiar_estado_radicado,
)


def test_numeros_radicado_son_unicos_y_consecutivos(db_session):
    numeros = [generar_numero_radicado(db_session, "PQR") for _ in range(5)]
    db_session.commit()

    assert len(numeros) == len(set(numeros)), "Los números de radicado deben ser únicos."
    assert numeros == sorted(numeros)
    assert numeros[0].startswith("PQR-")
    for i, numero in enumerate(numeros):
        consecutivo_esperado = i + 1
        assert numero.endswith(f"{consecutivo_esperado:06d}")


def test_prefijos_distintos_por_tipo_de_radicado(db_session):
    pqr = generar_numero_radicado(db_session, "PQR")
    dano = generar_numero_radicado(db_session, "DANO")
    solicitud = generar_numero_radicado(db_session, "SOLICITUD")
    db_session.commit()

    assert pqr.startswith("PQR-")
    assert dano.startswith("DANO-")
    assert solicitud.startswith("SOL-")
    # cada tipo lleva su propio consecutivo, independiente de los demás
    assert pqr.endswith("000001")
    assert dano.endswith("000001")
    assert solicitud.endswith("000001")


def test_crear_pqr_genera_radicado_pqr_e_historial(db_session):
    datos = PQRCreate(
        tipo_pqr="Petición", asunto="Prueba unitaria", descripcion="Descripción de prueba",
        numero_documento="1010101010", nombre_completo="Usuario de Prueba",
        telefono="3001234567",
    )
    radicado = crear_pqr(db_session, datos)

    assert radicado.id is not None
    assert radicado.tipo == "PQR"
    assert radicado.numero_radicado.startswith("PQR-")
    assert radicado.estado == "Recibido"
    assert radicado.usuario is not None
    assert radicado.usuario.numero_documento == "1010101010"

    pqr = db_session.query(PQR).filter(PQR.radicado_id == radicado.id).first()
    assert pqr is not None
    assert pqr.tipo_pqr == "Petición"

    historial = db_session.query(HistorialRadicado).filter(
        HistorialRadicado.radicado_id == radicado.id
    ).all()
    assert len(historial) == 1
    assert historial[0].estado_nuevo == "Recibido"
    assert historial[0].estado_anterior is None


def test_crear_reporte_dano_genera_radicado_dano_e_historial(db_session):
    datos = DanoCreate(
        tipo_dano="Fuga de agua", direccion="Calle 1 # 2-3", descripcion="Fuga visible",
        numero_documento="2020202020", nombre_completo="Otro Usuario", telefono="3009876543",
    )
    radicado = crear_reporte_dano(db_session, datos)

    assert radicado.tipo == "DANO"
    assert radicado.numero_radicado.startswith("DANO-")

    dano = db_session.query(ReporteDano).filter(ReporteDano.radicado_id == radicado.id).first()
    assert dano is not None
    assert dano.tipo_dano == "Fuga de agua"
    assert dano.direccion == "Calle 1 # 2-3"

    historial = db_session.query(HistorialRadicado).filter(
        HistorialRadicado.radicado_id == radicado.id
    ).all()
    assert len(historial) == 1
    assert historial[0].estado_nuevo == "Recibido"


def test_mismo_documento_reutiliza_el_mismo_usuario(db_session):
    datos1 = PQRCreate(
        tipo_pqr="Queja", asunto="Primer caso", descripcion="Primera descripción",
        numero_documento="3030303030", nombre_completo="Usuario Repetido", telefono="3005555555",
    )
    datos2 = DanoCreate(
        tipo_dano="Rebose", direccion="Cra 9 # 1-1", descripcion="Segundo caso",
        numero_documento="3030303030", nombre_completo="Usuario Repetido", telefono="3005555555",
    )
    radicado1 = crear_pqr(db_session, datos1)
    radicado2 = crear_reporte_dano(db_session, datos2)

    assert radicado1.usuario_id == radicado2.usuario_id


def test_cambiar_estado_registra_historial_con_estado_anterior(db_session):
    datos = PQRCreate(
        tipo_pqr="Reclamo", asunto="Caso de prueba", descripcion="Descripción",
        numero_documento="4040404040", nombre_completo="Usuario Cambios", telefono="3004444444",
    )
    radicado = crear_pqr(db_session, datos)

    radicado = cambiar_estado_radicado(
        db_session, radicado, estado_nuevo="En proceso", comentario="Asignado a revisión.",
        usuario_interno_id=None, realizado_por="Funcionario de prueba",
    )
    assert radicado.estado == "En proceso"

    radicado = cambiar_estado_radicado(
        db_session, radicado, estado_nuevo="Resuelto", comentario="Caso resuelto.",
        usuario_interno_id=None, realizado_por="Funcionario de prueba",
        respuesta="Se realizó el ajuste solicitado.",
    )
    assert radicado.estado == "Resuelto"
    assert radicado.respuesta == "Se realizó el ajuste solicitado."
    assert radicado.fecha_cierre is not None

    historial = db_session.query(HistorialRadicado).filter(
        HistorialRadicado.radicado_id == radicado.id
    ).order_by(HistorialRadicado.id).all()

    assert [h.estado_nuevo for h in historial] == ["Recibido", "En proceso", "Resuelto"]
    assert historial[1].estado_anterior == "Recibido"
    assert historial[2].estado_anterior == "En proceso"


def test_no_existen_radicados_duplicados_bajo_creacion_masiva(db_session):
    numeros = set()
    for i in range(20):
        datos = PQRCreate(
            tipo_pqr="Solicitud", asunto=f"Caso {i}", descripcion="Descripción de prueba masiva",
            numero_documento=f"500000{i:04d}", nombre_completo=f"Usuario {i}",
        )
        radicado = crear_pqr(db_session, datos)
        numeros.add(radicado.numero_radicado)

    assert len(numeros) == 20
    todos = db_session.query(Radicado.numero_radicado).all()
    numeros_bd = [n[0] for n in todos]
    assert len(numeros_bd) == len(set(numeros_bd)), "No deben existir radicados duplicados en la base de datos."
