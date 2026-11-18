(function () {
  "use strict";
  document.documentElement.classList.add("js");
  var D = window.TRIPLE_A || {};
  var $ = function (s, c) { return (c || document).querySelector(s); };
  var esc = function (t) {
    return String(t == null ? "" : t).replace(/[&<>"']/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c];
    });
  };
  var num = function (t) { return String(t || "").replace(/\D/g, ""); };
  var wa = function (txt) { return "https://wa.me/" + num(D.whatsapp) + (txt ? "?text=" + encodeURIComponent(txt) : ""); };
  var quieto = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var MESES = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"];
  var fecha = function (iso) { var p = String(iso).split("-"); return new Date(+p[0], +p[1] - 1, +(p[2] || 1)); };
  var fechaLarga = function (iso) { var f = fecha(iso); return f.getDate() + " de " + MESES[f.getMonth()] + " de " + f.getFullYear(); };

  /* ---------- Barra y menú ---------- */
  var barra = $("#barra"), menu = $(".barra__menu"), nav = $("#nav");
  function barraSolida() { barra.classList.toggle("solida", window.scrollY > window.innerHeight * 0.75); }
  barraSolida();
  window.addEventListener("scroll", barraSolida, { passive: true });
  menu.addEventListener("click", function () {
    var abierto = nav.classList.toggle("abierto");
    menu.setAttribute("aria-expanded", abierto);
    barra.classList.toggle("menu-abierto", abierto);
  });
  nav.addEventListener("click", function (e) {
    if (e.target.closest("a")) { nav.classList.remove("abierto"); menu.setAttribute("aria-expanded", "false"); barra.classList.remove("menu-abierto"); }
  });

  /* ---------- Portada: agua que fluye y responde al puntero ---------- */
  var cv = $("#agua"), ctx = cv.getContext("2d"), W = 0, H = 0, dpr = 1;
  var puntero = { x: -9999, y: -9999, fuerza: 0 };
  function medir() {
    dpr = Math.min(window.devicePixelRatio || 1, 2);
    W = cv.clientWidth; H = cv.clientHeight;
    cv.width = W * dpr; cv.height = H * dpr;
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
  }
  function dibujar(t) {
    ctx.clearRect(0, 0, W, H);
    var lineas = W < 700 ? 22 : 34, paso = W < 700 ? 14 : 10;
    for (var i = 0; i < lineas; i++) {
      var base = H * 0.18 + (H * 0.82) * (i / lineas);
      var prof = i / lineas;
      ctx.beginPath();
      for (var x = -10; x <= W + 10; x += paso) {
        var y = base
          + Math.sin(x * 0.0042 + t * 0.00042 + i * 0.32) * (12 + prof * 26)
          + Math.sin(x * 0.011 - t * 0.0007 + i * 0.9) * (4 + prof * 6);
        var dx = x - puntero.x, dy = base - puntero.y, d2 = dx * dx + dy * dy;
        if (puntero.fuerza > 0.01) y -= Math.exp(-d2 / 22000) * 46 * puntero.fuerza * Math.sin(Math.sqrt(d2) * 0.045 - t * 0.008);
        x === -10 ? ctx.moveTo(x, y) : ctx.lineTo(x, y);
      }
      ctx.strokeStyle = "rgba(34,181,245," + (0.05 + prof * 0.32).toFixed(3) + ")";
      ctx.lineWidth = 1 + prof * 0.8;
      ctx.stroke();
    }
  }
  var visible = true;
  function bucle(t) {
    if (visible) { puntero.fuerza *= 0.985; dibujar(t); }
    requestAnimationFrame(bucle);
  }
  medir();
  if (quieto) { dibujar(0); } else { requestAnimationFrame(bucle); }
  window.addEventListener("resize", function () { medir(); if (quieto) dibujar(0); });
  var portada = $(".portada");
  portada.addEventListener("pointermove", function (e) {
    var r = cv.getBoundingClientRect(); puntero.x = e.clientX - r.left; puntero.y = e.clientY - r.top; puntero.fuerza = 1;
  });
  if ("IntersectionObserver" in window) {
    new IntersectionObserver(function (en) { visible = en[0].isIntersecting; }).observe(portada);
  }
  // Entrada orquestada del titular
  var arrancar = function () { requestAnimationFrame(function () { document.body.classList.add("cargado"); }); };
  if (document.fonts && document.fonts.ready) document.fonts.ready.then(arrancar); else window.addEventListener("load", arrancar);
  setTimeout(arrancar, 1500);

  /* ---------- Estado del servicio ---------- */
  var titulos = { normal: "Servicio normal", programado: "Corte programado", interrumpido: "Servicio interrumpido" };
  var est = titulos[D.estado] ? D.estado : "normal";
  $("#estado-punto").dataset.estado = est;
  $("#estado-titulo").textContent = titulos[est];
  $("#estado-mensaje").textContent = D.mensajeEstado || "";

  /* ---------- Cinta del último comunicado ---------- */
  var comunicados = (D.comunicados || []).slice().sort(function (a, b) { return a.fecha < b.fecha ? 1 : -1; });
  if (comunicados.length) {
    $("#cinta").hidden = false;
    $("#cinta-texto").textContent = comunicados[0].titulo;
    $("#cinta-fecha").textContent = fechaLarga(comunicados[0].fecha);
  }

  /* ---------- Recorrido del agua: avanza con el scroll ---------- */
  var rec = $("#recorrido"), pasos = Array.prototype.slice.call(document.querySelectorAll(".paso")), tubo = $("#tubo-agua");
  document.querySelectorAll("[data-fuente]").forEach(function (el) { el.textContent = D.fuente || "de abastecimiento"; });
  function avanzar() {
    var r = rec.getBoundingClientRect();
    var total = rec.offsetHeight - window.innerHeight;
    var p = Math.min(Math.max(-r.top / total, 0), 1);
    tubo.style.setProperty("--avance", p.toFixed(4));
    var activo = Math.min(Math.floor(p * pasos.length), pasos.length - 1);
    pasos.forEach(function (el, i) { el.classList.toggle("activo", i === activo); el.classList.toggle("hecho", i < activo); });
  }
  avanzar();
  window.addEventListener("scroll", avanzar, { passive: true });
  window.addEventListener("resize", avanzar);

  /* ---------- Recolección ---------- */
  $("#recoleccion").innerHTML = (D.recoleccion || []).map(function (r) { return "<li><b>" + esc(r.dia) + "</b>" + esc(r.tipo) + "</li>"; }).join("");

  /* ---------- Centro de documentos ---------- */
  var docs = (D.documentos || []).concat(comunicados.filter(function (c) { return c.archivo; }).map(function (c) {
    return { titulo: c.titulo, categoria: "Comunicados", fecha: c.fecha, archivo: c.archivo, descripcion: c.resumen };
  })).sort(function (a, b) { return a.fecha < b.fecha ? 1 : -1; });
  var filtro = { cat: "Todos", q: "" };
  var orden = ["Estados financieros", "Comunicados", "Informes de gestión", "Tarifas", "Asambleas", "Normatividad"];
  var cats = ["Todos"].concat(orden.filter(function (c) { return docs.some(function (d) { return d.categoria === c; }); }));
  docs.forEach(function (d) { if (cats.indexOf(d.categoria) < 0) cats.push(d.categoria); });
  var chips = $("#doc-categorias");
  chips.innerHTML = cats.map(function (c) {
    var n = c === "Todos" ? docs.length : docs.filter(function (d) { return d.categoria === c; }).length;
    return '<button type="button" class="chip" aria-pressed="' + (c === "Todos") + '" data-cat="' + esc(c) + '">' + esc(c) + "<span>" + n + "</span></button>";
  }).join("");
  var normal = function (s) { return String(s).toLowerCase().normalize("NFD").replace(/[̀-ͯ]/g, ""); };
  var iconoBajar = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 4v11m0 0-4.5-4.5M12 15l4.5-4.5M5 20h14"/></svg>';
  function pintarDocs() {
    var q = normal(filtro.q.trim());
    var lista = docs.filter(function (d) {
      return (filtro.cat === "Todos" || d.categoria === filtro.cat) &&
        (!q || normal(d.titulo + " " + d.descripcion + " " + d.categoria + " " + d.fecha).indexOf(q) >= 0);
    });
    $("#doc-conteo").textContent = lista.length === 1 ? "1 documento" : lista.length + " documentos";
    $("#doc-lista").innerHTML = lista.length ? lista.map(function (d, i) {
      var ext = (d.archivo.split(".").pop() || "pdf").toUpperCase();
      return '<li class="doc" style="--vt: doc-' + docs.indexOf(d) + '">' +
        '<span class="doc__icono" data-cat="' + esc(d.categoria) + '">' + esc(ext) + "</span>" +
        "<div><h3>" + esc(d.titulo) + "</h3><p>" + esc(d.descripcion || "") + '</p><p class="doc__meta">' + esc(d.categoria) + ". Publicado el " + fechaLarga(d.fecha) + "</p></div>" +
        '<a class="doc__bajar" href="' + esc(d.archivo) + '" download>' + iconoBajar + "Descargar</a></li>";
    }).join("") : '<li class="docs__vacio">No hay documentos con ese filtro. Pruebe otra categoría o borre la búsqueda.</li>';
  }
  function conTransicion(fn) { if (document.startViewTransition && !quieto) document.startViewTransition(fn); else fn(); }
  chips.addEventListener("click", function (e) {
    var b = e.target.closest(".chip"); if (!b) return;
    chips.querySelectorAll(".chip").forEach(function (c) { c.setAttribute("aria-pressed", c === b); });
    filtro.cat = b.dataset.cat; conTransicion(pintarDocs);
  });
  var tBuscar;
  $("#doc-buscar").addEventListener("input", function (e) {
    clearTimeout(tBuscar); tBuscar = setTimeout(function () { filtro.q = e.target.value; conTransicion(pintarDocs); }, 150);
  });
  pintarDocs();

  /* ---------- Comunicados + diálogo ---------- */
  var dlg = $("#dialogo");
  $("#lista-comunicados").innerHTML = comunicados.length ? comunicados.map(function (c, i) {
    return '<button type="button" class="comunicado" data-i="' + i + '"><time datetime="' + esc(c.fecha) + '">' + fechaLarga(c.fecha) + "</time>" +
      "<h3>" + esc(c.titulo) + "</h3><p>" + esc(c.resumen) + '</p><span class="comunicado__leer">Leer comunicado</span></button>';
  }).join("") : '<p class="intro">Aún no hay comunicados publicados.</p>';
  $("#lista-comunicados").addEventListener("click", function (e) {
    var b = e.target.closest(".comunicado"); if (!b) return;
    var c = comunicados[+b.dataset.i];
    $("#dialogo-fecha").textContent = fechaLarga(c.fecha);
    $("#dialogo-titulo").textContent = c.titulo;
    $("#dialogo-texto").innerHTML = (c.texto || [c.resumen]).map(function (p) { return "<p>" + esc(p) + "</p>"; }).join("");
    var pdf = $("#dialogo-pdf"); pdf.hidden = !c.archivo; if (c.archivo) pdf.href = c.archivo;
    if (dlg.showModal) dlg.showModal(); else dlg.setAttribute("open", "");
  });
  dlg.addEventListener("click", function (e) { if (e.target === dlg) dlg.close(); });

  /* ---------- Tarifas ---------- */
  $("#periodo").textContent = D.periodoTarifas || "Tarifas vigentes";
  var servicios = Object.keys(D.tarifas || {});
  var pest = $("#tarifa-pestanas");
  pest.innerHTML = servicios.map(function (s, i) {
    return '<button type="button" role="tab" class="pestana" aria-selected="' + (i === 0) + '" data-s="' + esc(s) + '">' + esc(s) + "</button>";
  }).join("");
  var pesos = function (v) { return v == null ? '<span class="vacio">Por publicar</span>' : "$" + v.toLocaleString("es-CO", { minimumFractionDigits: 2, maximumFractionDigits: 2 }); };
  function pintarTarifa(s) {
    $("#tarifa-tabla tbody").innerHTML = (D.tarifas[s] || []).map(function (f) {
      return '<tr><th scope="row">' + esc(f.uso) + "</th><td>" + pesos(f.fijo) + "</td><td>" + pesos(f.basico) + "</td><td>" + pesos(f.complementario) + "</td><td>" + pesos(f.suntuario) + "</td></tr>";
    }).join("");
  }
  pest.addEventListener("click", function (e) {
    var b = e.target.closest(".pestana"); if (!b) return;
    pest.querySelectorAll(".pestana").forEach(function (x) { x.setAttribute("aria-selected", x === b); });
    conTransicion(function () { pintarTarifa(b.dataset.s); });
  });
  if (servicios.length) pintarTarifa(servicios[0]);

  /* ---------- Avisos ---------- */
  var hoy = new Date(); hoy.setHours(0, 0, 0, 0);
  var avisos = (D.avisos || []).slice().sort(function (a, b) { return a.fecha < b.fecha ? 1 : -1; });
  $("#lista-avisos").innerHTML = avisos.length ? avisos.map(function (a) {
    var f = fecha(a.fecha);
    return '<li class="aviso' + (f < hoy ? " aviso--pasado" : "") + '"><p class="aviso__fecha"><b>' + f.getDate() + "</b><span>" + MESES[f.getMonth()].slice(0, 3) + " " + f.getFullYear() + "</span></p>" +
      "<div><h3>" + esc(a.titulo) + "</h3><p>" + esc(a.detalle) + (a.sectores ? " Sectores: " + esc(a.sectores) + "." : "") + "</p></div></li>";
  }).join("") : '<li class="avisos__vacio">No hay cortes programados. Si su casa se queda sin agua, repórtelo en el formulario de atención.</li>';

  /* ---------- Calidad del agua (IRCA) ---------- */
  var c = D.calidad || {}, arco = $("#irca-arco");
  if (typeof c.irca === "number") {
    var v = c.irca, nivel = v <= 5 ? "Sin riesgo" : v <= 14 ? "Riesgo bajo" : v <= 35 ? "Riesgo medio" : "Riesgo alto";
    arco.style.stroke = v <= 5 ? "var(--hoja)" : v <= 14 ? "#b9d531" : v <= 35 ? "var(--alerta)" : "var(--peligro)";
    $("#irca-cifra").textContent = v.toLocaleString("es-CO") + " %";
    $("#irca-texto").textContent = nivel + ". " + [c.mes, c.laboratorio].filter(Boolean).join(", ");
    var llenarArco = function () { arco.style.strokeDashoffset = 1 - Math.max(Math.min(v, 100), 2) / 100; };
    if ("IntersectionObserver" in window) {
      var io = new IntersectionObserver(function (en) { if (en[0].isIntersecting) { llenarArco(); io.disconnect(); } }, { threshold: .5 });
      io.observe(arco);
    } else llenarArco();
  } else {
    $("#irca-texto").textContent = "El resultado del mes se publicará aquí cuando llegue el informe del laboratorio.";
  }

  /* ---------- Preguntas frecuentes ---------- */
  $("#faq").innerHTML = (D.preguntas || []).map(function (q) { return "<details><summary>" + esc(q.p) + "</summary><p>" + esc(q.r) + "</p></details>"; }).join("");

  /* ---------- Contacto ---------- */
  $("#txt-tel").textContent = D.telefono; $("#canal-tel").href = "tel:+57" + num(D.telefono);
  $("#txt-correo").textContent = D.correoPqrs; $("#canal-correo").href = "mailto:" + D.correoPqrs;
  $("#txt-horario").innerHTML = (D.horario || []).map(esc).join("<br>");
  $("#pie-razon").textContent = D.razonSocial + (D.nit ? ". NIT " + D.nit : "");
  $("#pie-dir").textContent = D.direccion;
  $("#pie-tel").textContent = D.telefono; $("#pie-tel").href = "tel:+57" + num(D.telefono);
  $("#pie-correo").textContent = D.correoGeneral; $("#pie-correo").href = "mailto:" + D.correoGeneral;
  $("#anio").textContent = new Date().getFullYear();

  /* ---------- Formulario PQRS ---------- */
  var form = $("#form"), err = $("#error");
  var nombres = { nombre: "nombre", direccion: "dirección", telefono: "teléfono", mensaje: "descripción" };
  form.addEventListener("submit", function (e) {
    e.preventDefault();
    var via = e.submitter ? e.submitter.value : "correo", f = new FormData(form);
    var faltan = Object.keys(nombres).filter(function (k) { return !String(f.get(k) || "").trim(); });
    form.querySelectorAll("[aria-invalid]").forEach(function (el) { el.removeAttribute("aria-invalid"); });
    if (faltan.length) {
      faltan.forEach(function (k) { form.elements[k].setAttribute("aria-invalid", "true"); });
      err.textContent = "Para enviar, complete: " + faltan.map(function (k) { return nombres[k]; }).join(", ") + ".";
      err.hidden = false; form.elements[faltan[0]].focus(); return;
    }
    err.hidden = true;
    var tipo = f.get("tipo");
    var cuerpo = "Tipo: " + tipo + "\nNombre: " + f.get("nombre") + "\nCódigo de suscriptor: " + (f.get("codigo") || "No indicado") +
      "\nDirección: " + f.get("direccion") + "\nTeléfono: " + f.get("telefono") + "\n\n" + f.get("mensaje");
    if (via === "whatsapp") window.open(wa(cuerpo), "_blank", "noopener");
    else location.href = "mailto:" + D.correoPqrs + "?subject=" + encodeURIComponent(tipo + " - " + f.get("nombre")) + "&body=" + encodeURIComponent(cuerpo);
  });
})();
