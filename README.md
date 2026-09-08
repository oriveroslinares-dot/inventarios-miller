# TRIPLE AAA DE CARTAGENITA — Plataforma de Atención al Usuario

**Acueducto · Alcantarillado · Aseo**

Plataforma funcional (backend + API + panel administrativo + portal ciudadano)
para la gestión de PQR, reportes de daños, solicitudes, radicados, facturación,
tarifas e inventario — construida para servir posteriormente como backend de
un **chatbot de atención al usuario por WhatsApp** (Meta WhatsApp Business
Platform / Cloud API), y preparada para integrarse con **SINFA** (facturación)
y **GBS** (inventario) cuando esas integraciones estén autorizadas.

Esta NO es una página informativa: hay base de datos relacional, lógica de
negocio, autenticación por roles, generación automática de radicados únicos,
historial de trazabilidad, carga de evidencias, y una API REST completa.

---

## 1. Puesta en marcha

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

cp .env.example .env   # opcional: personalice SECRET_KEY, etc.

uvicorn app.main:app --reload
```

Abra `http://127.0.0.1:8000/` para el portal público, o
`http://127.0.0.1:8000/admin/login` para el panel administrativo.
La documentación interactiva de la API está en `http://127.0.0.1:8000/docs`.

Al iniciar por primera vez, la aplicación:
- Crea las tablas de la base de datos (SQLite por defecto, en `triple_aaa.db`).
- Crea los 3 servicios (Acueducto, Alcantarillado, Aseo).
- Crea un usuario **ADMINISTRADOR** inicial:
  - correo: `admin@tripleaaacartagenita.gov.co`
  - contraseña temporal: `Admin#2026` (**cámbiela de inmediato** creando un
    nuevo administrador desde Configuración y desactivando este, o rotando su
    contraseña).
- Carga **DATOS DE PRUEBA** (si `LOAD_DEMO_DATA=true`, valor por defecto): 5
  usuarios, 5 facturas, 3 PQR, 3 reportes de daño, 1 solicitud adicional,
  historial de trazabilidad y 5 productos de inventario. Todo queda marcado
  con `es_demo=True` y con la insignia **DEMO** en el panel, para que nunca se
  confunda con información real. Desactive `LOAD_DEMO_DATA` en `.env` antes de
  usar la aplicación en producción.

### Pruebas automatizadas

```bash
pytest tests/ -v
```

20 pruebas cubren: unicidad y consecutividad de radicados, generación de PQR y
daños con su historial inicial, cambios de estado con historial completo,
estructura de la API, autenticación y control de roles, carga y validación de
evidencias, el flujo del chatbot, la verificación del webhook de WhatsApp y la
exigencia del segundo factor de validación para consultar facturación.

---

## 2. Qué se construyó

| Capa | Contenido |
|---|---|
| **Base de datos** | SQLAlchemy 2.0, 20 tablas (ver sección 3). SQLite por defecto; cambie `DATABASE_URL` a PostgreSQL en producción sin tocar código. |
| **Lógica de negocio** | `app/services/radicados.py` (numeración única y consecutiva, creación de PQR/daños, historial automático, cambios de estado), `app/services/sinfa.py` y `app/services/gbs.py` (capas de integración preparadas), `app/services/chatbot.py` (máquina de estados conversacional). |
| **API REST** | 13 routers bajo `/api/...` (ver sección 4), documentados automáticamente en `/docs`. |
| **Panel administrativo** | Server-rendered (Jinja2 + Bootstrap 5), en `/admin/...`: dashboard, usuarios, radicados/PQR/daños, facturación, tarifas, inventario, configuración. |
| **Portal ciudadano** | En `/`, `/reportar-dano`, `/presentar-pqr`, `/consultar-radicado`, `/registrar-usuario`. |
| **Seguridad** | JWT (cookie httponly para el panel, Bearer para la API), contraseñas con bcrypt, 4 roles, auditoría de cada acción sensible (`app/security.py`, tabla `auditoria`). |
| **Datos de prueba** | `app/seed.py`, claramente marcados `es_demo=True`. |
| **Pruebas** | `tests/` — 20 pruebas automatizadas (pytest). |

---

## 3. Tablas creadas

**Usuarios y seguridad**
- `usuarios` — ciudadanos/clientes del servicio.
- `usuarios_internos` — funcionarios/administradores (con rol y contraseña hasheada).
- `auditoria` — registro de toda acción sensible (quién, qué, cuándo, IP, resultado).

**Servicios y radicados**
- `servicios` — Acueducto, Alcantarillado, Aseo.
- `radicado_counters` — soporte interno para la numeración consecutiva por tipo/año.
- `radicados` — entidad transversal de PQR, daños y solicitudes (número único, estado, prioridad, funcionario asignado, respuesta).
- `pqr` — detalle específico de una PQR (tipo, asunto), 1:1 con `radicados`.
- `reportes_danos` — detalle específico de un daño (tipo, dirección, geolocalización), 1:1 con `radicados`.
- `historial_radicados` — trazabilidad completa de cada cambio de estado.
- `evidencias` — archivos (fotos/documentos) asociados a un radicado.

**Facturación (preparada para SINFA)**
- `facturas`, `consumos`, `pagos`, `cartera` — todas con `valor`/`saldo` nulos por defecto ("Dato faltante") hasta que exista una fuente real.

**Tarifas**
- `tarifas` — parametrizable desde el panel; queda en estado `Referencial` hasta marcarse `Confirmada en SINFA`.

**Inventario (preparado para GBS)**
- `productos_inventario` — existencias nulas por defecto hasta sincronizar con GBS.

**Configuración y chatbot**
- `parametros_sistema` — tiempos legales y textos configurables (vacíos hasta que TRIPLE AAA los defina).
- `sesiones_chatbot` — estado de la conversación por número de teléfono.
- `mensajes_whatsapp` — bitácora de mensajes entrantes/salientes.

---

## 4. APIs creadas

| Método | Ruta | Descripción |
|---|---|---|
| POST/GET | `/api/usuarios`, `/api/usuarios/{id}` | Gestión de usuarios (requiere rol interno). |
| POST/GET | `/api/usuarios-internos` | Gestión de funcionarios (solo ADMINISTRADOR crea). |
| POST | `/api/auth/login`, `/api/auth/logout` | Autenticación de funcionarios (JWT). |
| GET | `/api/servicios` | Catálogo de servicios. |
| POST | `/api/radicados` | Crea una solicitud genérica (tipo SOLICITUD). |
| GET | `/api/radicados` | Lista con filtros (tipo, estado, servicio, prioridad, usuario, fechas). |
| GET | `/api/radicados/{numero}` | Consulta pública del estado (con validación opcional por documento). |
| PATCH | `/api/radicados/{numero}/estado` | Cambio de estado (funcionarios), genera historial. |
| POST/GET | `/api/pqr`, `/api/pqr/{id}` | Radicación y consulta de PQR. |
| POST/GET | `/api/danos`, `/api/danos/{id}` | Radicación y consulta de reportes de daño. |
| POST/GET | `/api/evidencias` | Carga y listado de evidencias (fotos/documentos). |
| GET | `/api/facturas/{documento}`, `/api/cartera/{documento}`, `/api/consumos/{documento}` | Consulta de facturación (exige teléfono registrado como segundo factor). |
| GET/POST | `/api/tarifas` | Consulta y creación de tarifas (referenciales). |
| GET/POST | `/api/inventario`, `/api/inventario/sincronizar` | Consulta e intento de sincronización de inventario. |
| GET/POST | `/api/whatsapp/webhook` | Verificación y recepción de mensajes de Meta. |
| POST | `/api/whatsapp/test` | Prueba del chatbot sin depender de Meta. |
| GET | `/api/whatsapp/estado`, `/api/sinfa/estado` (en tarifas/facturación), `/api/inventario/gbs/estado` | Estado de cada integración externa. |
| GET | `/api/dashboard/resumen` | Estadísticas para el panel. |
| GET | `/api/salud` | Verificación de disponibilidad. |

---

## 5. Cómo funciona el sistema de radicados

Cada PQR, reporte de daño o solicitud genera un **radicado único**:

```
PREFIJO-AÑO-CONSECUTIVO      Ejemplos: PQR-2026-000001, DANO-2026-000001, SOL-2026-000001
```

`app/services/radicados.py` mantiene un contador por `(tipo, año)` en la
tabla `radicado_counters`, lo incrementa de forma atómica dentro de la misma
transacción de creación del radicado, y verifica la restricción `UNIQUE` de
`radicados.numero_radicado` como segunda barrera de seguridad (con
reintentos). En Postgres además se usa bloqueo de fila (`SELECT ... FOR
UPDATE`) para concurrencia real entre procesos; en SQLite (desarrollo) un solo
escritor a la vez ya garantiza la atomicidad.

Al crear cualquier radicado se registra automáticamente:
1. El radicado con estado inicial `Recibido`.
2. El registro específico (`pqr` o `reportes_danos`) enlazado 1:1.
3. Una entrada en `historial_radicados` (`estado_anterior=None → estado_nuevo=Recibido`).

Cada cambio posterior de estado (`Recibido → En revisión → Asignado → En
proceso → Pendiente de información → Resuelto/Cerrado/Rechazado`) crea una
nueva entrada de historial con el estado anterior, el nuevo, quién lo hizo y
cuándo — permitiendo reconstruir toda la trazabilidad del caso.

---

## 6. Cómo se conecta posteriormente WhatsApp

1. En Meta for Developers, cree/configure la app de **WhatsApp Business Platform**
   y obtenga: `WHATSAPP_ACCESS_TOKEN`, `WHATSAPP_PHONE_NUMBER_ID`,
   `WHATSAPP_BUSINESS_ACCOUNT_ID`, y defina un `WHATSAPP_VERIFY_TOKEN` propio.
2. Configure esas 4 variables en `.env` (nunca en el código).
3. Registre el webhook en Meta apuntando a
   `https://SU_DOMINIO/api/whatsapp/webhook` — Meta llamará primero a la
   verificación (`GET`, ya implementada) y luego enviará los mensajes por `POST`.
4. A partir de ahí, cada mensaje entrante pasa por
   `app/services/chatbot.py` (reconoce las 9 intenciones y conduce la
   conversación por estados) y la respuesta se envía de vuelta usando
   `enviar_mensaje_whatsapp()` en `app/routers/whatsapp.py`, que ya construye
   las llamadas a la Cloud API — solo falta que existan las credenciales.

Mientras tanto, `POST /api/whatsapp/test` permite probar exactamente la misma
lógica conversacional sin depender de Meta.

---

## 7. Qué falta para conectar SINFA

`app/services/sinfa.py` (**SINFA INTEGRATION SERVICE**) ya expone los puntos
de extensión (`sincronizar_facturacion`, `sincronizar_tarifas`) y el
formateo seguro de facturas/cartera/consumos/tarifas ("Dato faltante" cuando
no hay información). Para activarla falta que TRIPLE AAA defina y entregue:

- El **mecanismo de acceso autorizado**: API REST, exportación CSV/Excel
  periódica, o una conexión de solo lectura a la base de datos de SINFA.
- Credenciales/endpoint (`SINFA_API_URL`, `SINFA_API_KEY`) o la ubicación de
  los archivos a importar.
- El diccionario de campos de SINFA (facturación, consumos, cartera, pagos,
  tarifas, usuarios) para mapearlos a las tablas ya creadas.
- Confirmación oficial de los valores tarifarios (hoy quedan como
  `Referencial` hasta marcarse `Confirmada en SINFA`).

Una vez definido, solo se implementa el conector dentro de `sincronizar_*`;
el resto del sistema (API, panel, chatbot) no necesita cambios.

---

## 8. Qué falta para conectar GBS

`app/services/gbs.py` (**GBS INTEGRATION SERVICE**) sigue el mismo patrón.
Falta que TRIPLE AAA defina:

- El mecanismo de integración disponible (API, CSV/Excel, base de datos de
  solo lectura).
- Credenciales/endpoint (`GBS_API_URL`, `GBS_API_KEY`).
- El mapeo de existencias, costos, compras, proveedores y kardex hacia
  `productos_inventario`.

Mientras tanto, el inventario cargado manualmente por el panel funciona con
normalidad, y los campos no sincronizados muestran explícitamente "Dato
faltante – pendiente de sincronización con GBS."

---

## 9. Qué configurar para ponerlo en funcionamiento

1. **Variables de entorno** (`.env`, basado en `.env.example`):
   - `SECRET_KEY` propio y seguro.
   - `DATABASE_URL` apuntando a PostgreSQL en producción.
   - `LOAD_DEMO_DATA=false` antes de operar con datos reales.
   - Credenciales de WhatsApp, SINFA y GBS **solo cuando estén disponibles**.
2. **Primer administrador**: cambiar la contraseña temporal del usuario
   `admin@tripleaaacartagenita.gov.co` (o crear uno nuevo y desactivar este)
   desde `/admin/configuracion`.
3. **Tiempos legales y parámetros** (`/admin/configuracion`): están vacíos a
   propósito; deben cargarse con los valores que TRIPLE AAA apruebe
   formalmente (la aplicación nunca los inventa).
4. **Tarifas reales**: cargar desde el panel como `Referencial` hasta que
   SINFA las confirme oficialmente.
5. **Almacenamiento de evidencias**: en producción, `UPLOAD_DIR` debería
   apuntar a un volumen persistente (o migrarse a almacenamiento de objetos).
6. **HTTPS obligatorio** para el dominio público antes de registrar el
   webhook de WhatsApp (Meta lo exige).

---

## 10. Verificación realizada

- ✅ Relaciones de base de datos probadas (usuario ↔ radicado ↔ PQR/daño ↔ historial ↔ evidencias).
- ✅ Unicidad y consecutividad de radicados verificada con 20 creaciones simultáneas en prueba automatizada.
- ✅ Una PQR y un reporte de daño generan su radicado y su historial inicial correctamente.
- ✅ El historial registra cada cambio de estado con estado anterior/nuevo.
- ✅ Los archivos de evidencia se asocian correctamente al radicado (y se valida tipo/tamaño).
- ✅ Los roles (ADMINISTRADOR/FUNCIONARIO/SUPERVISOR/CONSULTA) se validan en la API (probado: CONSULTA no puede crear usuarios).
- ✅ No se presentan datos ficticios como reales: los campos sin dato muestran "Dato faltante" / "Información no disponible actualmente." / "Dato faltante – pendiente de validación en SINFA." / "Dato faltante – pendiente de sincronización con GBS."; los datos de prueba están marcados `es_demo=True` con insignia DEMO visible.
- ✅ La API está documentada automáticamente en `/docs` (OpenAPI/Swagger).
- ✅ El webhook de WhatsApp responde correctamente sin credenciales configuradas (503 explicativo) y el chatbot es totalmente probable vía `/api/whatsapp/test`.
- ✅ La interfaz usa Bootstrap 5 responsive (probada en las vistas de escritorio; se recomienda una prueba manual adicional en dispositivo móvil real antes de producción).

No se realizó ninguna integración real con SINFA, GBS o WhatsApp: las tres
quedan estructuralmente listas y a la espera de credenciales/autorización.
