# Sitio web: Triple A del Barrio Cartagena

Página estática (HTML, CSS y JavaScript). No necesita base de datos ni PHP: funciona en cualquier hosting con cPanel.

## Estructura

```
index.html          Página principal (no hace falta editarla)
css/estilos.css     Diseño
js/datos.js         TODA la información editable: contacto, avisos, comunicados, documentos, tarifas
js/app.js           Animaciones e interactividad
img/                Logo, mascota y favicon
documentos/         Aquí van los PDF (estados financieros, actas, tarifas, etc.)
```

## 1. Antes de subir: complete los datos

Abra `js/datos.js` y revise todo lo marcado **POR CONFIRMAR**:

- Razón social exacta y NIT
- Dirección de la oficina
- Si el 315 744 3635 tiene WhatsApp
- Fuente de agua (aparece "Río Botello")
- Días de recolección de aseo
- Nombre del servicio de cada tabla de tarifas y los valores que faltan

## 2. Subir la página a cPanel

1. Entre a `https://marcos.colombiahosting.com.co/cpanel` con el usuario `tripleaf`.
2. En la sección **Archivos**, abra **Administrador de archivos**.
3. Entre a la carpeta **public_html**.
4. **Respaldo:** si ya hay archivos de la página anterior, selecciónelos todos, haga clic derecho y elija **Comprimir**. Descargue ese .zip a su computador.
5. Borre los archivos viejos de `public_html`. No borre carpetas como `.well-known` ni `cgi-bin`.
6. Pulse **Cargar** (Upload) y suba `sitio-triple-a.zip`. Espere a que la barra llegue a 100 %.
7. Vuelva a `public_html`, haga clic derecho sobre `sitio-triple-a.zip` y elija **Extraer**.
8. Compruebe que `index.html`, `css`, `js`, `img` y `documentos` quedaron directamente dentro de `public_html`, no dentro de otra carpeta.
9. Borre el `.zip` y abra el dominio en el navegador. Si ve la página vieja, pulse Ctrl + F5.

## 3. Publicar documentos (estados financieros, actas, etc.)

1. En el Administrador de archivos, entre a `public_html/documentos` y pulse **Cargar**.
2. Suba el PDF con un nombre sin espacios ni tildes, por ejemplo `estados-financieros-2025.pdf`.
3. Abra `public_html/js/datos.js` (clic derecho, **Editar**) y agregue o ajuste la línea del documento en la lista `documentos`:
   ```js
   { titulo: "Estados financieros 2025", categoria: "Estados financieros", fecha: "2026-03-31", archivo: "documentos/estados-financieros-2025.pdf", descripcion: "..." },
   ```
4. Guarde. El documento aparece en el Centro de documentos, con buscador y filtro.

## 4. Datos de pago (sección "Pague su factura aquí")

En `js/datos.js`, bloque `pagos`. **Hoy está apagada** (`mostrar: false`): no se ve la sección ni los botones de pago.
Para activarla cuando tengan Wompi, PSE o cuentas, cambie `mostrar: false` por `mostrar: true` y complete:
- `enlacePSE`: pegue el enlace del botón PSE que le da su banco. Si lo deja vacío, la opción PSE no aparece.
- `medios`: escriba el número de Nequi y la cuenta de Bancolombia, con el titular. Si un medio no aplica, borre esa línea.
  Si deja un número vacío, la página le pide al usuario que lo solicite en la línea de atención.

## 5. Publicar un comunicado o un corte de agua

Edite `js/datos.js`:
- **Comunicado:** agregue un bloque en `comunicados`. El más reciente aparece en la cinta azul bajo la portada.
- **Corte programado:** agregue un bloque en `avisos` y cambie `estado` a `"programado"`. Cuando se restablezca el servicio, vuelva a `"normal"`.

## Recordatorios

- El dominio y el hosting deben estar renovados para que la página se vea en internet.
- Cambie las contraseñas que se compartieron por correo y por chat.
