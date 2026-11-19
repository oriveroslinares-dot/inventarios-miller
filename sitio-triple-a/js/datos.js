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
    { nombre: "Olga Lucía Chavarro Santana", cargo: "Secretario", foto: "" },
    { nombre: "Nubia Cristina Cruz Forero", cargo: "Tesorera", foto: "" },
    { nombre: "Daniel Duarte Duarte", cargo: "Vocal", foto: "" },
    { nombre: "José Enrique Caicedo Castañeda", cargo: "Vocal", foto: "" },
    { nombre: "Luz Stella Carrasco Alarcón", cargo: "Vocal", foto: "" }
  ],
  auditorExterno: { nombre: "AD Soluciones Integrales S.A.S.", vigencia: "abril de 2026 a abril de 2027" },

  // ---------- NOTICIAS ----------
  // tipo: "Comunicado" (oficial) o "Noticia". El texto completo se abre al pulsar "Leer".
  // facebook: pegue el enlace de la publicación en Facebook para mostrar el botón "Ver en Facebook".
  // archivo: PDF opcional en /documentos.
  noticias: [
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
    { titulo: "Estructura tarifaria periodo 02 de 2026", categoria: "Tarifas", fecha: "2026-02-01", archivo: "documentos/tarifas-2026-02.pdf", descripcion: "Cargos fijos y por consumo por uso y estrato." },
    { titulo: "Acta de asamblea general 2026", categoria: "Asambleas", fecha: "2026-03-28", archivo: "documentos/acta-asamblea-2026.pdf", descripcion: "Decisiones de la asamblea de socios suscriptores." },
    { titulo: "Contrato de condiciones uniformes", categoria: "Normatividad", fecha: "2025-01-15", archivo: "documentos/contrato-condiciones-uniformes.pdf", descripcion: "Derechos y deberes de usuarios y empresa." },
    { titulo: "Estatutos de la asociación", categoria: "Normatividad", fecha: "2024-06-01", archivo: "documentos/estatutos.pdf", descripcion: "Reglas de funcionamiento de la asociación." }
  ],

  // ---------- TARIFAS (periodo 02 de 2026) ----------
  // Valores en pesos. Cargo fijo: $/mes. Consumos: $/m³. Use null si no tiene el dato.
  // POR CONFIRMAR: el nombre de cada servicio y completar los valores faltantes.
  periodoTarifas: "Periodo 02 de 2026",
  tarifas: {
    "Acueducto": [
      { uso: "Residencial estrato 1", fijo: 11164.00, basico: 1292.57, complementario: null, suntuario: null },
      { uso: "Residencial estrato 2", fijo: null, basico: null, complementario: null, suntuario: null },
      { uso: "Residencial estrato 3", fijo: null, basico: null, complementario: null, suntuario: null },
      { uso: "Comercial", fijo: null, basico: null, complementario: null, suntuario: null },
      { uso: "Oficial", fijo: null, basico: null, complementario: null, suntuario: null },
      { uso: "Industrial", fijo: null, basico: null, complementario: null, suntuario: null },
      { uso: "Especial", fijo: null, basico: null, complementario: null, suntuario: null }
    ],
    "Alcantarillado": [
      { uso: "Residencial estrato 1", fijo: 4442.25, basico: 680.00, complementario: null, suntuario: null },
      { uso: "Residencial estrato 2", fijo: null, basico: null, complementario: null, suntuario: null },
      { uso: "Residencial estrato 3", fijo: null, basico: null, complementario: null, suntuario: null },
      { uso: "Comercial", fijo: null, basico: null, complementario: null, suntuario: null },
      { uso: "Oficial", fijo: null, basico: null, complementario: null, suntuario: null },
      { uso: "Industrial", fijo: null, basico: null, complementario: null, suntuario: null },
      { uso: "Especial", fijo: null, basico: null, complementario: null, suntuario: null }
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
