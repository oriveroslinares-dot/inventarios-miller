# Sitio web — Triple A del Barrio Cartagena

Página web estática (HTML, CSS y JavaScript). No necesita base de datos ni PHP.

## Antes de publicar: complete los datos

Abra `js/datos.js` con cualquier editor de texto y reemplace todo lo marcado **POR CONFIRMAR**:

- Teléfono, WhatsApp, línea de daños y horario de oficina
- Días de recolección de aseo
- Puntos de pago
- Avisos y cortes programados (borre los dos de ejemplo)
- Resultado mensual del IRCA (calidad del agua)

Suba los PDF de transparencia a una carpeta `documentos/` con los nombres indicados en `datos.js`
(contrato de condiciones uniformes, tarifas, informe de gestión, estatutos).

## Cómo subirla a cPanel

1. Entre a cPanel y abra **Administrador de archivos**.
2. Entre a la carpeta `public_html`. Si ya hay una página vieja, descárguela primero como respaldo.
3. Pulse **Cargar** y suba `sitio-triple-a.zip`.
4. Haga clic derecho sobre el .zip y elija **Extraer**. Los archivos (`index.html`, `css/`, `js/`, `img/`)
   deben quedar directamente dentro de `public_html`, no dentro de una subcarpeta.
5. Borre el .zip y abra el dominio en el navegador.

Recuerde: el dominio y el hosting deben estar renovados para que la página se vea en internet.

## Actualizaciones del día a día

Para publicar un corte de agua o cambiar el estado del servicio, edite solo `js/datos.js`
desde el Administrador de archivos (clic derecho, **Editar**) y guarde. No toque el HTML.
