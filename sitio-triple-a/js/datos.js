/* ==========================================================
   DATOS EDITABLES DE LA PÁGINA — Triple A del Barrio Cartagena
   Edite este archivo para actualizar la página. No toque el HTML.
   Lo marcado "POR CONFIRMAR" debe revisarlo antes de publicar.
   ========================================================== */
window.TRIPLE_A = {
  empresa: "Triple A del Barrio Cartagena",
  razonSocial: "Asociación de Socios Suscriptores del Barrio Cartagena", // POR CONFIRMAR: nombre exacto del RUT
  nit: "",                         // POR CONFIRMAR: ejemplo "900.000.000-0"
  lema: "Construimos servicio, construimos comunidad.",

  // ---------- CONTACTO ----------
  direccion: "Barrio Cartagena, Facatativá, Cundinamarca", // POR CONFIRMAR: dirección de la oficina
  telefono: "315 744 3635",
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
    enlacePSE: "",                 // POR CONFIRMAR: enlace del botón PSE de su banco (déjelo vacío si no tiene)
    medios: [
      { id: "nequi", nombre: "Nequi", detalle: "Número celular", numero: "", titular: "" },          // POR CONFIRMAR
      { id: "bancolombia", nombre: "Bancolombia", detalle: "Cuenta de ahorros", numero: "", titular: "" } // POR CONFIRMAR
    ],
    fechaLimite: "Pague antes de la fecha límite impresa en su factura para evitar intereses de mora y la suspensión del servicio."
  },

  // ---------- ESTADO DEL SERVICIO ----------
  // estado: "normal" | "programado" | "interrumpido"
  estado: "normal",
  mensajeEstado: "Acueducto, alcantarillado y aseo funcionan con normalidad.",

  // ---------- RECORRIDO DEL AGUA ----------
  fuente: "Río Botello",           // POR CONFIRMAR

  // ---------- CORTES Y AVISOS (fechas AAAA-MM-DD) ----------
  avisos: [
    // { fecha: "2026-12-02", titulo: "Lavado de tanque", detalle: "Suspensión de 8:00 a. m. a 2:00 p. m.", sectores: "Todo el barrio" }
  ],

  // ---------- COMUNICADOS ----------
  // El texto completo se muestra al pulsar "Leer". Puede adjuntar un PDF en "archivo".
  comunicados: [
    {
      fecha: "2026-05-12",
      titulo: "No hay incremento en la tarifa de aprovechamiento",
      resumen: "Aclaramos a la comunidad que actualmente no se está aplicando ningún aumento en el cobro de aprovechamiento.",
      texto: [
        "La Asociación de Socios Suscriptores del Barrio Cartagena informa a la comunidad que, hasta el momento, no se está realizando ningún aumento en el cobro de la tarifa de aprovechamiento.",
        "Cualquier modificación tarifaria debe estar previamente regulada y aprobada conforme a la normatividad de la Superintendencia de Servicios Públicos Domiciliarios. La empresa adelanta consultas ante esa entidad para verificar la normativa vigente.",
        "Para resolver inquietudes o solicitar aclaraciones, comuníquese a la línea 315 744 3635, de lunes a viernes de 8:00 a. m. a 5:00 p. m., o al correo aaacartagena@tripleafacatativa.com.co."
      ],
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
  recoleccion: [
    { dia: "Lunes", tipo: "Residuos ordinarios" },
    { dia: "Miércoles", tipo: "Material aprovechable" },
    { dia: "Viernes", tipo: "Residuos ordinarios" }
  ],

  // ---------- CALIDAD DEL AGUA (IRCA) ----------
  // Deje irca en null mientras no haya resultado.
  calidad: { irca: null, mes: "", laboratorio: "" },

  // ---------- PREGUNTAS FRECUENTES ----------
  preguntas: [
    { p: "¿Cuánto tiempo tienen para responder mi PQR?", r: "Máximo 15 días hábiles desde que la recibimos, según la Ley 142 de 1994. Si no respondemos a tiempo, se entiende resuelta a su favor (silencio administrativo positivo)." },
    { p: "¿Qué hago si mi factura llega muy alta?", r: "Revise su medidor con todas las llaves cerradas: si gira, hay una fuga interna. Si no encuentra la causa, presente un reclamo con su código de suscriptor y lo revisamos." },
    { p: "¿Qué pasa si no pago a tiempo?", r: "Después de la fecha límite se generan intereses de mora y, si se acumulan facturas sin pagar, el servicio puede ser suspendido. Si tiene dificultades, acérquese a la oficina para acordar un pago." },
    { p: "¿Cómo me hago socio suscriptor?", r: "Acérquese a la oficina con su documento de identidad y el certificado de tradición del predio. Le explicamos los requisitos y el proceso." },
    { p: "¿Puedo solicitar un cambio de medidor?", r: "Sí. Presente una petición indicando su código de suscriptor. Revisaremos el medidor y le informaremos si debe cambiarse y el costo." }
  ]
};
