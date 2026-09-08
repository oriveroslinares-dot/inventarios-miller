"""
Pruebas de integración sobre la aplicación completa: estructura de la API,
autenticación/roles, carga de evidencias, chatbot y webhook de WhatsApp.
"""
import io


def test_salud(client):
    resp = client.get("/api/salud")
    assert resp.status_code == 200
    assert resp.json()["estado"] == "ok"


def test_home_publica_responde(client):
    resp = client.get("/")
    assert resp.status_code == 200


def test_servicios_iniciales_creados_por_seed(client):
    resp = client.get("/api/servicios")
    assert resp.status_code == 200
    nombres = {s["nombre"] for s in resp.json()}
    assert nombres == {"Acueducto", "Alcantarillado", "Aseo"}


def _login_admin(client):
    resp = client.post(
        "/api/auth/login",
        json={"correo": "admin@tripleaaacartagenita.gov.co", "password": "Admin#2026"},
    )
    assert resp.status_code == 200
    return resp.json()["access_token"]


def test_api_usuarios_requiere_autenticacion(client):
    resp = client.get("/api/usuarios")
    assert resp.status_code == 401


def test_login_admin_y_creacion_de_usuario(client):
    token = _login_admin(client)
    headers = {"Authorization": f"Bearer {token}"}

    resp = client.post(
        "/api/usuarios",
        headers=headers,
        json={
            "tipo_documento": "CC", "numero_documento": "9999999999",
            "nombre_completo": "Usuario de Integración", "telefono": "3010000000",
        },
    )
    assert resp.status_code == 200
    assert resp.json()["numero_documento"] == "9999999999"

    resp = client.get("/api/usuarios", headers=headers)
    assert resp.status_code == 200
    assert any(u["numero_documento"] == "9999999999" for u in resp.json())


def test_rol_consulta_no_puede_crear_usuarios(client):
    token = _login_admin(client)
    headers = {"Authorization": f"Bearer {token}"}

    resp = client.post(
        "/api/usuarios-internos",
        headers=headers,
        json={
            "nombre_completo": "Funcionario Consulta", "correo": "consulta@demo.test",
            "rol": "CONSULTA", "password": "Consulta#123",
        },
    )
    assert resp.status_code == 200

    resp = client.post(
        "/api/auth/login", json={"correo": "consulta@demo.test", "password": "Consulta#123"}
    )
    token_consulta = resp.json()["access_token"]
    headers_consulta = {"Authorization": f"Bearer {token_consulta}"}

    # CONSULTA puede leer...
    resp = client.get("/api/usuarios", headers=headers_consulta)
    assert resp.status_code == 200

    # ...pero no puede crear usuarios.
    resp = client.post(
        "/api/usuarios",
        headers=headers_consulta,
        json={"tipo_documento": "CC", "numero_documento": "8888888888", "nombre_completo": "No autorizado"},
    )
    assert resp.status_code == 403


def test_pqr_genera_radicado_y_permite_consulta_publica(client):
    resp = client.post(
        "/api/pqr",
        json={
            "tipo_pqr": "Petición", "asunto": "Prueba de integración", "descripcion": "Descripción",
            "numero_documento": "7777777777", "nombre_completo": "Usuario API",
        },
    )
    assert resp.status_code == 200
    numero_radicado = resp.json()["numero_radicado"]
    assert numero_radicado.startswith("PQR-")

    consulta = client.get(f"/api/radicados/{numero_radicado}")
    assert consulta.status_code == 200
    assert consulta.json()["estado"] == "Recibido"
    assert len(consulta.json()["historial"]) == 1


def test_dano_genera_radicado_y_permite_adjuntar_evidencia(client):
    resp = client.post(
        "/api/danos",
        json={
            "tipo_dano": "Fuga de agua", "direccion": "Calle de prueba", "descripcion": "Fuga visible",
            "numero_documento": "6666666666", "nombre_completo": "Usuario Daño",
        },
    )
    assert resp.status_code == 200
    radicado = resp.json()

    archivo = io.BytesIO(b"contenido de evidencia de prueba")
    resp = client.post(
        "/api/evidencias",
        data={"radicado_id": str(radicado["id"])},
        files={"archivo": ("evidencia.jpg", archivo, "image/jpeg")},
    )
    assert resp.status_code == 200

    resp = client.get(f"/api/evidencias/radicado/{radicado['id']}")
    assert resp.status_code == 200
    assert len(resp.json()) == 1
    assert resp.json()[0]["nombre_archivo"] == "evidencia.jpg"


def test_evidencia_rechaza_extension_no_permitida(client):
    resp = client.post(
        "/api/pqr",
        json={
            "tipo_pqr": "Queja", "asunto": "Para evidencia inválida", "descripcion": "Descripción",
            "numero_documento": "6666666600", "nombre_completo": "Usuario Evidencia",
        },
    )
    radicado = resp.json()
    archivo = io.BytesIO(b"MZ...")
    resp = client.post(
        "/api/evidencias",
        data={"radicado_id": str(radicado["id"])},
        files={"archivo": ("virus.exe", archivo, "application/octet-stream")},
    )
    assert resp.status_code == 400


def test_chatbot_menu_y_flujo_de_reporte_de_dano(client):
    telefono = "573000000000"
    resp = client.post("/api/whatsapp/test", json={"telefono": telefono, "texto": "hola"})
    assert "1. Consultar factura o saldo" in resp.json()["respuesta"]

    resp = client.post("/api/whatsapp/test", json={"telefono": telefono, "texto": "2"})
    assert "tipo" in resp.json()["respuesta"].lower()

    resp = client.post("/api/whatsapp/test", json={"telefono": telefono, "texto": "1"})  # Fuga de agua
    resp = client.post("/api/whatsapp/test", json={"telefono": telefono, "texto": "Calle Falsa 123"})
    resp = client.post("/api/whatsapp/test", json={"telefono": telefono, "texto": "Fuga grande"})
    resp = client.post("/api/whatsapp/test", json={"telefono": telefono, "texto": "1234567890"})

    assert "radicado" in resp.json()["respuesta"].lower()

    import re
    match = re.search(r"DANO-\d{4}-\d{6}", resp.json()["respuesta"])
    assert match is not None

    consulta = client.get(f"/api/radicados/{match.group(0)}")
    assert consulta.status_code == 200
    assert consulta.json()["canal_origen"] == "WHATSAPP"


def test_webhook_whatsapp_verificacion_sin_credenciales(client):
    resp = client.get(
        "/api/whatsapp/webhook",
        params={"hub.mode": "subscribe", "hub.verify_token": "x", "hub.challenge": "123"},
    )
    assert resp.status_code == 503  # sin WHATSAPP_VERIFY_TOKEN configurado


def test_facturacion_exige_segundo_factor_de_validacion(client):
    token = _login_admin(client)
    headers = {"Authorization": f"Bearer {token}"}
    client.post(
        "/api/usuarios",
        headers=headers,
        json={
            "tipo_documento": "CC", "numero_documento": "5555555555",
            "nombre_completo": "Usuario Facturación", "telefono": "3020000000",
        },
    )

    resp = client.get("/api/facturas/5555555555", params={"telefono": "0000000000"})
    assert resp.status_code == 403

    resp = client.get("/api/facturas/5555555555", params={"telefono": "3020000000"})
    assert resp.status_code == 200
    assert resp.json() == []  # sin facturas cargadas: lista vacía, no datos inventados


def test_tarifas_sin_confirmar_se_muestran_como_referenciales(client):
    token = _login_admin(client)
    headers = {"Authorization": f"Bearer {token}"}

    servicios = client.get("/api/servicios").json()
    servicio_id = servicios[0]["id"]

    resp = client.post(
        "/api/tarifas",
        headers=headers,
        json={
            "servicio_id": servicio_id, "tipo_usuario": "Residencial", "concepto": "Cargo fijo prueba",
            "tipo_tarifa": "Cargo fijo",
        },
    )
    assert resp.status_code == 200
    tarifa = resp.json()
    assert tarifa["valor"] is None
    assert tarifa["estado"] == "Referencial"
