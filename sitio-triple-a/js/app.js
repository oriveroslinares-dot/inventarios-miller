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
  var titulos = { normal: "Servicio normal", alerta: "Alerta", programado: "Corte programado", interrumpido: "Servicio interrumpido" };
  var est = titulos[D.estado] ? D.estado : "normal";
  var tituloEst = D.tituloEstado && est !== "normal" ? D.tituloEstado : titulos[est];
  $("#estado-punto").dataset.estado = est;
  $("#estado-titulo").textContent = tituloEst;
  $("#estado-mensaje").textContent = D.mensajeEstado || "";

  /* ---------- Cinta del último comunicado ---------- */
  var comunicados = (D.noticias || D.comunicados || []).slice().sort(function (a, b) { return a.fecha < b.fecha ? 1 : -1; });
  if (est !== "normal") {
    // Mientras haya alerta o corte, la cinta muestra el estado del servicio en lugar de la última noticia
    var cinta = $("#cinta");
    cinta.hidden = false; cinta.href = "#avisos"; cinta.classList.add("cinta--alerta"); cinta.dataset.estado = est;
    $(".cinta__rotulo").textContent = tituloEst;
    $("#cinta-texto").textContent = D.mensajeEstado || "";
    $("#cinta-fecha").textContent = "Ver recomendaciones";
  } else if (comunicados.length) {
    $("#cinta").hidden = false;
    $("#cinta-texto").textContent = comunicados[0].titulo;
    $("#cinta-fecha").textContent = fechaLarga(comunicados[0].fecha);
  }

  /* ---------- Recorrido del agua: avanza con el scroll ---------- */
  var rec = $("#recorrido"), pasos = Array.prototype.slice.call(document.querySelectorAll(".paso")), tubo = $("#tubo-agua");
  document.querySelectorAll("[data-proveedor]").forEach(function (el) { el.textContent = D.proveedorAgua || "nuestro proveedor"; });
  var NUMS = ["Cero", "Un", "Dos", "Tres", "Cuatro", "Cinco", "Seis", "Siete", "Ocho", "Nueve", "Diez"];
  document.querySelectorAll("[data-macros]").forEach(function (el) { var n = +D.macromedidores || 0; el.textContent = NUMS[n] || String(n); });
  // Banda de aseo para todo Facatativá
  var aseoN = (D.suscriptores || {}).aseo;
  document.querySelectorAll("[data-suscriptores-aseo]").forEach(function (el) { if (aseoN) el.textContent = (Math.floor(aseoN / 100) * 100).toLocaleString("es-CO"); });
  var aseoBtn = $("#aseo-solicitar");
  if (aseoBtn) aseoBtn.href = wa("Hola, Triple A. Quiero el servicio de aseo. Mi dirección en Facatativá es: ");
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

  /* ---------- Interruptor de pagos (datos.js > pagos.mostrar) ---------- */
  var conPagos = !!(D.pagos && D.pagos.mostrar);
  document.querySelectorAll("[data-pagos]").forEach(function (el) { el.hidden = !conPagos; });
  document.querySelectorAll("[data-sin-pagos]").forEach(function (el) { el.hidden = conPagos; });

  /* ---------- Pague su factura ---------- */
  (function () {
    var P = D.pagos || {}, form = $("#pago"), cont = $("#medios"), det = $("#medio-detalle"), errP = $("#pago-error");
    if (!form) return;
    $("#pago-limite").textContent = P.fechaLimite || "";
    var medios = [];
    if (P.enlacePSE) medios.push({ id: "pse", nombre: "PSE", detalle: "Débito desde su banco", enlace: P.enlacePSE });
    (P.medios || []).forEach(function (m) { medios.push(m); });
    medios.push({ id: "oficina", nombre: "Oficina", detalle: "Efectivo, en persona" });
    var elegido = null;
    cont.innerHTML = medios.map(function (m, i) {
      return '<button type="button" class="medio" role="radio" aria-checked="false" data-i="' + i + '"><b>' + esc(m.nombre) + "</b><small>" + esc(m.detalle) + "</small></button>";
    }).join("");
    var dato = function (rotulo, valor, copiable) {
      return '<div class="dato"><div><small>' + esc(rotulo) + "</small><b>" + esc(valor) + "</b></div>" +
        (copiable ? '<button type="button" class="copiar" data-copiar="' + esc(valor) + '">Copiar</button>' : "") + "</div>";
    };
    function valorTexto() { var v = num(form.elements.valor.value); return v ? "$" + (+v).toLocaleString("es-CO") : ""; }
    function pintarMedio() {
      var m = elegido, h = "";
      if (!m) { det.innerHTML = ""; return; }
      if (m.id === "pse") {
        h = '<p class="medio__nota">Será dirigido a la página segura de PSE para pagar desde su cuenta bancaria. Escriba su código de suscriptor como referencia.</p>' +
          '<a class="boton boton--agua" href="' + esc(m.enlace) + '" target="_blank" rel="noopener">Ir a pagar con PSE</a>';
      } else if (m.id === "oficina") {
        h = dato("Dirección", D.direccion) + dato("Horario", (D.horario || []).join(". ")) +
          '<p class="medio__nota">Lleve su factura o su código de suscriptor. En la oficina le entregan el comprobante; no necesita enviarlo por WhatsApp.</p>';
      } else if (m.numero) {
        h = dato(m.detalle, m.numero, true) + (m.titular ? dato("A nombre de", m.titular) : "") + (valorTexto() ? dato("Valor a enviar", valorTexto(), false) : "") +
          '<p class="medio__nota">En la descripción de la transferencia escriba su código de suscriptor.</p>';
      } else {
        h = '<p class="medio__nota">Estamos actualizando los datos de ' + esc(m.nombre) + ". Solicítelos en la línea " + esc(D.telefono) + " o pague en la oficina.</p>";
      }
      det.innerHTML = h;
    }
    function revisar() {
      var p1 = num(form.elements.codigo.value).length > 0 && num(form.elements.valor.value).length > 0;
      form.querySelector('[data-paso="1"]').classList.toggle("listo", p1);
      form.querySelector('[data-paso="2"]').classList.toggle("listo", !!elegido);
    }
    cont.addEventListener("click", function (e) {
      var b = e.target.closest(".medio"); if (!b) return;
      cont.querySelectorAll(".medio").forEach(function (x) { x.setAttribute("aria-checked", x === b); });
      elegido = medios[+b.dataset.i]; pintarMedio(); revisar();
    });
    cont.addEventListener("keydown", function (e) {
      if (["ArrowRight", "ArrowDown", "ArrowLeft", "ArrowUp"].indexOf(e.key) < 0) return;
      var bs = Array.prototype.slice.call(cont.querySelectorAll(".medio")), i = bs.indexOf(document.activeElement);
      if (i < 0) return; e.preventDefault();
      var n = bs[(i + (e.key === "ArrowRight" || e.key === "ArrowDown" ? 1 : bs.length - 1)) % bs.length]; n.focus(); n.click();
    });
    form.elements.valor.addEventListener("input", function (e) {
      var v = num(e.target.value); e.target.value = v ? (+v).toLocaleString("es-CO") : ""; revisar();
      if (elegido && elegido.numero) pintarMedio();
    });
    form.elements.codigo.addEventListener("input", revisar);
    form.addEventListener("input", function (e) { e.target.removeAttribute("aria-invalid"); });
    var unir = function (xs) { return xs.length > 1 ? xs.slice(0, -1).join(", ") + " y " + xs[xs.length - 1] : xs[0]; };
    det.addEventListener("click", function (e) {
      var b = e.target.closest(".copiar"); if (!b) return;
      var listo = function () { b.textContent = "Copiado"; b.classList.add("copiado"); setTimeout(function () { b.textContent = "Copiar"; b.classList.remove("copiado"); }, 1800); };
      if (navigator.clipboard) navigator.clipboard.writeText(b.dataset.copiar).then(listo, listo); else listo();
    });
    form.addEventListener("submit", function (e) {
      e.preventDefault();
      form.querySelectorAll("[aria-invalid]").forEach(function (x) { x.removeAttribute("aria-invalid"); });
      var faltan = [];
      if (!num(form.elements.codigo.value)) faltan.push(["codigo", "su código de suscriptor"]);
      if (!num(form.elements.valor.value)) faltan.push(["valor", "el valor pagado"]);
      if (!elegido) faltan.push([null, "el medio de pago"]);
      if (faltan.length) {
        faltan.forEach(function (f) { if (f[0]) form.elements[f[0]].setAttribute("aria-invalid", "true"); });
        errP.textContent = "Para enviar el comprobante, indique " + unir(faltan.map(function (f) { return f[1]; })) + ".";
        errP.hidden = false; (faltan[0][0] ? form.elements[faltan[0][0]] : cont.querySelector(".medio")).focus(); return;
      }
      errP.hidden = true;
      window.open(wa("Hola, Triple A. Pagué mi factura.\nCódigo de suscriptor: " + num(form.elements.codigo.value) +
        "\nValor: " + valorTexto() + "\nMedio de pago: " + elegido.nombre + "\nAdjunto el comprobante."), "_blank", "noopener");
    });
  })();

  /* ---------- Publicaciones de Facebook (plugin oficial) ---------- */
  (function () {
    var sec = $("#facebook"), marco = $("#fb-marco");
    if (!sec || !D.facebook) return;
    sec.hidden = false;
    $("#fb-seguir").href = D.facebook; $("#fb-respaldo-link").href = D.facebook;
    var puesto = false;
    function cargar() {
      if (puesto) return; puesto = true;
      var ancho = Math.max(180, Math.min(500, Math.floor(marco.clientWidth)));
      var src = "https://www.facebook.com/plugins/page.php?href=" + encodeURIComponent(D.facebook) +
        "&tabs=timeline&width=" + ancho + "&height=700&small_header=false&adapt_container_width=true&hide_cover=false&show_facepile=false&locale=es_LA";
      var f = document.createElement("iframe");
      f.src = src; f.title = "Publicaciones de Triple A en Facebook"; f.loading = "lazy";
      f.setAttribute("allow", "encrypted-media; clipboard-write; web-share");
      f.addEventListener("load", function () { f.classList.add("listo"); $("#fb-cargando").hidden = true; });
      marco.insertBefore(f, marco.firstChild);
    }
    if ("IntersectionObserver" in window) {
      var io = new IntersectionObserver(function (en) { if (en[0].isIntersecting) { cargar(); io.disconnect(); } }, { rootMargin: "600px 0px" });
      io.observe(sec);
    } else cargar();
  })();

  /* ---------- Asistente flotante ---------- */
  (function () {
    var caja = $("#ayuda"), boton = $("#ayuda-boton"), panel = $("#ayuda-panel");
    if (!caja) return;
    $("#ayuda-wa").href = wa("Hola, Triple A. Necesito ayuda con ");
    function mostrar() { caja.classList.toggle("visible", window.scrollY > window.innerHeight * 0.6); }
    mostrar(); window.addEventListener("scroll", mostrar, { passive: true });
    function abrir(si) { panel.hidden = !si; boton.setAttribute("aria-expanded", si); }
    boton.addEventListener("click", function () { abrir(panel.hidden); });
    panel.addEventListener("click", function (e) { if (e.target.closest("a")) abrir(false); });
    document.addEventListener("keydown", function (e) { if (e.key === "Escape" && !panel.hidden) { abrir(false); boton.focus(); } });
    document.addEventListener("click", function (e) { if (!panel.hidden && !caja.contains(e.target)) abrir(false); });
  })();

  /* ---------- Mapa de rutas interactivo (zoom y desplazamiento) ---------- */
  (function () {
    var mapa = $("#mapa"), lienzo = $("#mapa-lienzo"), aviso = $("#mapa-aviso");
    if (!mapa || !lienzo) return;
    var IW = 1672, IH = 941, AR = IW / IH, MAX = 4;
    // Centro aproximado de cada ruta en la imagen original (píxeles)
    var RUTAS = { "1": { x: 915, y: 420, s: 2.3 }, "2": { x: 610, y: 430, s: 2.1 } };
    var W, H, lw, lh, ox, oy, s = 1, x = 0, y = 0;
    function medir() {
      W = mapa.clientWidth; H = mapa.clientHeight;
      lw = Math.min(W, H * AR); lh = lw / AR; ox = (W - lw) / 2; oy = (H - lh) / 2;
      lienzo.style.width = lw + "px"; lienzo.style.height = lh + "px";
      lienzo.style.left = ox + "px"; lienzo.style.top = oy + "px";
    }
    function limitar() {
      s = Math.min(MAX, Math.max(1, s));
      var cw = lw * s, ch = lh * s;
      x = cw >= W ? Math.min(-ox, Math.max(W - ox - cw, x)) : (W - cw) / 2 - ox;
      y = ch >= H ? Math.min(-oy, Math.max(H - oy - ch, y)) : (H - ch) / 2 - oy;
    }
    function aplicar(animar) {
      limitar();
      lienzo.classList.toggle("animar", !!animar && !quieto);
      lienzo.style.transform = "translate(" + x + "px," + y + "px) scale(" + s + ")";
      mapa.classList.toggle("ampliado", s > 1.01);
    }
    function zoomEn(px, py, nuevo, animar) {
      nuevo = Math.min(MAX, Math.max(1, nuevo));
      x = px - ox - (px - ox - x) * (nuevo / s);
      y = py - oy - (py - oy - y) * (nuevo / s);
      s = nuevo; aplicar(animar);
    }
    function marcarRuta(r) { document.querySelectorAll(".ruta-btn[data-ruta]").forEach(function (b) { b.setAttribute("aria-pressed", b.dataset.ruta === r); }); }
    function irA(r) {
      var t = RUTAS[r]; if (!t) return;
      s = t.s; x = W / 2 - ox - (t.x / IW) * lw * s; y = H / 2 - oy - (t.y / IH) * lh * s;
      aplicar(true); marcarRuta(r); usado();
    }
    function verTodo() { s = 1; x = 0; y = 0; aplicar(true); marcarRuta(null); }
    function usado() { mapa.classList.add("usado"); }
    var tAviso;
    function avisar(txt) { aviso.textContent = txt; aviso.classList.add("visible"); clearTimeout(tAviso); tAviso = setTimeout(function () { aviso.classList.remove("visible"); }, 1400); }
    var punto = function (e) { var r = mapa.getBoundingClientRect(); return { x: e.clientX - r.left, y: e.clientY - r.top }; };

    medir(); aplicar(false);
    window.addEventListener("resize", function () { var rs = s; medir(); s = rs; aplicar(false); });

    // Botones
    mapa.querySelector(".mapa__controles").addEventListener("click", function (e) {
      var b = e.target.closest("button"); if (!b) return; usado();
      var a = b.dataset.accion;
      if (a === "mas") zoomEn(W / 2, H / 2, s * 1.5, true);
      else if (a === "menos") zoomEn(W / 2, H / 2, s / 1.5, true);
      else if (a === "todo") verTodo();
      else if (a === "completa") pantallaCompleta();
    });
    document.querySelectorAll(".ruta-btn[data-ruta]").forEach(function (b) {
      b.addEventListener("click", function () { if (b.getAttribute("aria-pressed") === "true") verTodo(); else irA(b.dataset.ruta); });
    });

    // Rueda: con Ctrl/⌘ acerca; sin Ctrl deja hacer scroll a la página
    mapa.addEventListener("wheel", function (e) {
      if (!(e.ctrlKey || e.metaKey) && !document.fullscreenElement && !mapa.classList.contains("pantalla")) {
        if (s === 1) avisar("Use Ctrl + rueda del mouse para acercar"); return;
      }
      e.preventDefault(); usado(); var p = punto(e);
      zoomEn(p.x, p.y, s * Math.exp(-e.deltaY * 0.0022), false);
    }, { passive: false });

    // Arrastrar y pellizcar (mouse y táctil)
    var ptrs = new Map(), inicio = null;
    mapa.addEventListener("pointerdown", function (e) {
      if (e.target.closest(".mapa__controles")) return;
      ptrs.set(e.pointerId, punto(e)); mapa.setPointerCapture(e.pointerId);
      inicio = ptrs.size === 2 ? pellizcoInicio() : { px: punto(e).x, py: punto(e).y, x: x, y: y };
      if (s > 1) mapa.classList.add("arrastrando");
    });
    function pellizcoInicio() {
      var p = Array.from(ptrs.values());
      return { d: Math.hypot(p[0].x - p[1].x, p[0].y - p[1].y), cx: (p[0].x + p[1].x) / 2, cy: (p[0].y + p[1].y) / 2, s: s, x: x, y: y };
    }
    mapa.addEventListener("pointermove", function (e) {
      if (!ptrs.has(e.pointerId)) return;
      ptrs.set(e.pointerId, punto(e));
      if (ptrs.size === 2 && inicio && inicio.d) {
        var p = Array.from(ptrs.values()), d = Math.hypot(p[0].x - p[1].x, p[0].y - p[1].y);
        var cx = (p[0].x + p[1].x) / 2, cy = (p[0].y + p[1].y) / 2;
        s = inicio.s; x = inicio.x + (cx - inicio.cx); y = inicio.y + (cy - inicio.cy);
        zoomEn(cx, cy, inicio.s * d / inicio.d, false); usado();
      } else if (ptrs.size === 1 && inicio && s > 1) {
        var q = punto(e); x = inicio.x + (q.x - inicio.px); y = inicio.y + (q.y - inicio.py); aplicar(false); usado();
      }
    });
    function soltar(e) {
      ptrs.delete(e.pointerId); mapa.classList.remove("arrastrando");
      if (ptrs.size === 1) { var q = Array.from(ptrs.values())[0]; inicio = { px: q.x, py: q.y, x: x, y: y }; } else if (!ptrs.size) inicio = null;
    }
    mapa.addEventListener("pointerup", soltar); mapa.addEventListener("pointercancel", soltar);

    // Doble clic o doble toque: acercar (o volver si ya está muy cerca)
    var ultimoToque = 0;
    function dobleToque(p) { usado(); if (s >= MAX - 0.1) verTodo(); else zoomEn(p.x, p.y, s * 2, true); }
    mapa.addEventListener("dblclick", function (e) { if (!e.target.closest(".mapa__controles")) dobleToque(punto(e)); });
    mapa.addEventListener("pointerup", function (e) {
      if (e.pointerType !== "touch") return;
      var t = Date.now(); if (t - ultimoToque < 300) { dobleToque(punto(e)); ultimoToque = 0; } else ultimoToque = t;
    });

    // Teclado
    mapa.addEventListener("keydown", function (e) {
      var paso = 60, k = e.key;
      if (k === "+" || k === "=") zoomEn(W / 2, H / 2, s * 1.4, true);
      else if (k === "-" || k === "_") zoomEn(W / 2, H / 2, s / 1.4, true);
      else if (k === "0") verTodo();
      else if (k === "ArrowLeft") { x += paso; aplicar(true); }
      else if (k === "ArrowRight") { x -= paso; aplicar(true); }
      else if (k === "ArrowUp") { y += paso; aplicar(true); }
      else if (k === "ArrowDown") { y -= paso; aplicar(true); }
      else if (k === "Escape" && mapa.classList.contains("pantalla")) { salirPantalla(); }
      else return;
      e.preventDefault(); usado();
    });

    // Pantalla completa (con respaldo para iPhone)
    function pantallaCompleta() {
      if (document.fullscreenElement || mapa.classList.contains("pantalla")) { salirPantalla(); return; }
      if (mapa.requestFullscreen) mapa.requestFullscreen().catch(function () { mapa.classList.add("pantalla"); recalcular(); });
      else { mapa.classList.add("pantalla"); recalcular(); }
    }
    function salirPantalla() {
      if (document.fullscreenElement) document.exitFullscreen();
      mapa.classList.remove("pantalla"); recalcular();
    }
    function recalcular() { requestAnimationFrame(function () { var rs = s; medir(); s = rs; aplicar(false); }); }
    document.addEventListener("fullscreenchange", recalcular);
  })();

  /* ---------- Galería: trabajando en el barrio ---------- */
  (function () {
    var fotos = D.galeria || [], sec = $("#galeria"); if (!sec || !fotos.length) return;
    sec.hidden = false;
    $("#galeria-lista").innerHTML = fotos.map(function (f, i) {
      return '<li class="galeria__item' + (i === 0 ? " destacada" : "") + '"><button type="button" class="foto" data-i="' + i + '">' +
        '<span class="foto__marco"><img src="' + esc(f.foto) + '" alt="' + esc(f.titulo) + '" loading="lazy" decoding="async">' +
        (f.servicio ? '<span class="foto__etiqueta">' + esc(f.servicio) + "</span>" : "") + "</span>" +
        '<span class="foto__texto"><span class="foto__titulo">' + esc(f.titulo) + "</span>" + (f.descripcion ? '<span class="foto__desc">' + esc(f.descripcion) + "</span>" : "") +
        (f.fecha ? '<time class="foto__fecha" datetime="' + esc(f.fecha) + '">' + fechaLarga(f.fecha) + "</time>" : "") +
        '<span class="foto__ver">Ver foto completa</span></span></button></li>';
    }).join("");
    var visor = $("#foto-visor");
    $("#galeria-lista").addEventListener("click", function (e) {
      var b = e.target.closest(".foto"); if (!b) return;
      var f = fotos[+b.dataset.i];
      $("#foto-visor-img").src = f.fotoGrande || f.foto; $("#foto-visor-img").alt = f.titulo;
      $("#foto-visor-titulo").textContent = f.titulo; $("#foto-visor-desc").textContent = f.descripcion || "";
      if (visor.showModal) visor.showModal(); else visor.setAttribute("open", "");
    });
    visor.addEventListener("click", function (e) { if (e.target === visor) visor.close(); });
  })();

  /* ---------- Video aéreo: se reproduce solo (sin sonido) cuando está a la vista ---------- */
  (function () {
    var v = $("#video-aereo"); if (!v || quieto || !("IntersectionObserver" in window)) return;
    var pausadoPorUsuario = false;
    v.addEventListener("pause", function () { if (v.dataset.auto !== "1") pausadoPorUsuario = true; v.dataset.auto = ""; });
    new IntersectionObserver(function (en) {
      if (en[0].isIntersecting) { if (!pausadoPorUsuario) { v.preload = "auto"; var p = v.play(); if (p && p.catch) p.catch(function () {}); } }
      else if (!v.paused) { v.dataset.auto = "1"; v.pause(); }
    }, { threshold: 0.4 }).observe(v);
  })();

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

  /* ---------- Noticias + diálogo ---------- */
  var dlg = $("#dialogo"), filtroNot = "Todas";
  var MES3 = ["ene", "feb", "mar", "abr", "may", "jun", "jul", "ago", "sep", "oct", "nov", "dic"];
  var tiposNot = ["Todas"];
  comunicados.forEach(function (n) { var t = n.tipo || "Comunicado"; if (tiposNot.indexOf(t) < 0) tiposNot.push(t); });
  var filtrosNot = $("#noticias-filtros");
  filtrosNot.innerHTML = tiposNot.length > 2 ? tiposNot.map(function (t) {
    return '<button type="button" class="chip" aria-pressed="' + (t === "Todas") + '" data-t="' + esc(t) + '">' + esc(t === "Comunicado" ? "Comunicados" : t === "Noticia" ? "Noticias" : t) + "</button>";
  }).join("") : "";
  function pintarNoticias() {
    var lista = comunicados.map(function (n, i) { return { n: n, i: i }; }).filter(function (x) { return filtroNot === "Todas" || (x.n.tipo || "Comunicado") === filtroNot; });
    $("#lista-noticias").innerHTML = lista.length ? lista.map(function (x) {
      var n = x.n, f = fecha(n.fecha), tipo = n.tipo || "Comunicado";
      return '<article class="noticia' + (tipo === "Comunicado" ? " noticia--comunicado" : "") + '">' +
        '<p class="noticia__fecha"><b>' + f.getDate() + "</b><span>" + MES3[f.getMonth()] + " " + f.getFullYear() + "</span></p>" +
        '<div><span class="noticia__tipo">' + esc(tipo) + "</span><h3>" + esc(n.titulo) + "</h3><p>" + esc(n.resumen) + '</p><div class="noticia__acciones">' +
        ((n.texto && n.texto.length) ? '<button type="button" class="noticia__accion" data-i="' + x.i + '">Leer completo</button>' : "") +
        (n.facebook ? '<a class="noticia__accion noticia__accion--fb" href="' + esc(n.facebook) + '" target="_blank" rel="noopener"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M13.5 21v-7.5h2.6l.4-3h-3V8.6c0-.9.3-1.5 1.5-1.5h1.6V4.4c-.3 0-1.2-.1-2.3-.1-2.3 0-3.9 1.4-3.9 4v2.2H7.8v3h2.6V21h3.1Z"/></svg>Ver en Facebook</a>' : "") +
        (n.archivo ? '<a class="noticia__accion" href="' + esc(n.archivo) + '" download>Descargar PDF</a>' : "") +
        "</div></div></article>";
    }).join("") : '<p class="noticias__vacio">Aún no hay publicaciones en esta categoría.</p>';
  }
  pintarNoticias();
  filtrosNot.addEventListener("click", function (e) {
    var b = e.target.closest(".chip"); if (!b) return;
    filtrosNot.querySelectorAll(".chip").forEach(function (c) { c.setAttribute("aria-pressed", c === b); });
    filtroNot = b.dataset.t; conTransicion(pintarNoticias);
  });
  $("#lista-noticias").addEventListener("click", function (e) {
    var b = e.target.closest("button.noticia__accion"); if (!b) return;
    var c = comunicados[+b.dataset.i];
    $("#dialogo-fecha").textContent = (c.tipo || "Comunicado") + ". " + fechaLarga(c.fecha);
    $("#dialogo-titulo").textContent = c.titulo;
    $("#dialogo-texto").innerHTML = (c.texto || [c.resumen]).map(function (p) { return "<p>" + esc(p) + "</p>"; }).join("");
    var pdf = $("#dialogo-pdf"); pdf.hidden = !c.archivo; if (c.archivo) pdf.href = c.archivo;
    if (dlg.showModal) dlg.showModal(); else dlg.setAttribute("open", "");
  });
  dlg.addEventListener("click", function (e) { if (e.target === dlg) dlg.close(); });

  /* ---------- Quiénes somos: cifras, representante legal y junta ---------- */
  (function () {
    var iniciales = function (nombre) { var p = String(nombre).trim().split(/\s+/); return ((p[0] || "")[0] + ((p.length > 2 ? p[p.length - 2] : p[1]) || "")[0]).toUpperCase(); };
    var avatar = function (per) { return '<span class="persona__avatar">' + (per.foto ? '<img src="' + esc(per.foto) + '" alt="">' : esc(iniciales(per.nombre))) + "</span>"; };
    var miles = function (n) { return Number(n).toLocaleString("es-CO"); };
    var su = D.suscriptores || {}, cifras = [];
    if (D.asociacionDesde || D.fundacion) cifras.push(["Asociación al servicio del barrio desde", D.asociacionDesde || fecha(D.fundacion).getFullYear()]);
    if (su.acueducto) cifras.push(["Suscriptores de acueducto", miles(su.acueducto)]);
    if (su.alcantarillado) cifras.push(["Suscriptores de alcantarillado", miles(su.alcantarillado)]);
    if (su.aseo) cifras.push(["Suscriptores de aseo", miles(su.aseo)]);
    $("#cifras").innerHTML = cifras.map(function (c) { return "<div><dt>" + esc(c[0]) + "</dt><dd>" + esc(c[1]) + "</dd></div>"; }).join("");
    var intro = "Somos una asociación de usuarios que trabaja por los servicios públicos del Barrio Cartagena" + (D.asociacionDesde ? " desde " + D.asociacionDesde : "") + ".";
    if (D.fundacion) intro += " El " + fechaLarga(D.fundacion) + " nos constituimos formalmente como prestador de acueducto y alcantarillado";
    if (D.aseoInicio) intro += (D.fundacion ? ", y desde " : " Desde ") + fecha(D.aseoInicio).getFullYear() + " prestamos el servicio de aseo en todo Facatativá";
    intro += ". Compramos el agua en bloque, la distribuimos por redes propias y tratamos las aguas residuales en nuestra PTAR. Los mismos suscriptores, reunidos en asamblea, eligen a la junta directiva.";
    $("#nosotros-intro").textContent = intro;
    var r = D.representanteLegal, s = D.suplente;
    if (r) {
      $("#representante").innerHTML = '<span class="representante__rotulo">' + esc(r.cargo || "Representante legal") + "</span>" + avatar(r) +
        "<h3>" + esc(r.nombre) + "</h3>" + (r.desde ? "<p>En el cargo desde el " + fechaLarga(r.desde) + ".</p>" : "") +
        (D.correoGeneral ? '<p>Contacto: <a href="mailto:' + esc(D.correoGeneral) + '" style="color:#fff">' + esc(D.correoGeneral) + "</a></p>" : "") +
        (s ? '<div class="representante__suplente">' + avatar(s) + "<div><b>" + esc(s.nombre) + "</b><small>" + esc(s.cargo) + "</small></div></div>" : "");
    } else $("#representante").hidden = true;
    $("#junta").innerHTML = (D.junta || []).map(function (m) {
      var rol = /presiden|secretar|tesor|fiscal/i.test(m.cargo) ? "directivo" : /vocal/i.test(m.cargo) ? "vocal" : "otro";
      return '<li class="miembro" data-rol="' + rol + '">' + avatar(m) + "<div><b>" + esc(m.nombre) + "</b><small>" + esc(m.cargo) + "</small></div></li>";
    }).join("");
    var fuente = [];
    fuente.push("Vigilados por la Superintendencia de Servicios Públicos Domiciliarios.");
    if (D.auditorExterno) fuente.push("Auditor externo de gestión y resultados: " + D.auditorExterno.nombre + (D.auditorExterno.vigencia ? " (" + D.auditorExterno.vigencia + ")" : "") + ".");
    if (D.rupsFecha) fuente.push("Información del Registro Único de Prestadores (RUPS), actualizado el " + fechaLarga(D.rupsFecha) + ".");
    $("#nosotros-fuente").textContent = fuente.join(" ");
  })();

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
    return '<li class="aviso' + (a.vigente ? " aviso--vigente" : f < hoy ? " aviso--pasado" : "") + '"><p class="aviso__fecha"><b>' + f.getDate() + "</b><span>" + MESES[f.getMonth()].slice(0, 3) + " " + f.getFullYear() + "</span></p>" +
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
    arco.style.visibility = "hidden";
    $("#irca-texto").textContent = "El resultado del mes se publicará aquí cuando llegue el informe del laboratorio.";
  }

  /* ---------- Preguntas frecuentes ---------- */
  $("#faq").innerHTML = (D.preguntas || []).map(function (q) { return "<details><summary>" + esc(q.p) + "</summary><p>" + esc(q.r) + "</p></details>"; }).join("");

  /* ---------- Contacto ---------- */
  $("#txt-tel").textContent = D.telefono; $("#canal-tel").href = "tel:+57" + num(D.telefono);
  $("#txt-correo").textContent = D.correoPqrs; $("#canal-correo").href = "mailto:" + D.correoPqrs;
  $("#txt-horario").innerHTML = (D.horario || []).map(esc).join("<br>");
  $("#pie-razon").textContent = D.razonSocial + (D.nit ? ". NIT " + D.nit + "." : "");
  $("#pie-dir").textContent = D.direccion;
  $("#pie-tel").textContent = D.telefono + (D.telefonoFijo ? " / " + D.telefonoFijo : ""); $("#pie-tel").href = "tel:+57" + num(D.telefono);
  $("#pie-correo").textContent = D.correoGeneral; $("#pie-correo").href = "mailto:" + D.correoGeneral;
  if (D.facebook) { ["#canal-fb", "#pie-fb"].forEach(function (s) { var a = $(s); a.href = D.facebook; a.hidden = false; }); }
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
