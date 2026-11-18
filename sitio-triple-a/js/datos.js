/* ==========================================================
   DATOS EDITABLES DE LA PÁGINA
   Cambie aquí la información y guarde el archivo.
   No necesita tocar el HTML.
   ========================================================== */
window.TRIPLE_A = {
  empresa: "Triple A del Barrio Cartagena",
  municipio: "Facatativá, Cundinamarca",

  // ---- CONTACTO (POR CONFIRMAR: reemplace con los datos reales) ----
  direccion: "Barrio Cartagena, Facatativá, Cundinamarca",
  telefono: "+57 300 000 0000",          // POR CONFIRMAR
  whatsapp: "573000000000",              // POR CONFIRMAR: solo números, con 57 adelante
  correo: "gerenciatriplea@tripleafacatativa.com.co",
  horario: "Lunes a viernes, 8:00 a. m. a 12:00 m. y 2:00 p. m. a 5:00 p. m.", // POR CONFIRMAR
  lineaDanos: "+57 300 000 0000",        // POR CONFIRMAR: línea para fugas y daños

  // ---- ESTADO DEL SERVICIO ----
  // estado: "normal" | "programado" | "interrumpido"
  estado: "normal",
  mensajeEstado: "El servicio de acueducto funciona con normalidad en todo el barrio.",

  // ---- AVISOS Y CORTES PROGRAMADOS (el más reciente primero) ----
  avisos: [
    {
      fecha: "2026-11-25",
      titulo: "Lavado de tanque de almacenamiento",
      detalle: "Suspensión del servicio de 8:00 a. m. a 2:00 p. m. Recomendamos almacenar agua el día anterior.",
      sectores: "Todo el barrio"
    },
    {
      fecha: "2026-11-12",
      titulo: "Cambio de válvula en la red principal",
      detalle: "Trabajo terminado. El servicio quedó restablecido a las 11:30 a. m.",
      sectores: "Calles del sector norte"
    }
  ],

  // ---- RECOLECCIÓN DE ASEO (POR CONFIRMAR) ----
  recoleccion: [
    { dia: "Lunes", tipo: "Residuos ordinarios (bolsa negra)" },
    { dia: "Miércoles", tipo: "Reciclables limpios y secos (bolsa blanca)" },
    { dia: "Viernes", tipo: "Residuos ordinarios (bolsa negra)" }
  ],

  // ---- PUNTOS DE PAGO (POR CONFIRMAR) ----
  puntosPago: [
    { nombre: "Oficina de Triple A", detalle: "Barrio Cartagena. Efectivo y transferencia." },
    { nombre: "Transferencia o Nequi", detalle: "Envíe el comprobante por WhatsApp con su código de suscriptor." }
  ],

  // ---- CALIDAD DEL AGUA (IRCA) ----
  // Publique el resultado mensual. Deje irca en null mientras no haya dato.
  // Escala IRCA: 0–5 % sin riesgo, 5,1–14 % bajo, 14,1–35 % medio, 35,1–80 % alto.
  calidad: {
    irca: null,          // ejemplo: 0.0
    mes: "",             // ejemplo: "Octubre de 2026"
    laboratorio: ""      // ejemplo: "Secretaría de Salud de Cundinamarca"
  },

  // ---- DOCUMENTOS DE TRANSPARENCIA (suba los PDF a la carpeta /documentos) ----
  documentos: [
    { nombre: "Contrato de condiciones uniformes", archivo: "documentos/contrato-condiciones-uniformes.pdf" },
    { nombre: "Tarifas vigentes", archivo: "documentos/tarifas.pdf" },
    { nombre: "Informe de gestión", archivo: "documentos/informe-gestion.pdf" },
    { nombre: "Estatutos de la organización", archivo: "documentos/estatutos.pdf" }
  ]
};
