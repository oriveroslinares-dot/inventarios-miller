/* ==========================================================
   DATOS EDITABLES DE LA PÁGINA — Triple A del Barrio Cartagena
   Edite este archivo para actualizar la página. No toque el HTML.
   Lo marcado "POR CONFIRMAR" debe revisarlo antes de publicar.
   ========================================================== */
window.TRIPLE_A = {
  empresa: "Triple A del Barrio Cartagena",
  // Datos oficiales tomados del certificado RUPS (Superservicios), actualizado el 27 de octubre de 2026
  razonSocial: "Asociación de Socios Suscriptores del Servicio de Acueducto, Alcantarillado y Aseo del Barrio Cartagena Facatativá",
  sigla: "Triple A del Barrio Cartagena Facatativá E.S.P.",
  nit: "832.001.989-1",
  asociacionDesde: 1977,           // año en que nació la asociación (dato de la empresa)
  fundacion: "1997-03-09",         // constitución formal como prestador, según el RUPS
  inicioOperaciones: "1997-08-15",
  rupsFecha: "2026-10-27",
  suscriptores: { acueducto: 1438, alcantarillado: 1420, aseo: 2882 },
  lema: "Construimos servicio, construimos comunidad.",

  // ---------- CONTACTO ----------
  direccion: "Calle 3 Sur No. 2-78, Barrio Cartagena, Facatativá, Cundinamarca",
  telefono: "315 744 3635",
  telefonoFijo: "(601) 843 0911",
  whatsapp: "573157443635",        // POR CONFIRMAR que esta línea tenga WhatsApp
  correoPqrs: "pqrs@tripleafacatativa.com.co",
  correoGeneral: "aaacartagena@tripleafacatativa.com.co",
  facebook: "https://www.facebook.com/p/Triple-A-del-Barrio-Cartagena-100083142559953/",
  horario: [
    "Lunes a viernes: 8:00 a. m. a 5:00 p. m.",
    "Sábados: 9:00 a. m. a 12:00 m."
  ],

  // ---------- PAGOS ----------
  // Complete los números reales. Si un medio no aplica, bórrelo de la lista.
  // Si "numero" queda vacío, la página le indica al usuario que lo pida en la oficina.
  pagos: {
    // mostrar: false oculta la sección "Pague su factura aquí" y sus botones en toda la página.
    // Cámbielo a true cuando tengan Wompi, PSE o cuentas para recibir pagos.
    mostrar: false,
    enlacePSE: "",                 // POR CONFIRMAR: enlace del botón PSE de su banco (déjelo vacío si no tiene)
    medios: [
      { id: "nequi", nombre: "Nequi", detalle: "Número celular", numero: "", titular: "" },          // POR CONFIRMAR
      { id: "bancolombia", nombre: "Bancolombia", detalle: "Cuenta de ahorros", numero: "", titular: "" } // POR CONFIRMAR
    ],
    fechaLimite: "Pague antes de la fecha límite impresa en su factura para evitar intereses de mora y la suspensión del servicio."
  },

  // ---------- ESTADO DEL SERVICIO ----------
  // estado: "normal" | "alerta" | "programado" | "interrumpido"
  //   "alerta" muestra la cinta naranja bajo la portada. Cuando pase la alerta, vuelva a "normal" y
  //   cambie el mensaje por: "Acueducto, alcantarillado y aseo funcionan con normalidad."
  estado: "alerta",
  tituloEstado: "Alerta naranja",
  mensajeEstado: "El servicio de acueducto puede presentar intermitencia. Almacene agua y úsela con moderación.",

  // ---------- RECORRIDO DEL AGUA ----------
  proveedorAgua: "Empresa de Aguas de Facatativá S.A.S. E.S.P.",  // compramos el agua en bloque
  macromedidores: 4,
  aseoInicio: "2009-03-10",        // inicio del servicio de aseo según el RUPS

  // ---------- CORTES Y AVISOS (fechas AAAA-MM-DD) ----------
  // vigente: true mantiene el aviso destacado aunque su fecha ya haya pasado (bórrelo al terminar la alerta).
  avisos: [
    {
      fecha: "2026-11-19",
      vigente: true,
      titulo: "Alerta naranja: posible intermitencia en el acueducto",
      detalle: "Mientras dure la alerta, el suministro de agua puede interrumpirse por momentos. Almacene agua en recipientes limpios y tapados, úsela con moderación, cierre bien las llaves y repórtenos cualquier fuga.",
      sectores: "Todo el barrio"
    },
    // { fecha: "2026-12-02", titulo: "Lavado de tanque", detalle: "Suspensión de 8:00 a. m. a 2:00 p. m.", sectores: "Todo el barrio" }
  ],

  // ---------- JUNTA DIRECTIVA Y REPRESENTANTE LEGAL ----------
  // Fuente: certificado RUPS del 27 de octubre de 2026. Por privacidad NO se publican números de cédula.
  // "foto" es opcional: suba la imagen a /img y escriba, por ejemplo, "img/junta/maria-elvira.jpg".
  representanteLegal: { nombre: "María Elvira Maldonado Martínez", cargo: "Representante legal", desde: "2026-02-22", foto: "" },
  suplente: { nombre: "Alba Rocío García Gómez", cargo: "Representante legal suplente", foto: "" },
  junta: [
    { nombre: "María Elvira Maldonado Martínez", cargo: "Presidente", foto: "" },
    { nombre: "Alba Rocío García Gómez", cargo: "Vicepresidente", foto: "" },
    { nombre: "Yenny Martínez", cargo: "Secretaria", foto: "" },   // actualizado por la empresa (el RUPS de oct. 2026 registra a Olga Lucía Chavarro Santana)
    { nombre: "Nubia Cristina Cruz Forero", cargo: "Tesorera", foto: "" },
    { nombre: "Daniel Duarte Duarte", cargo: "Vocal", foto: "" },
    { nombre: "José Enrique Caicedo Castañeda", cargo: "Vocal", foto: "" },
    { nombre: "Luz Stella Carrasco Alarcón", cargo: "Vocal", foto: "" }
  ],
  auditorExterno: { nombre: "AD Soluciones Integrales S.A.S.", vigencia: "abril de 2026 a abril de 2027" },

  // ---------- GALERÍA "TRABAJANDO EN EL BARRIO" ----------
  // Suba las fotos a img/galeria/. "foto" es la versión liviana y "fotoGrande" la que se abre al ampliar.
  // fecha es opcional (AAAA-MM-DD). La primera foto de la lista sale destacada.
  galeria: [
    {
      foto: "img/galeria/mantenimiento-alcantarillado-600.webp",
      fotoGrande: "img/galeria/mantenimiento-alcantarillado-900.webp",
      titulo: "Mantenimiento de la red de alcantarillado",
      descripcion: "Limpieza de pozos y tuberías con equipo de succión a presión, para evitar taponamientos y reboses en las calles del barrio.",
      servicio: "Alcantarillado",
      fecha: ""
    }
  ],

  // ---------- NOTICIAS ----------
  // tipo: "Comunicado" (oficial) o "Noticia". El texto completo se abre al pulsar "Leer".
  // facebook: pegue el enlace de la publicación en Facebook para mostrar el botón "Ver en Facebook".
  // archivo: PDF opcional en /documentos.
  noticias: [
    {
      tipo: "Comunicado",
      fecha: "2026-11-19",
      titulo: "Publicamos las tarifas vigentes 2026",
      resumen: "Las tarifas de acueducto, alcantarillado y aseo se ajustaron un 4,77 % por el IPC, desde el período de facturación julio–agosto de 2026.",
      texto: [
        "Informamos a los suscriptores que las tarifas de acueducto, alcantarillado y aseo vigentes a partir del período de facturación julio–agosto de 2026 tienen un incremento del 4,77 %, igual a la variación del Índice de Precios al Consumidor (IPC) de enero a junio de 2026 certificada por el DANE, como lo establece el artículo 125 de la Ley 142 de 1994.",
        "Los porcentajes de subsidio para los estratos 1 y 2 y de contribución para los usuarios comerciales e industriales, fijados por el Acuerdo Municipal de Facatativá 2022-2026, no cambian.",
        "Puede consultar todas las tarifas en la sección Tarifas de esta página o descargar el documento completo."
      ],
      facebook: "",
      archivo: "documentos/tarifas-vigentes-2026.pdf"
    },
    {
      tipo: "Comunicado",
      fecha: "2026-05-12",
      titulo: "No hay incremento en la tarifa de aprovechamiento",
      resumen: "Aclaramos a la comunidad que actualmente no se está aplicando ningún aumento en el cobro de aprovechamiento.",
      texto: [
        "La Asociación de Socios Suscriptores del Barrio Cartagena informa a la comunidad que, hasta el momento, no se está realizando ningún aumento en el cobro de la tarifa de aprovechamiento.",
        "Cualquier modificación tarifaria debe estar previamente regulada y aprobada conforme a la normatividad de la Superintendencia de Servicios Públicos Domiciliarios. La empresa adelanta consultas ante esa entidad para verificar la normativa vigente.",
        "Para resolver inquietudes o solicitar aclaraciones, comuníquese a la línea 315 744 3635, de lunes a viernes de 8:00 a. m. a 5:00 p. m., o al correo aaacartagena@tripleafacatativa.com.co."
      ],
      facebook: "",
      archivo: ""
    },
    {
      tipo: "Noticia",
      fecha: "2026-10-27",
      titulo: "Actualizamos nuestro registro ante la Superservicios",
      resumen: "Nuestro Registro Único de Prestadores (RUPS) quedó actualizado y la empresa figura como prestador operativo de acueducto, alcantarillado y aseo.",
      texto: [
        "El 27 de octubre de 2026 la Superintendencia de Servicios Públicos Domiciliarios aprobó la actualización de nuestro Registro Único de Prestadores de Servicios Públicos (RUPS).",
        "El registro confirma que la asociación está operativa desde 1997 y presta los servicios de acueducto, alcantarillado y aseo a los suscriptores del Barrio Cartagena, en Facatativá.",
        "También quedaron actualizados los datos de la representante legal, la junta directiva y el auditor externo de gestión y resultados. Puede consultarlos en la sección Quiénes somos."
      ],
      facebook: "",
      archivo: ""
    }
  ],

  // ---------- CENTRO DE DOCUMENTOS ----------
  // Suba cada PDF a la carpeta /documentos con el nombre que indique "archivo".
  // categoria: "Estados financieros" | "Informes de gestión" | "Tarifas" | "Asambleas" | "Normatividad" | "Comunicados"
  documentos: [
    { titulo: "Estados financieros 2025", categoria: "Estados financieros", fecha: "2026-03-31", archivo: "documentos/estados-financieros-2025.pdf", descripcion: "Estado de situación financiera, estado de resultados y notas." },
    { titulo: "Estados financieros 2024", categoria: "Estados financieros", fecha: "2025-03-31", archivo: "documentos/estados-financieros-2024.pdf", descripcion: "Estado de situación financiera, estado de resultados y notas." },
    { titulo: "Informe de gestión 2025", categoria: "Informes de gestión", fecha: "2026-03-31", archivo: "documentos/informe-gestion-2025.pdf", descripcion: "Resultados del año, inversiones y metas." },
    { titulo: "Tarifas vigentes 2026: acueducto, alcantarillado y aseo", categoria: "Tarifas", fecha: "2026-11-19", archivo: "documentos/tarifas-vigentes-2026.pdf", descripcion: "Vigentes desde el período julio–agosto de 2026. Ajuste del 4,77 % por IPC." },
    { titulo: "Acta de asamblea general 2026", categoria: "Asambleas", fecha: "2026-03-28", archivo: "documentos/acta-asamblea-2026.pdf", descripcion: "Decisiones de la asamblea de socios suscriptores." },
    { titulo: "Contrato de condiciones uniformes", categoria: "Normatividad", fecha: "2025-01-15", archivo: "documentos/contrato-condiciones-uniformes.pdf", descripcion: "Derechos y deberes de usuarios y empresa." },
    { titulo: "Estatutos de la asociación", categoria: "Normatividad", fecha: "2024-06-01", archivo: "documentos/estatutos.pdf", descripcion: "Reglas de funcionamiento de la asociación." }
  ],

  // ---------- TARIFAS VIGENTES 2026 ----------
  // Fuente: "Tarifas vigentes 2026" (documentos/tarifas-vigentes-2026.pdf), publicado en noviembre de 2026.
  // En las filas, use null en "básico" cuando la categoría paga tarifa única por m³ (sin tramos).
  tarifasVigentes: {
    vigencia: "A partir del período de facturación julio–agosto de 2026",
    ajuste: "Incremento del 4,77 %, igual a la variación del IPC de enero a junio de 2026 certificada por el DANE (Ley 142 de 1994, art. 125). Los porcentajes de subsidio y contribución del Acuerdo Municipal de Facatativá 2022-2026 no cambian.",
    pdf: "documentos/tarifas-vigentes-2026.pdf",
    acueducto: {
      filas: [
        ["Residencial", 12292.52, 1423.29, 2587.80],
        ["Comercial", 34419.06, null, 3881.70],
        ["Oficial", 16390.03, null, 2587.80],
        ["Industrial", 63522.05, null, 4406.84],
        ["Especial", 16390.03, null, 2587.80]
      ],
      referencia: "Costo de referencia del servicio: cargo fijo $16.390,03 y consumo $2.587,80/m³ (industrial: $27.030,66 y $3.389,86/m³)."
    },
    alcantarillado: {
      filas: [
        ["Residencial", 4891.50, 748.77, 1497.54],
        ["Comercial", 16305.01, null, 2246.31],
        ["Oficial", 6522.01, null, 1497.54],
        ["Industrial", 20218.22, null, 1946.80],
        ["Especial", 6522.01, null, 1497.54]
      ],
      referencia: "Costo de referencia del servicio: cargo fijo $6.522,01 y consumo $1.497,54/m³."
    },
    aseo: {
      filas: [
        ["Residencial estrato 1", 37064.37, "Subsidio 43,89 %"],
        ["Residencial estrato 2", 47427.28, "Subsidio 25,08 %"],
        ["Residencial estrato 3", 57956.87, "Sin subsidio"],
        ["Residencial estrato 4", 60082.18, "Sin subsidio"],
        ["Sin recolección puerta a puerta, estrato 1", 30638.01, "Subsidio 43,89 %"],
        ["Desocupado residencial, estrato 1", 15949.37, "Subsidio 43,89 %"],
        ["Desocupado residencial, estrato 2", 18458.84, "Subsidio 25,08 %"],
        ["Comercial", 97690.39, "Contribución 50 %"],
        ["Desocupado comercial", 36433.50, "Contribución 50 %"],
        ["Industrial", 88301.02, "Contribución 30 %"],
        ["Especial 1", 359255.61, "Sin subsidio"],
        ["Especial 2", 1338053.93, "Sin subsidio"],
        ["Especial 3", 2271237.51, "Sin subsidio"],
        ["Especial 4", 60424.08, "Sin subsidio"]
      ],
      referencia: "El servicio de aseo es un valor fijo por categoría (barrido, recolección, transporte, disposición final y aprovechamiento). Metodología Resolución CRA 853 de 2018."
    },
    comoLeer: [
      "La facturación es bimestral. El cargo fijo se paga en cada factura, aunque no haya consumo.",
      "Consumo básico: los primeros 22 m³ del período (11 m³ por mes, Resolución CRA 750 de 2016). Solo este tramo tiene subsidio para los usuarios residenciales.",
      "Desde 22 m³ en adelante (complementario y suntuario) se paga el valor completo, sin subsidio.",
      "Comercial, oficial, industrial y especial pagan una tarifa única por metro cúbico, sin tramos."
    ],
    informacion: [
      "Subsidio: descuento sobre el costo del servicio para los estratos 1 y 2. Contribución: valor adicional que pagan los usuarios comerciales e industriales para financiar esos subsidios. Los porcentajes los fija el Concejo Municipal de Facatativá.",
      "Las tarifas solo se vuelven a ajustar cuando el IPC acumule una variación de por lo menos el 3 % (Ley 142 de 1994, art. 125). Cualquier nuevo ajuste se publicará antes de aplicarse.",
      "Los usuarios industriales aforados (facturados por tonelada) reciben su liquidación por separado.",
      "Los valores están en pesos colombianos. No incluyen otros cobros como reconexión, intereses de mora o cuotas de financiación."
    ]
  },

  // ---------- COPIA DE COMPATIBILIDAD (no la borre) ----------
  // Algunos navegadores guardan una versión vieja de la página. Esa versión lee las tarifas en este formato.
  // Si cambian las tarifas, actualice también estos valores (complementario y suntuario = valor desde 22 m³).
  periodoTarifas: "Vigentes desde el período julio–agosto de 2026",
  tarifas: {
    "Acueducto": [
      { uso: "Residencial", fijo: 12292.52, basico: 1423.29, complementario: 2587.80, suntuario: 2587.80 },
      { uso: "Comercial (tarifa única)", fijo: 34419.06, basico: 3881.70, complementario: 3881.70, suntuario: 3881.70 },
      { uso: "Oficial (tarifa única)", fijo: 16390.03, basico: 2587.80, complementario: 2587.80, suntuario: 2587.80 },
      { uso: "Industrial (tarifa única)", fijo: 63522.05, basico: 4406.84, complementario: 4406.84, suntuario: 4406.84 },
      { uso: "Especial (tarifa única)", fijo: 16390.03, basico: 2587.80, complementario: 2587.80, suntuario: 2587.80 }
    ],
    "Alcantarillado": [
      { uso: "Residencial", fijo: 4891.50, basico: 748.77, complementario: 1497.54, suntuario: 1497.54 },
      { uso: "Comercial (tarifa única)", fijo: 16305.01, basico: 2246.31, complementario: 2246.31, suntuario: 2246.31 },
      { uso: "Oficial (tarifa única)", fijo: 6522.01, basico: 1497.54, complementario: 1497.54, suntuario: 1497.54 },
      { uso: "Industrial (tarifa única)", fijo: 20218.22, basico: 1946.80, complementario: 1946.80, suntuario: 1946.80 },
      { uso: "Especial (tarifa única)", fijo: 6522.01, basico: 1497.54, complementario: 1497.54, suntuario: 1497.54 }
    ]
  },

  // ---------- RECOLECCIÓN DE ASEO (POR CONFIRMAR) ----------
  // Barrio Cartagenita: 2 rutas, desde las 6:00 a. m. (ver img/rutas-aseo.webp)
  recoleccion: [
    { dia: "Lunes", tipo: "desde las 6:00 a. m." },
    { dia: "Miércoles", tipo: "desde las 6:00 a. m." },
    { dia: "Viernes", tipo: "desde las 6:00 a. m." }
  ],

  // ---------- CALIDAD DEL AGUA (IRCA) ----------
  // Deje irca en null mientras no haya resultado.
  calidad: { irca: null, mes: "", laboratorio: "" },

  // ---------- PREGUNTAS FRECUENTES ----------
  preguntas: [
    { p: "¿Puedo tener el servicio de aseo si no vivo en el Barrio Cartagena?", r: "Sí. Prestamos el servicio de aseo en todo Facatativá y es de libre competencia: usted elige su prestador. Escríbanos por WhatsApp o acérquese a la oficina con su factura de servicios y le explicamos cómo hacer el cambio." },
    { p: "¿De dónde viene el agua que llega a mi casa?", r: "Compramos agua potable en bloque a la Empresa de Aguas de Facatativá y la distribuimos por nuestras redes propias, controladas con cuatro macromedidores, hasta el medidor de cada predio." },
    { p: "¿Cuánto tiempo tienen para responder mi PQR?", r: "Máximo 15 días hábiles desde que la recibimos, según la Ley 142 de 1994. Si no respondemos a tiempo, se entiende resuelta a su favor (silencio administrativo positivo)." },
    { p: "¿Qué hago si mi factura llega muy alta?", r: "Revise su medidor con todas las llaves cerradas: si gira, hay una fuga interna. Si no encuentra la causa, presente un reclamo con su código de suscriptor y lo revisamos." },
    { p: "¿Qué pasa si no pago a tiempo?", r: "Después de la fecha límite se generan intereses de mora y, si se acumulan facturas sin pagar, el servicio puede ser suspendido. Si tiene dificultades, acérquese a la oficina para acordar un pago." },
    { p: "¿Cómo me hago socio suscriptor?", r: "Acérquese a la oficina con su documento de identidad y el certificado de tradición del predio. Le explicamos los requisitos y el proceso." },
    { p: "¿Puedo solicitar un cambio de medidor?", r: "Sí. Presente una petición indicando su código de suscriptor. Revisaremos el medidor y le informaremos si debe cambiarse y el costo." }
  ]
};
