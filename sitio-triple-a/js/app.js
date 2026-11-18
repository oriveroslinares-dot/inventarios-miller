(function () {
  "use strict";
  var D = window.TRIPLE_A || {};
  var $ = function (s) { return document.querySelector(s); };
  var esc = function (t) {
    return String(t == null ? "" : t).replace(/[&<>"']/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c];
    });
  };
  var soloNumeros = function (t) { return String(t || "").replace(/\D/g, ""); };
  var waLink = function (texto) {
    return "https://wa.me/" + soloNumeros(D.whatsapp) + (texto ? "?text=" + encodeURIComponent(texto) : "");
  };

  /* ---------- Menú móvil ---------- */
  var boton = $(".barra__menu"), nav = $("#nav");
  boton.addEventListener("click", function () {
    var abierto = nav.classList.toggle("abierto");
    boton.setAttribute("aria-expanded", abierto);
  });
  nav.addEventListener("click", function (e) {
    if (e.target.tagName === "A") { nav.classList.remove("abierto"); boton.setAttribute("aria-expanded", "false"); }
  });

  /* ---------- Hero: el agua sube hasta la mitad del titular ---------- */
  var hero = $(".hero"), titulo = $("#titulo-hero");
  function calcularNivel() {
    // Corta una línea del titular por la mitad (no el espacio entre líneas)
    var h = hero.getBoundingClientRect(), r = document.createRange();
    r.selectNodeContents(titulo);
    var lineas = [];
    Array.prototype.forEach.call(r.getClientRects(), function (c) {
      if (c.width > 2 && !lineas.some(function (l) { return Math.abs(l.top - c.top) < 4; })) lineas.push(c);
    });
    lineas.sort(function (a, b) { return a.top - b.top; });
    if (!lineas.length) { var t = titulo.getBoundingClientRect(); return Math.round(t.top - h.top + t.height * 0.5); }
    var l = lineas[Math.floor((lineas.length - 1) / 2)];
    return Math.round(l.top - h.top + l.height * 0.6);
  }
  function aplicarNivel() { hero.style.setProperty("--nivel", calcularNivel() + "px"); }
  function llenar() {
    hero.style.setProperty("--nivel", hero.offsetHeight + 40 + "px");
    requestAnimationFrame(function () {
      requestAnimationFrame(function () { hero.classList.add("lleno"); aplicarNivel(); });
    });
  }
  if (document.fonts && document.fonts.ready) { document.fonts.ready.then(llenar); } else { window.addEventListener("load", llenar); }
  var timer;
  window.addEventListener("resize", function () {
    clearTimeout(timer);
    timer = setTimeout(function () { hero.classList.remove("lleno"); aplicarNivel(); }, 80);
  });

  /* ---------- Estado del servicio ---------- */
  var titulos = { normal: "Servicio normal", programado: "Corte programado", interrumpido: "Servicio interrumpido" };
  var estado = titulos[D.estado] ? D.estado : "normal";
  $(".estado__punto").dataset.estado = estado;
  $(".estado__titulo").textContent = titulos[estado];
  if (D.mensajeEstado) $(".estado__mensaje").textContent = D.mensajeEstado;

  /* ---------- Recolección ---------- */
  $("#lista-recoleccion").innerHTML = (D.recoleccion || []).map(function (r) {
    return "<li><strong>" + esc(r.dia) + "</strong>" + esc(r.tipo) + "</li>";
  }).join("");

  /* ---------- Puntos de pago ---------- */
  $("#lista-puntos").innerHTML = (D.puntosPago || []).map(function (p) {
    return "<li><strong>" + esc(p.nombre) + "</strong><span>" + esc(p.detalle) + "</span></li>";
  }).join("");
  $("#wa-pago").href = waLink("Hola, envío el comprobante de pago. Mi código de suscriptor es: ");

  /* ---------- Avisos ---------- */
  var meses = ["ene", "feb", "mar", "abr", "may", "jun", "jul", "ago", "sep", "oct", "nov", "dic"];
  var hoy = new Date(); hoy.setHours(0, 0, 0, 0);
  var avisos = (D.avisos || []).slice().sort(function (a, b) { return a.fecha < b.fecha ? 1 : -1; });
  $("#lista-avisos").innerHTML = avisos.length ? avisos.map(function (a) {
    var p = String(a.fecha).split("-"), f = new Date(+p[0], +p[1] - 1, +p[2]);
    var pasado = f < hoy;
    return '<li class="aviso' + (pasado ? " aviso--pasado" : "") + '">' +
      '<p class="aviso__fecha"><b>' + f.getDate() + "</b><span>" + meses[f.getMonth()] + " " + f.getFullYear() + "</span></p>" +
      "<div><h3>" + esc(a.titulo) + '<span class="aviso__etiqueta">' + (pasado ? "Finalizado" : "Próximo") + "</span></h3>" +
      "<p>" + esc(a.detalle) + "</p>" +
      (a.sectores ? '<p class="aviso__sector">Sectores: ' + esc(a.sectores) + "</p>" : "") + "</div></li>";
  }).join("") : '<li class="aviso"><div><h3>No hay cortes programados</h3><p>Si su casa se queda sin agua, use el formulario de reporte.</p></div></li>';

  /* ---------- Calidad del agua ---------- */
  var c = D.calidad || {}, aguja = $("#aguja");
  if (typeof c.irca === "number") {
    var v = c.irca;
    var nivel = v <= 5 ? "Sin riesgo" : v <= 14 ? "Riesgo bajo" : v <= 35 ? "Riesgo medio" : v <= 80 ? "Riesgo alto" : "Inviable sanitariamente";
    var tramos = [[0, 5], [5, 14], [14, 35], [35, 80]], pos = 100;
    tramos.forEach(function (t, i) { if (v >= t[0] && v <= t[1] && pos === 100) pos = (i + (v - t[0]) / (t[1] - t[0])) * 25; });
    aguja.style.left = pos + "%";
    $("#irca-valor").textContent = "IRCA " + v.toLocaleString("es-CO") + " %: " + nivel;
    $("#irca-fuente").textContent = [c.mes, c.laboratorio].filter(Boolean).join(". ");
  } else {
    aguja.hidden = true;
    $("#irca-valor").textContent = "Resultado del mes por publicar";
    $("#irca-fuente").textContent = "Cuando recibamos el informe del laboratorio lo publicaremos aquí.";
  }

  /* ---------- Documentos ---------- */
  $("#lista-documentos").innerHTML = (D.documentos || []).map(function (d) {
    return '<li><a href="' + esc(d.archivo) + '" target="_blank" rel="noopener">' + esc(d.nombre) + "<small>PDF</small></a></li>";
  }).join("");

  /* ---------- Contacto ---------- */
  var tel = D.lineaDanos || D.telefono;
  $("#tel-danos").textContent = tel; $("#tel-danos").href = "tel:+" + soloNumeros(tel);
  $("#pie-direccion").textContent = D.direccion || "";
  $("#pie-horario").textContent = D.horario || "";
  $("#pie-tel").textContent = D.telefono; $("#pie-tel").href = "tel:+" + soloNumeros(D.telefono);
  $("#pie-correo").textContent = D.correo; $("#pie-correo").href = "mailto:" + D.correo;
  $("#pie-wa").href = waLink("Hola, Triple A. ");
  $("#anio").textContent = new Date().getFullYear();

  /* ---------- Calculadora de consumo ---------- */
  var ip = $("#personas"), id = $("#ducha"), ir = $("#ropa");
  function calcular() {
    var personas = +ip.value, ducha = +id.value, ropa = +ir.value;
    $("#o-personas").textContent = personas; $("#o-ducha").textContent = ducha; $("#o-ropa").textContent = ropa;
    // litros/día: ducha 9 L/min, sanitario 5 descargas x 6 L, cocina y lavamanos 15 L por persona
    var litrosDia = personas * (ducha * 9 + 30 + 15) + (ropa * 70) / 7 + 20;
    var m3 = litrosDia * 30 / 1000;
    $("#r-m3").textContent = m3.toLocaleString("es-CO", { maximumFractionDigits: 1 });
    $("#tanque-agua").style.height = Math.min(m3 / 22 * 100, 100) + "%";
    var nota = m3 <= 11
      ? "Está dentro del consumo básico de 11 m³. Muy bien."
      : "Supera el consumo básico por " + (m3 - 11).toLocaleString("es-CO", { maximumFractionDigits: 1 }) + " m³. Ese excedente se cobra sin subsidio.";
    $("#r-nota").textContent = nota + " Cálculo aproximado; su factura muestra el consumo real del medidor.";
  }
  [ip, id, ir].forEach(function (el) { el.addEventListener("input", calcular); });
  calcular();

  /* ---------- Formulario PQRS ---------- */
  var form = $("#form-pqrs"), error = $("#form-error");
  form.addEventListener("submit", function (e) {
    e.preventDefault();
    var via = e.submitter ? e.submitter.value : "correo";
    var f = new FormData(form);
    var faltan = ["nombre", "direccion", "telefono", "mensaje"].filter(function (k) { return !String(f.get(k) || "").trim(); });
    if (faltan.length) {
      error.textContent = "Complete estos campos para enviar: " + faltan.map(function (k) {
        return { nombre: "nombre", direccion: "dirección", telefono: "teléfono", mensaje: "descripción" }[k];
      }).join(", ") + ".";
      error.hidden = false;
      form.querySelector('[name="' + faltan[0] + '"]').focus();
      return;
    }
    error.hidden = true;
    var tipo = f.get("tipo");
    var cuerpo = "Tipo: " + tipo + "\nNombre: " + f.get("nombre") + "\nCódigo de suscriptor: " + (f.get("codigo") || "No indicado") +
      "\nDirección: " + f.get("direccion") + "\nTeléfono: " + f.get("telefono") + "\n\n" + f.get("mensaje");
    if (via === "whatsapp") {
      window.open(waLink(cuerpo), "_blank", "noopener");
    } else {
      location.href = "mailto:" + D.correo + "?subject=" + encodeURIComponent(tipo + " - " + f.get("nombre")) + "&body=" + encodeURIComponent(cuerpo);
    }
  });
})();
