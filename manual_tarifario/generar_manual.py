import datetime as dt, sys
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.workbook.defined_name import DefinedName
from openpyxl.worksheet.datavalidation import DataValidation
from openpyxl.comments import Comment
from openpyxl.formatting.rule import CellIsRule, FormulaRule

OUT = sys.argv[1]; BAS = sys.argv[2]
wb = Workbook()
F = "Arial"
NAVY = "1F3864"; LBLUE = "D9E2F3"; YEL = "FFF2CC"; GRAY = "F2F2F2"; GRN = "E2EFDA"; RED = "FCE4D6"
thin = Side(style="thin", color="BFBFBF"); BOX = Border(left=thin, right=thin, top=thin, bottom=thin)
MONEY = '$#,##0.00;($#,##0.00);"-"'; PCT = '0.00%;-0.00%;"-"'; FAC = '0.0000'; MES = 'mmm-yyyy'; DATEF = 'dd/mm/yyyy'

def st(c, bold=False, color="000000", size=10, fill=None, fmt=None, wrap=False, align=None, italic=False, border=True):
    c.font = Font(name=F, bold=bold, color=color, size=size, italic=italic)
    if fill: c.fill = PatternFill("solid", fgColor=fill)
    if fmt: c.number_format = fmt
    c.alignment = Alignment(wrap_text=wrap, vertical="center", horizontal=align)
    if border: c.border = BOX
    return c
def inp(c, v, fmt=None, key=False):   # blue input
    c.value = v; return st(c, color="0000FF", fill=YEL if key else None, fmt=fmt)
def fx(c, v, fmt=None, bold=False, link=False, fill=None):
    c.value = v; return st(c, color="008000" if link else "000000", fmt=fmt, bold=bold, fill=fill)
def txt(c, v, bold=False, wrap=False, fill=None, color="000000", italic=False, border=True, size=10):
    c.value = v; return st(c, bold=bold, wrap=wrap, fill=fill, color=color, italic=italic, border=border, size=size)
def title(ws, t, sub=None, width=10):
    ws.merge_cells(start_row=1, start_column=1, end_row=1, end_column=width)
    c = ws.cell(1, 1, t); c.font = Font(name=F, bold=True, size=14, color="FFFFFF"); c.fill = PatternFill("solid", fgColor=NAVY)
    c.alignment = Alignment(vertical="center"); ws.row_dimensions[1].height = 26
    if sub:
        ws.merge_cells(start_row=2, start_column=1, end_row=2, end_column=width)
        c = ws.cell(2, 1, sub); c.font = Font(name=F, italic=True, size=9, color="404040"); c.alignment = Alignment(wrap_text=True, vertical="top")
        ws.row_dimensions[2].height = 30
def hdr(ws, r, vals, c0=1, fill=LBLUE):
    for i, v in enumerate(vals):
        c = ws.cell(r, c0 + i, v); st(c, bold=True, fill=fill, wrap=True, align="center")
def name(n, ref): wb.defined_names[n] = DefinedName(n, attr_text=ref)
def widths(ws, d):
    for k, v in d.items(): ws.column_dimensions[k].width = v
def note(c, t): c.comment = Comment(t, "Manual tarifario")
def okfmt(ws, rng):
    ws.conditional_formatting.add(rng, FormulaRule(formula=[f'ISNUMBER(SEARCH("OK",{rng.split(":")[0].replace("$","")}))'], fill=PatternFill("solid", fgColor="C6EFCE"), font=Font(name=F, color="006100", bold=True)))
    ws.conditional_formatting.add(rng, FormulaRule(formula=[f'OR(ISNUMBER(SEARCH("REVISAR",{rng.split(":")[0].replace("$","")})),ISNUMBER(SEARCH("NO ",{rng.split(":")[0].replace("$","")})))'], fill=PatternFill("solid", fgColor="FFC7CE"), font=Font(name=F, color="9C0006", bold=True)))

# ============================== INICIO =====================================
ws0 = wb.active; ws0.title = "INICIO"
# ============================ PARAMETROS ===================================
wp = wb.create_sheet("PARAMETROS")
title(wp, "PARÁMETROS DEL PRESTADOR Y DE LA REGULACIÓN", "Celdas en AZUL = datos que usted escribe. Fondo AMARILLO = dato clave que debe revisar. Negro = fórmula (no tocar).", 3)
hdr(wp, 3, ["Dato", "Valor", "Fuente / nota"])
P = {}
rows = [
 ("Prestador", "Triple A del Barrio Cartagena – Asociación de Socios Suscriptores", "Proyecto de resolución de Junta Directiva 2026", None, False),
 ("NIT", "832.001.989-1", "Proyecto de resolución de Junta Directiva 2026", None, False),
 ("Municipio", "Facatativá, Cundinamarca", "", None, False),
 ("Altitud del municipio (msnm)", 2586, "Dato de referencia de Facatativá; verificar con el POT. Define el consumo básico (Res. CRA 750/2016).", "0", True),
 ("Suscriptores ACUEDUCTO a 31-dic-2024", None, "ESCRIBIR. Lo exige la Res. CRA 1038/2026 art. 2.1.1.1.1.6 para clasificar el subsegmento.", "#,##0", True),
 ("Suscriptores ALCANTARILLADO a 31-dic-2024", None, "ESCRIBIR. Se usa el mayor de los dos (parágrafo 1, art. 2.1.1.1.1.6).", "#,##0", True),
 ("¿Es Gestor Comunitario del Agua? (SI / NO)", "POR DEFINIR", "Asociación de suscriptores: puede ser Gestor Comunitario (Decreto 960/2025). Confírmelo con el abogado: cambia la metodología desde 2027.", None, True),
 ("Segmento CRA 1038/2026", '=IF(B10="SI","Segundo segmento (Gestor Comunitario – tarifa comunitaria)",IF(B10="NO","Primer segmento","Definir B10"))', "Art. 2.1.1.1.1.6 Res. CRA 1038/2026", None, False),
 ("Subsegmento CRA 1038/2026", '=IF(COUNT(B8:B9)=0,"Faltan suscriptores (B8:B9)",IF(B10="SI",IF(MAX(B8:B9)>1600,"Primer subsegmento",IF(MAX(B8:B9)>500,"Segundo subsegmento",IF(MAX(B8:B9)>300,"Tercer subsegmento","Cuarto subsegmento"))),IF(B10="NO",IF(MAX(B8:B9)>3200,"Primer subsegmento",IF(MAX(B8:B9)>1400,"Segundo subsegmento",IF(MAX(B8:B9)>600,"Tercer subsegmento","Cuarto subsegmento"))),"Definir B10")))', "Umbrales: 1er segmento 3.200/1.400/600; GC 1.600/500/300 suscriptores", None, False),
 ("Periodicidad de facturación (meses)", 2, "Facturación bimestral (períodos ene-feb, mar-abr...)", "0", False),
 ("Consumo básico mensual (m³/suscriptor)", "=IF(B7>2000,11,IF(B7>=1000,13,16))", "Res. CRA 750/2016: >2.000 msnm = 11 m³; 1.000–2.000 = 13 m³; <1.000 = 16 m³", "0", False),
 ("Consumo básico del período (m³)", "=B14*B13", "Tramo BÁSICO, con subsidio (0–22 m³ bimestral)", "0", False),
 ("Múltiplo del básico donde empieza el suntuario", 2, "Manual Riveli: complementario 22–44 m³, suntuario > 44 m³", "0.0", False),
 ("Límite superior del complementario (m³/período)", "=B15*B16", "", "0", False),
 ("Fecha de aplicación de la próxima actualización", dt.date(2026, 11, 1), "ESCRIBIR. Define qué metodología e índice aplican.", DATEF, True),
 ("Metodología acueducto / alcantarillado vigente", '=IF(B18<=DATE(2026,12,31),"Res. CRA 825/2017 (Título 2, Res. CRA 943/2021) – indexa con IPC total","Res. CRA 1038/2026 – IPC sin alimentos ni regulados (CMA, CMOG, CMICT) e IPC total (CMI)")', "Res. CRA 1038/2026 art. 23 (transición hasta 31-dic-2026) y art. 2.1.1.1.1.7 (inicio 1-ene-2027)", None, False),
 ("Mes base IPC – Acueducto y Alcantarillado", dt.date(2026, 6, 30), "Último mes usado en la actualización anterior (jun-2026). La macro lo actualiza sola.", MES, True),
 ("Mes base IPC – Aseo y Aforados", dt.date(2026, 6, 30), "Último mes usado en la actualización anterior (jun-2026).", MES, True),
 ("Mes final (opcional: déjelo vacío para usar el último IPC cargado)", None, "Escriba un mes solo si quiere simular con un mes distinto al último", MES, False),
 ("Mes final usado en los cálculos", "=IF(B22=\"\",INDEX(IPC!$A$5:$A$64,COUNT(IPC!$B$5:$B$64)),B22)", "Último mes con IPC cargado en la hoja IPC", MES, False),
 ("Umbral de actualización", 0.03, "Ley 142/1994 art. 125; Res. CRA 1038/2026 Anexo 6.2.1.1; Res. CRA 943/2021 art. 5.3.5.2.9.1 (aseo)", PCT, False),
 ("% del cargo por consumo que es CMI (solo 1er segmento, desde 2027)", 0, "Desde 2027 el CMI se indexa con IPC total y el resto con IPC sin alimentos ni regulados. Tómelo del estudio de costos.", PCT, False),
]
r = 4
for (lab, val, src, fmt, key) in rows:
    txt(wp.cell(r, 1), lab, bold=True, wrap=True)
    c = wp.cell(r, 2)
    if isinstance(val, str) and val.startswith("="): fx(c, val, fmt)
    else: inp(c, val, fmt, key)
    txt(wp.cell(r, 3), src, wrap=True, italic=True, color="404040")
    r += 1
# r is now 26
txt(wp.cell(26, 1), "LÍMITES LEGALES DE SUBSIDIOS Y CONTRIBUCIONES", bold=True, fill=LBLUE); wp.merge_cells("A26:C26")
lim = [("Subsidio MÁXIMO estrato 1", 0.70, "Ley 1450/2011 art. 125 (citado en el proyecto de resolución)"),
       ("Subsidio MÁXIMO estrato 2", 0.40, "Ley 1450/2011 art. 125"),
       ("Subsidio MÁXIMO estrato 3", 0.15, "Ley 1450/2011 art. 125"),
       ("Contribución MÍNIMA estrato 5", 0.50, "Ley 1450/2011 art. 125"),
       ("Contribución MÍNIMA estrato 6", 0.60, "Ley 1450/2011 art. 125"),
       ("Contribución MÍNIMA comercial", 0.50, "Ley 1450/2011 art. 125"),
       ("Contribución MÍNIMA industrial", 0.30, "Ley 1450/2011 art. 125")]
for i, (a, b, s) in enumerate(lim):
    rr = 27 + i; txt(wp.cell(rr, 1), a, bold=True); inp(wp.cell(rr, 2), b, PCT); txt(wp.cell(rr, 3), s, italic=True, color="404040")
txt(wp.cell(35, 1), "ASEO INDUSTRIAL AFORADO (por tonelada)", bold=True, fill=LBLUE); wp.merge_cells("A35:C35")
afo = [("SMMLV 2026", 1750905, "Decreto 1469/2025; transitorio Decreto 0159/2026 (archivo Macro_Facturacion_Aforados)", '$#,##0'),
       ("% VIAT sobre SMMLV (por tonelada)", 0.008, "Decreto 2412/2018 según archivo Macro_Facturacion_Aforados – VERIFICAR", '0.00%'),
       ("CDF Nuevo Mondoñedo ($/ton)", 49729.34, "Circular vigente desde 17-jul-2026 – actualizar cuando cambie", MONEY),
       ("Recolección, transporte y comercialización ($/ton)", 11581.13, "Estimado por diferencia – reemplazar por dato oficial", MONEY),
       ("% Contribución industrial (aseo)", 0.30, "Acuerdo Municipal Facatativá 2022-2026", PCT),
       ("Método de facturación de aforados (A o B)", "A", "A = Consolidado jul-2026 (tarifa/ton + VIAT por factura). B = Parámetros del archivo de aforados (VIAT dentro de la tarifa/ton). Ver hoja AFORADOS.", None)]
for i, (a, b, s, f) in enumerate(afo):
    rr = 36 + i; txt(wp.cell(rr, 1), a, bold=True, wrap=True); inp(wp.cell(rr, 2), b, f, key=(rr == 41)); txt(wp.cell(rr, 3), s, italic=True, color="404040", wrap=True)
widths(wp, {"A": 46, "B": 30, "C": 80})
dv = DataValidation(type="list", formula1='"SI,NO,POR DEFINIR"', allow_blank=True); wp.add_data_validation(dv); dv.add("B10")
dv2 = DataValidation(type="list", formula1='"A,B"'); wp.add_data_validation(dv2); dv2.add("B41")
for n, ref in [("Altitud","$B$7"),("ConsBasico","$B$15"),("LimCompl","$B$17"),("FechaAplic","$B$18"),("MesBase","$B$20"),
               ("MesBaseAseo","$B$21"),("MesFinalManual","$B$22"),("MesFinal","$B$23"),("Umbral","$B$24"),("PesoCMI","$B$25"),
               ("EsGC","$B$10"),("Sub1","$B$27"),("Sub2","$B$28"),("Sub3","$B$29"),("MinCom","$B$32"),("MinInd","$B$33"),("MetodoAfo","$B$41")]:
    name(n, f"PARAMETROS!{ref}")

# ================================ IPC ======================================
wi = wb.create_sheet("IPC")
title(wi, "SERIE OFICIAL DEL IPC (base dic-2018 = 100)", "Fuente: DANE, publicado por el Banco de la República (series 15000 IPC total y 15315 IPC sin alimentos ni regulados), consultado el 19-nov-2026. Cada mes agregue el nuevo dato (en azul) o use la macro ActualizarIPC. El DANE publica cerca del día 8 de cada mes.", 8)
hdr(wi, 4, ["Mes", "IPC total", "IPC sin alimentos ni regulados", "Var. mensual", "Var. año corrido", "Var. 12 meses", "Fuente", "Acum. desde mes base (Acu/Alc)"])
ipc = [("2024-12",144.88,133.4),("2025-01",146.24,134.24),("2025-02",147.9,135.28),("2025-03",148.68,135.93),("2025-04",149.66,136.71),
("2025-05",150.14,137.12),("2025-06",150.3,137.52),("2025-07",150.71,137.83),("2025-08",150.99,138.15),("2025-09",151.48,138.63),
("2025-10",151.76,139.04),("2025-11",151.87,139.38),("2025-12",152.27,140.09),("2026-01",154.07,141.47),("2026-02",155.73,142.75),
("2026-03",156.94,143.8),("2026-04",158.17,144.62),("2026-05",158.91,145.32),("2026-06",159.53,145.78),("2026-07",159.79,146.05),
("2026-08",160.42,146.61),("2026-09",161.0,146.99),("2026-10",161.32,147.26)]
def eom(y, m):
    n = dt.date(y + (m == 12), m % 12 + 1, 1); return n - dt.timedelta(days=1)
months = []
y, m = 2024, 12
for i in range(60):
    months.append(eom(y, m)); m += 1
    if m == 13: y, m = y + 1, 1
data = {e[0]: e for e in ipc}
for i, d in enumerate(months):
    rr = 5 + i
    st(wi.cell(rr, 1, d), fmt=MES)
    k = d.strftime("%Y-%m")
    if k in data:
        inp(wi.cell(rr, 2), data[k][1], '0.00'); inp(wi.cell(rr, 3), data[k][2], '0.00')
        txt(wi.cell(rr, 7), "DANE vía BanRep", italic=True, color="404040")
    else:
        inp(wi.cell(rr, 2), None, '0.00'); inp(wi.cell(rr, 3), None, '0.00'); txt(wi.cell(rr, 7), None)
    fx(wi.cell(rr, 4), f'=IF(OR(B{rr}="",B{rr-1}="",ROW()=5),"",B{rr}/B{rr-1}-1)' if rr > 5 else '=""', PCT)
    fx(wi.cell(rr, 5), f'=IF(B{rr}="","",IFERROR(B{rr}/INDEX($B$5:$B$64,MATCH(DATE(YEAR(A{rr})-1,12,31),$A$5:$A$64,0))-1,""))', PCT)
    fx(wi.cell(rr, 6), f'=IF(B{rr}="","",IFERROR(B{rr}/INDEX($B$5:$B$64,MATCH(DATE(YEAR(A{rr})-1,MONTH(A{rr})+1,0),$A$5:$A$64,0))-1,""))', PCT)
    fx(wi.cell(rr, 8), f'=IF(OR(B{rr}="",A{rr}<=MesBase),"",ROUND(ROUND(B{rr},2)/INDEXACION!$B$5,4)-1)', PCT)
okfmt  # noqa
wi.conditional_formatting.add("H5:H64", CellIsRule(operator="greaterThanOrEqual", formula=["Umbral"], fill=PatternFill("solid", fgColor="C6EFCE")))
widths(wi, {"A": 12, "B": 12, "C": 16, "D": 12, "E": 13, "F": 13, "G": 22, "H": 16})
wi.freeze_panes = "A5"

# ============================ INDEXACION ===================================
wx = wb.create_sheet("INDEXACION")
title(wx, "CÁLCULO DEL FACTOR DE ACTUALIZACIÓN (FA)", "FA = ROUND( ROUND(IPC mes final,2) / ROUND(IPC mes base,2) ; 4 ). Los valores actualizados se redondean a 2 decimales (Res. CRA 1038/2026 Anexo 6.2.1.1; Res. CRA 943/2021 art. 5.3.5.2.9.1). Solo se aplica si la variación acumulada es ≥ 3%.", 5)
hdr(wx, 4, ["Concepto", "IPC total", "IPC sin alim. ni regulados", "Mes", "Nota"])
L = lambda col, mes: f'=IFERROR(ROUND(INDEX(IPC!${col}$5:${col}$64,MATCH({mes},IPC!$A$5:$A$64,0)),2),"Sin dato")'
txt(wx.cell(5, 1), "Índice mes base – Acueducto/Alcantarillado", bold=True)
fx(wx.cell(5, 2), L("B", "MesBase"), '0.00'); fx(wx.cell(5, 3), L("C", "MesBase"), '0.00'); fx(wx.cell(5, 4), "=MesBase", MES, link=True)
txt(wx.cell(6, 1), "Índice mes base – Aseo/Aforados", bold=True)
fx(wx.cell(6, 2), L("B", "MesBaseAseo"), '0.00'); fx(wx.cell(6, 3), L("C", "MesBaseAseo"), '0.00'); fx(wx.cell(6, 4), "=MesBaseAseo", MES, link=True)
txt(wx.cell(7, 1), "Índice mes final", bold=True)
fx(wx.cell(7, 2), L("B", "MesFinal"), '0.00'); fx(wx.cell(7, 3), L("C", "MesFinal"), '0.00'); fx(wx.cell(7, 4), "=MesFinal", MES, link=True)
txt(wx.cell(8, 1), "FA Acueducto/Alcantarillado por índice", bold=True)
fx(wx.cell(8, 2), '=IFERROR(ROUND(B7/B5,4),1)', FAC); fx(wx.cell(8, 3), '=IFERROR(ROUND(C7/C5,4),1)', FAC)
txt(wx.cell(9, 1), "FA Aseo por índice", bold=True)
fx(wx.cell(9, 2), '=IFERROR(ROUND(B7/B6,4),1)', FAC); fx(wx.cell(9, 3), '=IFERROR(ROUND(C7/C6,4),1)', FAC)
for i, t in enumerate(["FACTOR QUE SE APLICA", "", "", "", ""]): pass
hdr(wx, 11, ["Factor aplicable", "Valor", "Variación", "¿Cumple umbral?", "Regla"])
rowsF = [
 ("FA cargo fijo Acueducto/Alcantarillado (CMA)", '=IF(FechaAplic<=DATE(2026,12,31),B8,C8)', "Hasta 31-dic-2026 IPC total (CRA 825/2017); desde 2027 IPC sin alimentos ni regulados (CRA 1038/2026)"),
 ("FA cargo por consumo Acueducto/Alcantarillado", '=IF(FechaAplic<=DATE(2026,12,31),B8,IF(EsGC="SI",C8,ROUND(PesoCMI*B8+(1-PesoCMI)*C8,4)))', "Desde 2027: CMO/CMICT con IPC sin alim. ni regulados y CMI con IPC total (pondera con PARAMETROS!B25). Gestor Comunitario: todo con IPC sin alim. ni regulados"),
 ("FA Aseo y Aforados", '=B9', "Res. CRA 853/2018 (art. 5.3.5.2.9.1 Res. CRA 943/2021): IPC total"),
]
for i, (a, f, rule) in enumerate(rowsF):
    rr = 12 + i
    txt(wx.cell(rr, 1), a, bold=True, wrap=True); fx(wx.cell(rr, 2), f, FAC, bold=True, fill=GRN)
    fx(wx.cell(rr, 3), f'=B{rr}-1', PCT)
    fx(wx.cell(rr, 4), f'=IF(C{rr}>=Umbral-0.000001,"OK – SE PUEDE ACTUALIZAR","NO – esperar (falta "&FIXED((Umbral-C{rr})*100,2)&" puntos)")')
    txt(wx.cell(rr, 5), rule, wrap=True, italic=True, color="404040")
okfmt(wx, "D12:D14")
txt(wx.cell(15, 1), "Índice usado para Acueducto/Alcantarillado", bold=True)
fx(wx.cell(15, 2), '=IF(FechaAplic<=DATE(2026,12,31),"IPC total",IF(EsGC="SI","IPC sin alimentos ni regulados","IPC SAR (CMA/CMO/CMICT) + IPC total (CMI)"))')
wx.merge_cells("B15:E15")
for n, ref in [("FA_AA_CF","$B$12"),("FA_AA_CONS","$B$13"),("FA_Aseo","$B$14"),("VarAcuAlc","$C$12"),("VarAseo","$C$14"),("IndiceAA","$B$15")]:
    name(n, f"INDEXACION!{ref}")
# comprobación jul-2026
txt(wx.cell(17, 1), "COMPROBACIÓN DE LA ACTUALIZACIÓN DE JULIO 2026", bold=True, fill=LBLUE); wx.merge_cells("A17:E17")
txt(wx.cell(18, 1), "IPC dic-2025 (mes base)"); fx(wx.cell(18, 2), '=ROUND(INDEX(IPC!$B$5:$B$64,MATCH(DATE(2025,12,31),IPC!$A$5:$A$64,0)),2)', '0.00')
txt(wx.cell(19, 1), "IPC jun-2026 (mes final)"); fx(wx.cell(19, 2), '=ROUND(INDEX(IPC!$B$5:$B$64,MATCH(DATE(2026,6,30),IPC!$A$5:$A$64,0)),2)', '0.00')
txt(wx.cell(20, 1), "FA calculado"); fx(wx.cell(20, 2), '=ROUND(B19/B18,4)', FAC)
txt(wx.cell(21, 1), "FA usado en la resolución (4,77%)"); inp(wx.cell(21, 2), 1.0477, FAC)
txt(wx.cell(22, 1), "Resultado", bold=True); fx(wx.cell(22, 2), '=IF(B20=B21,"OK – coincide con el boletín DANE jun-2026","REVISAR")'); okfmt(wx, "B22:B22")
widths(wx, {"A": 46, "B": 26, "C": 22, "D": 34, "E": 70})

# ====================== ACUEDUCTO / ALCANTARILLADO ========================
cats = ["Residencial", "Comercial", "Oficial", "Industrial", "Especial"]
acu = [[16390.03,2587.8,2587.8,2587.8,12292.52,1423.29,2587.8,2587.8],[16390.03,2587.8,2587.8,2587.8,34419.06,3881.7,3881.7,3881.7],
       [16390.03,2587.8,2587.8,2587.8,16390.03,2587.8,2587.8,2587.8],[27030.66,3389.86,3389.86,3389.86,63522.05,4406.84,4406.84,4406.84],
       [16390.03,2587.8,2587.8,2587.8,16390.03,2587.8,2587.8,2587.8]]
acuF = [[-0.25,-0.45,0,0],[1.10,0.5,0.5,0.5],[0,0,0,0],[1.35,0.3,0.3,0.3],[0,0,0,0]]
alc = [[6522.01,1497.54,1497.54,1497.54,4891.5,748.77,1497.54,1497.54],[6522.01,1497.54,1497.54,1497.54,16305.01,2246.31,2246.31,2246.31],
       [6522.01,1497.54,1497.54,1497.54,6522.01,1497.54,1497.54,1497.54],[6522.01,1497.54,1497.54,1497.54,20218.22,1946.8,1946.8,1946.8],
       [6522.01,1497.54,1497.54,1497.54,6522.01,1497.54,1497.54,1497.54]]
alcF = [[-0.25,-0.5,0,0],[1.5,0.5,0.5,0.5],[0,0,0,0],[2.1,0.3,0.3,0.3],[0,0,0,0]]
from openpyxl.utils import get_column_letter as CL
def servicio(nm, vig, fac, pref):
    w = wb.create_sheet(nm)
    title(w, f"{nm} — COSTO vs. TARIFA (vigente jul-2026 y proyectada)", "Básico = 0 a 22 m³ por período (con subsidio). Complementario 22–44 m³ y Suntuario > 44 m³ SIN subsidio. Fuente de valores vigentes: Costo_vs_Tarifa_BASICO (jul-2026) y Consolidado de Tarifas Triple A jul-2026. Los factores del Acuerdo Municipal 2022-2026 se escriben en azul.", 26)
    groups = [(2, 5, "COSTO vigente ($)"), (6, 9, "TARIFA vigente ($)"), (10, 13, "Factor implícito (tarifa/costo − 1)"),
              (14, 17, "Factor Acuerdo Municipal (− subsidio / + contribución)"), (18, 21, "COSTO proyectado ($)"), (22, 25, "TARIFA proyectada ($)")]
    fills = [GRAY, GRAY, "FFFFFF", YEL, GRN, GRN]
    for (a, b, t), fl in zip(groups, fills):
        w.merge_cells(start_row=4, start_column=a, end_row=4, end_column=b); st(w.cell(4, a, t), bold=True, fill=fl if fl != "FFFFFF" else LBLUE, align="center")
    sub = ["Fijo", "Básico $/m³", "Compl. $/m³", "Sunt. $/m³"]
    hdr(w, 5, ["Categoría"] + sub * 6 + ["¿Factor implícito = Acuerdo?"])
    for i, cat in enumerate(cats):
        rr = 6 + i
        txt(w.cell(rr, 1), cat, bold=True)
        for j in range(8): inp(w.cell(rr, 2 + j), vig[i][j], MONEY)
        for j in range(4):
            cc, tc = CL(2 + j), CL(6 + j)
            fx(w.cell(rr, 10 + j), f'=IF({cc}{rr}=0,0,{tc}{rr}/{cc}{rr}-1)', PCT)
            inp(w.cell(rr, 14 + j), fac[i][j], PCT)
        for j in range(8):
            src = CL(2 + j); fa = "FA_AA_CF" if j in (0, 4) else "FA_AA_CONS"
            fx(w.cell(rr, 18 + j), f'=ROUND({src}{rr}*{fa},2)', MONEY)
        fx(w.cell(rr, 26), f'=IF(MAX(ABS(J{rr}-N{rr}),ABS(K{rr}-O{rr}),ABS(L{rr}-P{rr}),ABS(M{rr}-Q{rr}))<=0.0005,"OK","REVISAR")')
    okfmt(w, "Z6:Z10")
    txt(w.cell(12, 1), "Cómo se calcula:", bold=True, border=False)
    for k, t in enumerate(["• Tarifa = Costo × (1 + factor del Acuerdo). Ej.: Residencial cargo fijo = Costo × (1 − 25%).",
                           "• Actualización por IPC: Costo nuevo = ROUND(Costo vigente × FA; 2) y Tarifa nueva = ROUND(Tarifa vigente × FA; 2). El % de subsidio/contribución NO cambia.",
                           "• FA cargo fijo y FA consumo vienen de la hoja INDEXACION (B12 y B13). Las columnas R:Y son lo que se facturaría si se aplica la actualización.",
                           "• Columna Z: compara el factor implícito con el del Acuerdo; si dice REVISAR, el valor vigente no corresponde al % aprobado por el Concejo."]):
        txt(w.cell(13 + k, 1), t, border=False); w.merge_cells(start_row=13 + k, start_column=1, end_row=13 + k, end_column=20)
    w.column_dimensions["A"].width = 14
    for c in range(2, 27): w.column_dimensions[CL(c)].width = 12.5
    w.column_dimensions["Z"].width = 16; w.freeze_panes = "B6"
    name(f"{pref}_Vig", f"{nm}!$B$6:$I$10"); name(f"{pref}_Proy", f"{nm}!$R$6:$Y$10")
    return w
wa = servicio("ACUEDUCTO", acu, acuF, "Acu")
wl = servicio("ALCANTARILLADO", alc, alcF, "Alc")
note(wa["B9"], "Industrial tiene su propio costo porque su consumo es distinto (Manual Riveli).")

# ================================= ASEO ====================================
aseo = [("Residencial Estrato 1",66057,37064.37,"Subsidio 43,89%",1,-0.4389),("Residencial Estrato 2",63304,47427.28,"Subsidio 25,08%",2,-0.2508),
("Residencial Estrato 3",57957,57956.87,"Sin subsidio",3,0),("Residencial Estrato 4",60082,60082.18,"Sin subsidio",4,0),
("Sin Recolección Puerta a Puerta Est.1",54603,30638.01,"Subsidio 43,89%",1,-0.4389),("Desocupado Residencial Est.1",28425,15949.37,"Subsidio 43,89%",1,-0.4389),
("Desocupado Residencial Est.2",24638,18458.84,"Subsidio 25,08%",2,-0.2508),("Comercial",65127,97690.39,"Contribución 50%","Comercial",0.5),
("Desocupado Comercial",24289,36433.50,"Contribución 50%","Comercial",0.5),("Industrial (estándar)",67924,88301.02,"Contribución 30%","Industrial",0.3),
("Especial 1",359256,359255.61,"Sin subsidio","Especial",0),("Especial 2",1338054,1338053.93,"Sin subsidio","Especial",0),
("Especial 3",2271238,2271237.51,"Sin subsidio","Especial",0),("Especial 4",60424,60424.08,"Sin subsidio","Especial",0)]
ws_ = wb.create_sheet("ASEO")
title(ws_, "ASEO — COSTO vs. TARIFA (vigente jul-2026 y proyectada)", "Aseo no tiene tramos: un valor fijo por categoría. Metodología Res. CRA 853/2018 (aclarada por CRA 892/2019). Base de la actualización de julio: período mar-abr 2026 × 1,0477. Costos tomados del archivo Costo_vs_Tarifa (redondeados a pesos); tarifas del Consolidado jul-2026.", 13)
hdr(ws_, 5, ["Categoría", "COSTO vigente ($)", "TARIFA vigente ($)", "Condición", "Tipo", "Clase legal", "Factor implícito", "Factor Acuerdo", "COSTO proyectado ($)", "TARIFA proyectada ($)", "¿Implícito = Acuerdo?", "Límite legal", "¿Cumple ley?"])
for i, (cat, c, t, cond, cls, f) in enumerate(aseo):
    rr = 6 + i
    txt(ws_.cell(rr, 1), cat, bold=True); inp(ws_.cell(rr, 2), c, MONEY); inp(ws_.cell(rr, 3), t, MONEY); txt(ws_.cell(rr, 4), cond)
    fx(ws_.cell(rr, 5), f'=IF(H{rr}<0,"Subsidio",IF(H{rr}>0,"Contribución","Neutro"))'); inp(ws_.cell(rr, 6), cls)
    fx(ws_.cell(rr, 7), f'=C{rr}/B{rr}-1', PCT); inp(ws_.cell(rr, 8), f, PCT)
    fx(ws_.cell(rr, 9), f'=ROUND(B{rr}*FA_Aseo,2)', MONEY); fx(ws_.cell(rr, 10), f'=ROUND(C{rr}*FA_Aseo,2)', MONEY)
    fx(ws_.cell(rr, 11), f'=IF(ABS(G{rr}-H{rr})<=0.0005,"OK","REVISAR")')
    fx(ws_.cell(rr, 12), f'=IF(F{rr}=1,-Sub1,IF(F{rr}=2,-Sub2,IF(F{rr}=3,-Sub3,IF(F{rr}="Comercial",MinCom,IF(F{rr}="Industrial",MinInd,0)))))', PCT)
    fx(ws_.cell(rr, 13), f'=IF(OR(F{rr}="Comercial",F{rr}="Industrial"),IF(H{rr}>=L{rr}-0.00001,"OK","REVISAR – contribución bajo el mínimo"),IF(OR(F{rr}=1,F{rr}=2,F{rr}=3),IF(H{rr}>=L{rr}-0.00001,"OK","REVISAR – subsidio sobre el máximo"),IF(H{rr}=0,"OK","REVISAR – debería ser 0%")))')
okfmt(ws_, "K6:K19"); okfmt(ws_, "M6:M19")
txt(ws_.cell(21, 1), "Nota: Industrial Aforado (por tonelada) e Industrial por viajes NO están aquí; ver hoja AFORADOS. Columna 'Clase legal': 1, 2, 3, 4, Comercial, Industrial o Especial.", italic=True, border=False)
ws_.merge_cells("A21:M21")
widths(ws_, {"A": 36, "B": 15, "C": 15, "D": 17, "E": 12, "F": 11, "G": 11, "H": 11, "I": 16, "J": 16, "K": 13, "L": 11, "M": 30})
ws_.freeze_panes = "B6"
name("Aseo_Vig", "ASEO!$B$6:$C$19"); name("Aseo_Proy", "ASEO!$I$6:$J$19")

# =============================== AFORADOS ==================================
wf = wb.create_sheet("AFORADOS")
title(wf, "ASEO INDUSTRIAL AFORADO — tarifa por tonelada", "Hay DOS cálculos distintos en los documentos recibidos; el método se elige en PARAMETROS!B41. Diferencia importante: el Consolidado cobra VIAT como cargo fijo por factura; el archivo de aforados lo incluye dentro de la tarifa por tonelada.", 8)
hdr(wf, 4, ["Concepto", "Vigente", "Proyectado (× FA aseo)", "Fuente"])
txt(wf.cell(5, 1), "MÉTODO A – Tarifa por tonelada ($/t)", bold=True); inp(wf.cell(5, 2), 79392.84, MONEY); fx(wf.cell(5, 3), '=ROUND(B5*FA_Aseo,2)', MONEY); txt(wf.cell(5, 4), "Consolidado Tarifas jul-2026 (facturas reales may-jun 2026)", italic=True)
txt(wf.cell(6, 1), "MÉTODO A – VIAT cargo fijo por factura ($)", bold=True); inp(wf.cell(6, 2), 4075.13, MONEY); fx(wf.cell(6, 3), '=ROUND(B6*FA_Aseo,2)', MONEY); txt(wf.cell(6, 4), "Consolidado jul-2026 (archivo de costos SINFA, IPC aplicado)", italic=True)
txt(wf.cell(8, 1), "MÉTODO B – VIAT por tonelada = SMMLV × % VIAT", bold=True); fx(wf.cell(8, 2), '=ROUND(PARAMETROS!B36*PARAMETROS!B37,2)', MONEY)
txt(wf.cell(9, 1), "MÉTODO B – CDF con incentivo (CDF + VIAT)", bold=True); fx(wf.cell(9, 2), '=PARAMETROS!B38+B8', MONEY)
txt(wf.cell(10, 1), "MÉTODO B – Costo total por tonelada (+ RTC)", bold=True); fx(wf.cell(10, 2), '=B9+PARAMETROS!B39', MONEY)
txt(wf.cell(11, 1), "MÉTODO B – Tarifa final $/t = Costo × (1 + contribución)", bold=True); fx(wf.cell(11, 2), '=ROUND(B10*(1+PARAMETROS!B40),2)', MONEY)
txt(wf.cell(11, 4), "Archivo Macro_Facturacion_Aforados. Se actualiza cambiando SMMLV o CDF en PARAMETROS.", italic=True)
txt(wf.cell(13, 1), "Diferencia tarifa/t método B vs A", bold=True); fx(wf.cell(13, 2), '=B11/B5-1', PCT)
txt(wf.cell(13, 4), "Si es distinta de 0%, la Junta debe definir cuál método es el oficial antes de facturar.", italic=True, color="C00000")
txt(wf.cell(15, 1), "TARIFA EN USO ($/t)", bold=True, fill=GRN); fx(wf.cell(15, 2), '=IF(MetodoAfo="A",B5,B11)', MONEY, bold=True)
txt(wf.cell(16, 1), "VIAT POR FACTURA EN USO ($)", bold=True, fill=GRN); fx(wf.cell(16, 2), '=IF(MetodoAfo="A",B6,0)', MONEY, bold=True)
name("Afo_Vig", "AFORADOS!$B$5:$B$6"); name("Afo_Proy", "AFORADOS!$C$5:$C$6")
hdr(wf, 18, ["① Cliente", "② Fecha", "③ Peso (kg)", "Toneladas", "Valor por tonelaje ($)"])
ej = [("Alimentos Polar Colombia S.A.S.", dt.date(2026, 1, 29), 2790), ("Ingemetal W.F. S.A.S.", dt.date(2026, 2, 5), 5000)]
for i in range(40):
    rr = 19 + i
    if i < len(ej):
        inp(wf.cell(rr, 1), ej[i][0]); inp(wf.cell(rr, 2), ej[i][1], DATEF); inp(wf.cell(rr, 3), ej[i][2], '#,##0')
    else:
        inp(wf.cell(rr, 1), None); inp(wf.cell(rr, 2), None, DATEF); inp(wf.cell(rr, 3), None, '#,##0')
    fx(wf.cell(rr, 4), f'=IF(C{rr}="","",C{rr}/1000)', '#,##0.00'); fx(wf.cell(rr, 5), f'=IF(D{rr}="","",ROUND(D{rr}*$B$15,2))', MONEY)
txt(wf.cell(59, 1), "TOTAL", bold=True); fx(wf.cell(59, 4), '=SUM(D19:D58)', '#,##0.00', bold=True); fx(wf.cell(59, 5), '=SUM(E19:E58)', MONEY, bold=True)
txt(wf.cell(17, 1), "Filas 19–20 son EJEMPLO (viajes de enero-febrero 2026 del archivo de aforados). Reemplácelas por los viajes reales del período.", italic=True, color="C00000", border=False)
wf.merge_cells("A17:E17")
hdr(wf, 18, ["Cliente", "Toneladas", "Valor tonelaje", "VIAT factura", "TOTAL A FACTURAR"], c0=7)
clientes = ["Alimentos Polar Colombia S.A.S.", "Ingemetal W.F. S.A.S.", "The Elite Flower SAS CI", "Marly", "Morado", "Ekobojaca", "Banca de Alimentos"]
for i, cl in enumerate(clientes):
    rr = 19 + i
    inp(wf.cell(rr, 7), cl); fx(wf.cell(rr, 8), f'=SUMIF($A$19:$A$58,G{rr},$D$19:$D$58)', '#,##0.00')
    fx(wf.cell(rr, 9), f'=SUMIF($A$19:$A$58,G{rr},$E$19:$E$58)', MONEY); fx(wf.cell(rr, 10), f'=IF(H{rr}>0,$B$16,0)', MONEY)
    fx(wf.cell(rr, 11), f'=I{rr}+J{rr}', MONEY, bold=True)
txt(wf.cell(26, 7), "TOTAL", bold=True); fx(wf.cell(26, 8), '=SUM(H19:H25)', '#,##0.00', bold=True); fx(wf.cell(26, 11), '=SUM(K19:K25)', MONEY, bold=True)
txt(wf.cell(28, 7), "Advertencia del Consolidado: en 4 facturas reales de may-jun 2026 NO se cobró VIAT. Si se incorpora ahora, es un cargo nuevo para el usuario.", italic=True, color="C00000", border=False, size=9)
wf.merge_cells("G28:K30"); wf["G28"].alignment = Alignment(wrap_text=True, vertical="top")
widths(wf, {"A": 50, "B": 15, "C": 18, "D": 13, "E": 20, "F": 3, "G": 32, "H": 12, "I": 16, "J": 14, "K": 18})

# ============================== SIMULADOR ==================================
wsim = wb.create_sheet("SIMULADOR")
title(wsim, "SIMULADOR DE FACTURA (un suscriptor, un período)", "Escriba los datos en azul. Calcula acueducto, alcantarillado y aseo por tramos, y cuánto recibe de subsidio o aporta de contribución.", 7)
txt(wsim.cell(4, 1), "Categoría acueducto / alcantarillado", bold=True); inp(wsim.cell(4, 2), "Residencial", key=True)
txt(wsim.cell(5, 1), "Categoría de aseo", bold=True); inp(wsim.cell(5, 2), "Residencial Estrato 1", key=True)
txt(wsim.cell(6, 1), "Consumo del período (m³)", bold=True); inp(wsim.cell(6, 2), 30, '#,##0.0', key=True)
txt(wsim.cell(7, 1), "Tarifas a usar", bold=True); inp(wsim.cell(7, 2), "Vigentes", key=True)
txt(wsim.cell(8, 1), "¿Tiene alcantarillado? (SI/NO)", bold=True); inp(wsim.cell(8, 2), "SI")
d1 = DataValidation(type="list", formula1="=ACUEDUCTO!$A$6:$A$10"); d2 = DataValidation(type="list", formula1="=ASEO!$A$6:$A$19")
d3 = DataValidation(type="list", formula1='"Vigentes,Proyectadas"'); d4 = DataValidation(type="list", formula1='"SI,NO"')
for d, c in [(d1, "B4"), (d2, "B5"), (d3, "B7"), (d4, "B8")]: wsim.add_data_validation(d); d.add(c)
txt(wsim.cell(9, 1), "Desplazamiento de columnas (interno)", italic=True, color="808080"); fx(wsim.cell(9, 2), '=IF(B7="Proyectadas",16,0)')
hdr(wsim, 11, ["Concepto", "m³", "Tarifa unitaria", "Valor tarifa", "Costo unitario", "Valor a costo", "Subsidio (−) / Contribución (+)"])
tramos = [("Cargo fijo", '=1', 5, 1), ("Consumo básico", '=MIN($B$6,ConsBasico)', 6, 2), ("Consumo complementario", '=MIN(MAX($B$6-ConsBasico,0),LimCompl-ConsBasico)', 7, 3), ("Consumo suntuario", '=MAX($B$6-LimCompl,0)', 8, 4)]
rr = 12
for sv, sh in [("ACUEDUCTO", "ACUEDUCTO"), ("ALCANTARILLADO", "ALCANTARILLADO")]:
    txt(wsim.cell(rr, 1), sv, bold=True, fill=GRAY); rr += 1; first = rr
    for (lab, q, tcol, ccol) in tramos:
        txt(wsim.cell(rr, 1), "   " + lab)
        mult = '*IF($B$8="SI",1,0)' if sv == "ALCANTARILLADO" else ''
        fx(wsim.cell(rr, 2), q + mult, '#,##0.0')
        fx(wsim.cell(rr, 3), f'=INDEX({sh}!$B$6:$Y$10,MATCH($B$4,{sh}!$A$6:$A$10,0),{tcol}+$B$9)', MONEY, link=True)
        fx(wsim.cell(rr, 4), f'=ROUND(B{rr}*C{rr},2)', MONEY)
        fx(wsim.cell(rr, 5), f'=INDEX({sh}!$B$6:$Y$10,MATCH($B$4,{sh}!$A$6:$A$10,0),{ccol}+$B$9)', MONEY, link=True)
        fx(wsim.cell(rr, 6), f'=ROUND(B{rr}*E{rr},2)', MONEY); fx(wsim.cell(rr, 7), f'=D{rr}-F{rr}', MONEY)
        rr += 1
    txt(wsim.cell(rr, 1), f"Subtotal {sv.lower()}", bold=True)
    for c in (4, 6, 7): fx(wsim.cell(rr, c), f'=SUM({CL(c)}{first}:{CL(c)}{rr-1})', MONEY, bold=True)
    rr += 2
# rr now: acueducto 12..17 subtotal at 17, alc 19..24 subtotal 24 ; rr=26
txt(wsim.cell(rr, 1), "ASEO", bold=True, fill=GRAY); rr += 1
txt(wsim.cell(rr, 1), "   Tarifa de aseo del período"); fx(wsim.cell(rr, 2), 1, '0')
fx(wsim.cell(rr, 3), '=INDEX(ASEO!$A$6:$J$19,MATCH($B$5,ASEO!$A$6:$A$19,0),IF($B$7="Proyectadas",10,3))', MONEY, link=True)
fx(wsim.cell(rr, 4), f'=C{rr}', MONEY, bold=True)
fx(wsim.cell(rr, 5), '=INDEX(ASEO!$A$6:$J$19,MATCH($B$5,ASEO!$A$6:$A$19,0),IF($B$7="Proyectadas",9,2))', MONEY, link=True)
fx(wsim.cell(rr, 6), f'=E{rr}', MONEY); fx(wsim.cell(rr, 7), f'=D{rr}-F{rr}', MONEY, bold=True)
aseo_r = rr; rr += 2
txt(wsim.cell(rr, 1), "TOTAL FACTURA", bold=True, fill=GRN, size=11)
fx(wsim.cell(rr, 4), f'=D17+D24+D{aseo_r}', MONEY, bold=True, fill=GRN); fx(wsim.cell(rr, 6), f'=F17+F24+F{aseo_r}', MONEY, bold=True); fx(wsim.cell(rr, 7), f'=G17+G24+G{aseo_r}', MONEY, bold=True)
txt(wsim.cell(rr + 2, 1), "Para usuarios aforados (por tonelada) use la hoja AFORADOS. Cargos por otros conceptos (reconexión, intereses, etc.) no están incluidos.", italic=True, border=False)
wsim.merge_cells(start_row=rr + 2, start_column=1, end_row=rr + 2, end_column=7)
widths(wsim, {"A": 38, "B": 24, "C": 16, "D": 16, "E": 16, "F": 16, "G": 22})

# ============================== VALIDACION =================================
wv = wb.create_sheet("VALIDACION")
title(wv, "VALIDACIONES DE RIGOR (normativa CRA / Ley)", "Cada fila revisa una regla. OK = cumple. REVISAR / NO = hay que corregir o decidir antes de facturar o firmar la resolución.", 5)
hdr(wv, 4, ["#", "Qué se revisa", "Valor encontrado", "Resultado", "Norma"])
A, Lc = "ACUEDUCTO", "ALCANTARILLADO"
checks = [
 ("IPC acumulado acueducto/alcantarillado ≥ umbral", "=VarAcuAlc", PCT, '=IF(VarAcuAlc>=Umbral-0.000001,"OK – se puede actualizar","NO – aún no alcanza el 3%")', "Ley 142/1994 art. 125; CRA 1038/2026 Anexo 6.2.1.1"),
 ("IPC acumulado aseo ≥ umbral", "=VarAseo", PCT, '=IF(VarAseo>=Umbral-0.000001,"OK – se puede actualizar","NO – aún no alcanza el 3%")', "Res. CRA 943/2021 art. 5.3.5.2.9.1"),
 ("Metodología acueducto/alcantarillado para la fecha de aplicación", "=PARAMETROS!B19", None, '=IF(FechaAplic<=DATE(2026,12,31),"OK – CRA 825/2017 (transición)",IF(EsGC="POR DEFINIR","REVISAR – definir si es Gestor Comunitario","OK – CRA 1038/2026 (requiere estudio de costos nuevo)"))', "CRA 1038/2026 art. 23 y art. 2.1.1.1.1.7"),
 ("Consumo básico del período coincide con 22 m³ del manual", "=ConsBasico", '0', '=IF(ConsBasico=22,"OK","REVISAR")', "Res. CRA 750/2016 (11 m³/mes >2.000 msnm × 2 meses)"),
 ("Subsidio residencial acueducto (cargo fijo) ≤ máximo estrato 1", f"=-{A}!J6", PCT, f'=IF(-{A}!J6<=Sub1+0.00001,"OK","REVISAR")', "Ley 1450/2011 art. 125"),
 ("Subsidio residencial acueducto (básico) ≤ máximo estrato 1", f"=-{A}!K6", PCT, f'=IF(-{A}!K6<=Sub1+0.00001,"OK","REVISAR")', "Ley 1450/2011 art. 125"),
 ("Subsidio residencial acueducto (básico) ≤ máximo estrato 2", f"=-{A}!K6", PCT, f'=IF(-{A}!K6<=Sub2+0.00001,"OK","REVISAR – 45% supera el 40% del estrato 2: no aplicarlo a estratos 2 y 3")', "Ley 1450/2011 art. 125"),
 ("Subsidio residencial alcantarillado (básico) ≤ máximo estrato 2", f"=-{Lc}!K6", PCT, f'=IF(-{Lc}!K6<=Sub2+0.00001,"OK","REVISAR – 50% supera el 40% del estrato 2: no aplicarlo a estratos 2 y 3")', "Ley 1450/2011 art. 125"),
 ("Sin subsidio en complementario y suntuario (acueducto)", f"=MAX(ABS({A}!L6),ABS({A}!M6))", PCT, f'=IF(MAX(ABS({A}!L6),ABS({A}!M6))<0.0005,"OK","REVISAR")', "Res. CRA 750/2016; proyecto de resolución, parágrafo art. 1"),
 ("Sin subsidio en complementario y suntuario (alcantarillado)", f"=MAX(ABS({Lc}!L6),ABS({Lc}!M6))", PCT, f'=IF(MAX(ABS({Lc}!L6),ABS({Lc}!M6))<0.0005,"OK","REVISAR")', "Res. CRA 750/2016"),
 ("Contribución comercial acueducto ≥ 50% (todos los componentes)", f"=MIN({A}!J7:M7)", PCT, f'=IF(MIN({A}!J7:M7)>=MinCom-0.00001,"OK","REVISAR")', "Ley 1450/2011 art. 125"),
 ("Contribución comercial alcantarillado ≥ 50%", f"=MIN({Lc}!J7:M7)", PCT, f'=IF(MIN({Lc}!J7:M7)>=MinCom-0.00001,"OK","REVISAR")', "Ley 1450/2011 art. 125"),
 ("Contribución industrial acueducto ≥ 30%", f"=MIN({A}!J9:M9)", PCT, f'=IF(MIN({A}!J9:M9)>=MinInd-0.00001,"OK","REVISAR")', "Ley 1450/2011 art. 125"),
 ("Contribución industrial alcantarillado ≥ 30%", f"=MIN({Lc}!J9:M9)", PCT, f'=IF(MIN({Lc}!J9:M9)>=MinInd-0.00001,"OK","REVISAR")', "Ley 1450/2011 art. 125"),
 ("Oficial y Especial pagan el costo exacto (acueducto y alcantarillado)", f"=MAX(ABS(MIN({A}!J8:M8,{A}!J10:M10,{Lc}!J8:M8,{Lc}!J10:M10)),ABS(MAX({A}!J8:M8,{A}!J10:M10,{Lc}!J8:M8,{Lc}!J10:M10)))", PCT, '=IF(C19<0.0005,"OK","REVISAR")', "Manual Riveli; Acuerdo Municipal"),
 ("Factores implícitos = Acuerdo Municipal (acu, alc, aseo)", f'=COUNTIF({A}!Z6:Z10,"REVISAR")+COUNTIF({Lc}!Z6:Z10,"REVISAR")+COUNTIF(ASEO!K6:K19,"REVISAR")', '0', '=IF(C20=0,"OK","REVISAR – "&C20&" categoría(s) no cuadran")', "Acuerdo Municipal Facatativá 2022-2026"),
 ("Aseo: subsidios y contribuciones dentro de la ley", '=COUNTIF(ASEO!M6:M19,"REVISAR*")', '0', '=IF(C21=0,"OK","REVISAR – "&C21&" categoría(s)")', "Ley 1450/2011 art. 125"),
 ("Conciliación con la resolución (ene-feb/mar-abr × 1,0477 = vigente)", '=COUNTIF(F33:F45,"REVISAR")', '0', '=IF(C22=0,"OK – los 13 valores cuadran","REVISAR")', "Proyecto Resolución Junta 2026, arts. 1-3"),
 ("Aforados: diferencia entre método A y B", "=AFORADOS!B13", PCT, '=IF(ABS(AFORADOS!B13)<0.0005,"OK","REVISAR – la Junta debe definir el método oficial")', "Res. CRA 853/2018; Decreto 2412/2018"),
 ("Suscriptores a 31-dic-2024 registrados (para segmento CRA 1038)", "=MAX(PARAMETROS!B8:B9)", '#,##0', '=IF(COUNT(PARAMETROS!B8:B9)>0,"OK","REVISAR – escribir en PARAMETROS B8:B9")', "CRA 1038/2026 art. 2.1.1.1.1.6"),
 ("Fecha de inicio indicada en el proyecto de resolución (considerando 7)", '="Dice: desde 1-jul-2026"', None, '="REVISAR – la CRA 1038/2026 aplica desde 1-ene-2027 (art. 2.1.1.1.1.7); hasta 31-dic-2026 rige la CRA 825/2017 (art. 23)"', "CRA 1038/2026 arts. 23 y 2.1.1.1.1.7"),
 ("Manual Riveli: ejemplo de $11.164 (mar-abr) × 1,0477", '=ROUND(11164*1.0477,2)', MONEY, '="REVISAR – da $11.696, no $12.293: la base correcta es ene-feb ($11.732,86 × 1,0477 = $12.292,52)"', "Manual básico jul-2026, pág. 1 y 4"),
]
for i, (d, v, f, res, nrm) in enumerate(checks):
    rr = 5 + i
    txt(wv.cell(rr, 1), i + 1); txt(wv.cell(rr, 2), d, wrap=True); fx(wv.cell(rr, 3), v, f); fx(wv.cell(rr, 4), res); wv.cell(rr, 4).alignment = Alignment(wrap_text=True, vertical="center")
    txt(wv.cell(rr, 5), nrm, wrap=True, italic=True, color="404040")
last_check = 5 + len(checks) - 1
okfmt(wv, f"D5:D{last_check}")
# conciliación
txt(wv.cell(30, 1), "CONCILIACIÓN: valores de la resolución × 1,0477 frente a las tarifas vigentes del libro", bold=True, fill=LBLUE); wv.merge_cells("A30:F30")
hdr(wv, 32, ["Servicio", "Concepto", "Actual en resolución", "× FA jul-2026", "Vigente en el libro", "¿Cuadra?"])
conc = [("Acueducto", "Cargo fijo residencial", 11732.86, "ACUEDUCTO!F6"), ("Acueducto", "Básico residencial $/m³", 1358.49, "ACUEDUCTO!G6"),
        ("Acueducto", "Más de 22 m³ residencial", 2469.98, "ACUEDUCTO!H6"), ("Acueducto", "Cargo fijo comercial", 32852.02, "ACUEDUCTO!F7"),
        ("Acueducto", "Metro comercial", 3704.97, "ACUEDUCTO!G7"), ("Alcantarillado", "Cargo fijo residencial", 4668.80, "ALCANTARILLADO!F6"),
        ("Alcantarillado", "Básico residencial $/m³", 714.68, "ALCANTARILLADO!G6"), ("Alcantarillado", "Más de 22 m³ residencial", 1429.36, "ALCANTARILLADO!H6"),
        ("Alcantarillado", "Cargo fijo comercial", 15562.67, "ALCANTARILLADO!F7"), ("Alcantarillado", "Metro comercial", 2144.04, "ALCANTARILLADO!G7"),
        ("Aseo", "Residencial estrato 1", 35376.89, "ASEO!C6"), ("Aseo", "Sin recolección puerta a puerta", 29243.11, "ASEO!C10"), ("Aseo", "Comercial", 93242.71, "ASEO!C13")]
for i, (s, c, v, ref) in enumerate(conc):
    rr = 33 + i
    txt(wv.cell(rr, 1), s); txt(wv.cell(rr, 2), c); inp(wv.cell(rr, 3), v, MONEY)
    fx(wv.cell(rr, 4), f'=ROUND(C{rr}*INDEXACION!$B$21,2)', MONEY); fx(wv.cell(rr, 5), f'={ref}', MONEY, link=True)
    fx(wv.cell(rr, 6), f'=IF(ABS(D{rr}-E{rr})<0.005,"OK","REVISAR")')
okfmt(wv, "F33:F45")
widths(wv, {"A": 14, "B": 52, "C": 20, "D": 62, "E": 40, "F": 12})

# ============================== RESOLUCION =================================
wr = wb.create_sheet("RESOLUCION")
title(wr, "TABLAS PARA LA RESOLUCIÓN DE JUNTA DIRECTIVA (se llenan solas)", "Copie estas tablas en la resolución. ACTUAL = tarifa vigente; FINAL = tarifa proyectada con el factor de la hoja INDEXACION. Solo firme si la hoja VALIDACION no tiene REVISAR en las filas 1 y 2.", 4)
MESN = 'CHOOSE(MONTH({d}),"enero","febrero","marzo","abril","mayo","junio","julio","agosto","septiembre","octubre","noviembre","diciembre")&" de "&YEAR({d})'
fx(wr.cell(4, 1), '="CONSIDERANDO: Que el DANE certificó una variación del IPC entre "&' + MESN.format(d="MesBase") + '&" y "&' + MESN.format(d="MesFinal") + '&" de "&FIXED(VarAcuAlc*100,2)&"% (índice "&IndiceAA&"), "&IF(VarAcuAlc>=Umbral,"que supera","que NO alcanza")&" el umbral del "&FIXED(Umbral*100,0)&"% del artículo 125 de la Ley 142 de 1994."')
wr.merge_cells("A4:D4"); wr["A4"].alignment = Alignment(wrap_text=True, vertical="top"); wr.row_dimensions[4].height = 48
rr = 6
def bloque(titulo, filas, fa_cell):
    global rr
    txt(wr.cell(rr, 1), titulo, bold=True, fill=LBLUE); wr.merge_cells(start_row=rr, start_column=1, end_row=rr, end_column=4); rr += 1
    hdr(wr, rr, ["Concepto", "ACTUAL", "INCREMENTO", "FINAL"]); rr += 1
    for (lab, a, b) in filas:
        txt(wr.cell(rr, 1), lab); fx(wr.cell(rr, 2), "=" + a, MONEY, link=True)
        fx(wr.cell(rr, 3), f'="+"&FIXED(({b}/{a}-1)*100,2)&"%"'); wr.cell(rr, 3).alignment = Alignment(horizontal="center")
        fx(wr.cell(rr, 4), "=" + b, MONEY, link=True, bold=True); rr += 1
    rr += 1
def svc_rows(sh):
    out = []
    for i, cat in enumerate(cats):
        r_ = 6 + i
        out.append((f"Cargo fijo {cat.lower()}", f"{sh}!F{r_}", f"{sh}!V{r_}"))
        if cat == "Residencial":
            out += [("Consumo básico 0–22 m³ ($/m³)", f"{sh}!G{r_}", f"{sh}!W{r_}"), ("Consumo de 22 m³ en adelante ($/m³)", f"{sh}!H{r_}", f"{sh}!X{r_}")]
        else:
            out.append((f"Valor metro {cat.lower()} ($/m³)", f"{sh}!G{r_}", f"{sh}!W{r_}"))
    return out
bloque("ARTÍCULO PRIMERO – ACUEDUCTO", svc_rows("ACUEDUCTO"), "FA_AA_CF")
bloque("ARTÍCULO SEGUNDO – ALCANTARILLADO", svc_rows("ALCANTARILLADO"), "FA_AA_CF")
bloque("ARTÍCULO TERCERO – ASEO", [(a[0], f"ASEO!C{6+i}", f"ASEO!J{6+i}") for i, a in enumerate(aseo)] +
       [("Industrial aforado ($/tonelada) – método A", "AFORADOS!B5", "AFORADOS!C5"), ("VIAT por factura – método A", "AFORADOS!B6", "AFORADOS!C6")], "FA_Aseo")
txt(wr.cell(rr, 1), "ARTÍCULO CUARTO: los factores de subsidio y contribución del Acuerdo Municipal de Facatativá 2022-2026 no se modifican. Recuerde: informar a la CRA y a la SSPD, publicar las tarifas antes de aplicarlas y reportar en el SUI.", italic=True, border=False)
wr.merge_cells(start_row=rr, start_column=1, end_row=rr + 1, end_column=4); wr.cell(rr, 1).alignment = Alignment(wrap_text=True, vertical="top")
widths(wr, {"A": 46, "B": 18, "C": 14, "D": 18})

# ============================== NORMATIVA ==================================
wn = wb.create_sheet("NORMATIVA")
title(wn, "MARCO NORMATIVO, FÓRMULAS Y HALLAZGOS", "Resumen de las normas que usa este libro. Las normas CRA se consultaron en el Gestor Normativo de la CRA (normas.cra.gov.co) el 31-oct-2026.", 4)
hdr(wn, 4, ["Norma", "Qué dice (resumen)", "Cómo se usa en este libro", "Vigencia"])
norms = [
 ("Constitución Política, art. 367", "Régimen tarifario con criterios de costos, solidaridad y redistribución.", "Fundamento general.", "Permanente"),
 ("Ley 142/1994, art. 87", "Criterios: eficiencia, neutralidad, solidaridad, redistribución, suficiencia financiera, simplicidad y transparencia.", "Justifica la corrección del rezago de mar-abr 2026.", "Permanente"),
 ("Ley 142/1994, art. 125", "Las tarifas se actualizan con los índices de la fórmula cada vez que acumulen al menos 3%.", "Umbral 3% (PARAMETROS!B24, INDEXACION fila 12-14).", "Permanente"),
 ("Ley 142/1994, art. 99.6", "Subsidios solo para estratos 1, 2 y 3, sobre el consumo de subsistencia (básico).", "Subsidio solo en el tramo básico.", "Permanente"),
 ("Ley 1450/2011, art. 125", "Subsidio máximo: E1 70%, E2 40%, E3 15%. Contribución mínima: E5 50%, E6 60%, comercial 50%, industrial 30%.", "Límites en PARAMETROS!B27:B33; hoja VALIDACION.", "Vigente (verificar prórroga en el PND vigente)"),
 ("Decreto 1077/2015, art. 2.3.4.2.2", "Equilibrio entre subsidios y contribuciones; factores los fija el Concejo.", "Factores del Acuerdo Municipal en columnas N:Q y ASEO!H.", "Vigente"),
 ("Res. CRA 750/2016", "Consumo básico: 11 m³/mes (>2.000 msnm), 13 m³ (1.000–2.000), 16 m³ (<1.000). Sobre el básico no hay subsidio.", "Consumo básico 22 m³ bimestral (PARAMETROS!B14:B15).", "Vigente"),
 ("Res. CRA 825/2017 (Título 2 Res. CRA 943/2021)", "Metodología de pequeños prestadores de acueducto y alcantarillado. CMA, CMO, CMI indexados con IPC.", "Índice IPC total para actualizaciones hasta el 31-dic-2026.", "Hasta 31-dic-2026 (art. 23 CRA 1038/2026)"),
 ("Res. CRA 1038/2026 (30-jun-2026)", "Nuevo marco para prestadores de hasta 5.000 suscriptores y gestores comunitarios. Dos segmentos con 4 subsegmentos. Cargo fijo = CMA; cargo por consumo = CMO + CMI + CMICT. Vigencia 5 años.", "Segmento/subsegmento en PARAMETROS!B11:B12; índices desde 2027 en INDEXACION.", "Aplicación desde 1-ene-2027 (art. 2.1.1.1.1.7)"),
 ("Res. CRA 1038/2026, art. 2.1.1.1.2.2.1.6 y Anexo 6.2.1.1", "Indexación: IPC sin alimentos ni regulados para CMA, CMOG y CMICT; IPC total para CMI. Gestor comunitario: IPC sin alimentos ni regulados. Índices a 2 decimales, factor a 4 decimales, resultado a 2 decimales. Acumulación sin solapamientos.", "Fórmulas ROUND en INDEXACION; mes base se reinicia en cada actualización.", "Desde 1-ene-2027"),
 ("Res. CRA 1038/2026, art. 2.1.1.1.2.2.1.2", "Recálculo anual de costos (1er segmento) entre el 1 de enero y el 31 de mayo de cada año.", "Cronograma (abajo).", "Desde 2028 (2º año tarifario)"),
 ("Res. CRA 1038/2026, Parágrafo 1 del art. 2.1.1.1.2.2.1.6", "Los costos laborales ligados al SMMLV pueden actualizarse con la variación del SMMLV.", "SMMLV en PARAMETROS!B36.", "Desde 2027"),
 ("Res. CRA 853/2018 (aclarada CRA 892/2019); art. 5.3.5.2.9.1 Res. CRA 943/2021", "Aseo en municipios de hasta 5.000 suscriptores. Actualización con IPC cuando acumule ≥ 3%; informar a la CRA y a la SSPD; factor a 4 decimales, resultado a 2.", "FA aseo = IPC total (INDEXACION!B14).", "Vigente"),
 ("Decreto MVCT 2412/2018", "Crea el VIAT (Incentivo al Aprovechamiento y Tratamiento de residuos).", "Hoja AFORADOS.", "Vigente"),
 ("Res. CRA 943/2021, Título 6, Parte 8, Libro 1", "Reglas de aplicación, publicación e información de las variaciones tarifarias a la CRA, SSPD y usuarios.", "Paso 5 del procedimiento (INICIO).", "Vigente"),
]
for i, row in enumerate(norms):
    for j, v in enumerate(row): txt(wn.cell(5 + i, 1 + j), v, wrap=True, bold=(j == 0))
r0 = 5 + len(norms) + 1
txt(wn.cell(r0, 1), "FÓRMULAS DEL LIBRO", bold=True, fill=LBLUE); wn.merge_cells(start_row=r0, start_column=1, end_row=r0, end_column=4)
forms = [("Factor de actualización", "FA = ROUND( ROUND(IPC final;2) / ROUND(IPC base;2) ; 4 )"),
         ("Variación acumulada", "Var = FA − 1  → se actualiza solo si Var ≥ 3%"),
         ("Costo o tarifa actualizada", "Nuevo = ROUND( Vigente × FA ; 2 )"),
         ("Tarifa desde el costo", "Tarifa = Costo × (1 + factor)   (factor negativo = subsidio; positivo = contribución)"),
         ("Factura acueducto/alcantarillado", "Cargo fijo + m³ básico × tarifa básica + m³ complementario × tarifa compl. + m³ suntuario × tarifa sunt."),
         ("Aseo aforado – método A", "Toneladas × tarifa/t + VIAT por factura"),
         ("Aseo aforado – método B", "Toneladas × [ (CDF + SMMLV × 0,8% + RTC) × (1 + 30%) ]"),
         ("Desde 2027 (1er segmento)", "FA consumo = %CMI × FA(IPC total) + (1 − %CMI) × FA(IPC sin alimentos ni regulados)")]
for i, (a, b) in enumerate(forms):
    txt(wn.cell(r0 + 1 + i, 1), a, bold=True); txt(wn.cell(r0 + 1 + i, 2), b); wn.merge_cells(start_row=r0 + 1 + i, start_column=2, end_row=r0 + 1 + i, end_column=4)
r1 = r0 + len(forms) + 2
txt(wn.cell(r1, 1), "HALLAZGOS AL REVISAR LOS DOCUMENTOS", bold=True, fill=RED); wn.merge_cells(start_row=r1, start_column=1, end_row=r1, end_column=4)
hall = [
 ("1. Fecha de la CRA 1038/2026", "El proyecto de resolución (considerando 7) dice que la CRA 1038 aplica desde el 1-jul-2026. El texto oficial (art. 23 y art. 2.1.1.1.1.7) dice: se sigue con la CRA 825/2017 hasta el 31-dic-2026 y la nueva metodología inicia el 1-ene-2027. Corregir el considerando."),
 ("2. Índice desde 2027", "Con la CRA 1038/2026 ya no se usa solo el IPC total: CMA/CMOG/CMICT (y toda la tarifa comunitaria) se indexan con el IPC sin alimentos ni regulados. El libro ya lo cambia solo según la fecha de aplicación."),
 ("3. ¿Gestor comunitario?", "Siendo una asociación de suscriptores, Triple A puede clasificar como Gestor Comunitario (segundo segmento, tarifa comunitaria aprobada en Asamblea). Definir en PARAMETROS!B10 y preparar el estudio de costos antes del 1-ene-2027."),
 ("4. Ejemplo del manual básico", "El manual dice que $11.164 (mar-abr) × 1,0477 = $11.696 y también que sube a $12.293. La base correcta es ene-feb: $11.732,86 × 1,0477 = $12.292,52."),
 ("5. Subsidio residencial único", "Acueducto y alcantarillado tienen una sola tarifa 'Residencial' con 45%/50% de subsidio en el básico. La ley permite máximo 40% al estrato 2 y 15% al estrato 3. Si hay usuarios de estrato 2 o 3, se necesitan tarifas por estrato."),
 ("6. Aforados: dos cálculos", "Consolidado: $79.392,84/t + VIAT $4.075,13 por factura. Archivo de aforados: $97.913,02/t con VIAT incluido (≈ +23%). La Junta debe definir uno. El Consolidado advierte que el VIAT no se venía cobrando."),
 ("7. Próxima actualización", "Con IPC a oct-2026 (161,32) el acumulado desde jun-2026 (159,53) es 1,12%: aún NO se puede actualizar. Seguir cargando el IPC mensual."),
]
for i, (a, b) in enumerate(hall):
    rr = r1 + 1 + i; txt(wn.cell(rr, 1), a, bold=True, wrap=True); txt(wn.cell(rr, 2), b, wrap=True); wn.merge_cells(start_row=rr, start_column=2, end_row=rr, end_column=4); wn.row_dimensions[rr].height = 44
r2 = r1 + len(hall) + 2
txt(wn.cell(r2, 1), "CRONOGRAMA", bold=True, fill=LBLUE); wn.merge_cells(start_row=r2, start_column=1, end_row=r2, end_column=4)
cron = [(dt.date(2026, 11, 10), "DANE publica el IPC de octubre 2026 (aprox.). Cargarlo en la hoja IPC."),
        (dt.date(2026, 12, 31), "Último día de la metodología CRA 825/2017 para acueducto y alcantarillado."),
        (dt.date(2027, 1, 1), "Inicio obligatorio de la Res. CRA 1038/2026 (costos de referencia o tarifa comunitaria nuevos). Nuevo SMMLV."),
        (dt.date(2027, 5, 31), "Límite del recálculo anual de costos (desde el 2º año tarifario, 1er segmento).")]
for i, (d, t) in enumerate(cron):
    rr = r2 + 1 + i; st(wn.cell(rr, 1, d), fmt=DATEF, bold=True); txt(wn.cell(rr, 2), t, wrap=True); wn.merge_cells(start_row=rr, start_column=2, end_row=rr, end_column=4)
widths(wn, {"A": 38, "B": 60, "C": 44, "D": 30})

# ============================== HISTORICO ==================================
wh = wb.create_sheet("HISTORICO")
title(wh, "HISTÓRICO DE ACTUALIZACIONES TARIFARIAS", "La macro AplicarActualizacion agrega una fila por cada actualización. Conserve los soportes (boletín DANE) como exige la CRA.", 8)
hdr(wh, 3, ["Fecha registro", "Servicio", "Mes base", "Mes final", "Índice", "Factor", "Variación", "Soporte"])
for i, s in enumerate(["Acueducto y Alcantarillado (base ene-feb 2026)", "Aseo (base mar-abr 2026)"]):
    rr = 4 + i
    st(wh.cell(rr, 1, dt.date(2026, 7, 1)), fmt=DATEF); txt(wh.cell(rr, 2), s); st(wh.cell(rr, 3, dt.date(2025, 12, 31)), fmt=MES)
    st(wh.cell(rr, 4, dt.date(2026, 6, 30)), fmt=MES); txt(wh.cell(rr, 5), "IPC total"); st(wh.cell(rr, 6, 1.0477), fmt=FAC)
    fx(wh.cell(rr, 7), f"=F{rr}-1", PCT); txt(wh.cell(rr, 8), "Boletín técnico IPC jun-2026 (DANE); proyecto de Resolución de Junta 2026")
widths(wh, {"A": 14, "B": 44, "C": 11, "D": 11, "E": 30, "F": 9, "G": 10, "H": 60})

# ================================ MACRO ====================================
wm = wb.create_sheet("MACRO")
title(wm, "MACROS (VBA) — cómo instalarlas", None, 2)
steps = ["1. Guarde este archivo como 'Libro de Excel habilitado para macros (*.xlsm)'.",
         "2. Presione Alt + F11 (editor de Visual Basic) → menú Archivo → Importar archivo → elija ModTarifas.bas (viene junto a este Excel).",
         "   (Si no tiene el .bas: Insertar → Módulo y pegue el código de abajo, desde la línea 'Option Explicit').",
         "3. Cierre el editor. Ejecute las macros con Alt + F8:",
         "   • ActualizarIPC – agrega el IPC del mes siguiente (intenta bajarlo del DANE; si no puede, se lo pide).",
         "   • AplicarActualizacion – solo si el acumulado es ≥ 3%: archiva lo vigente, pasa lo proyectado a vigente, registra el histórico y reinicia el mes base.",
         "   • ExportarResolucionPDF – guarda la hoja RESOLUCION en PDF junto al archivo.",
         "Sin macros el libro también funciona: escriba el IPC en la hoja IPC y copie (pegado de valores) las columnas proyectadas sobre las vigentes."]
for i, s in enumerate(steps): txt(wm.cell(3 + i, 1), s, border=False, bold=i in (0, 1, 3))
code = open(BAS, encoding="utf-8").read().splitlines()
txt(wm.cell(13, 1), "CÓDIGO", bold=True, fill=LBLUE)
for i, line in enumerate(code):
    c = wm.cell(14 + i, 1, line if not line.startswith("=") else "'" + line); c.font = Font(name="Consolas", size=9)
wm.column_dimensions["A"].width = 140

# ================================ INICIO ===================================
title(ws0, "MANUAL TARIFARIO INTEGRAL — TRIPLE A DEL BARRIO CARTAGENA (Facatativá)", "Acueducto, Alcantarillado y Aseo. Libro formulado: actualización por IPC, validaciones legales (CRA / Ley 142 / Ley 1450), simulador de factura, aforados y tablas para la resolución. Preparado el 31-oct-2026 con IPC hasta oct-2026.", 4)
txt(ws0.cell(4, 1), "PANEL DE ESTADO", bold=True, fill=NAVY, color="FFFFFF"); ws0.merge_cells("A4:D4")
panel = [("Último IPC cargado", "=MesFinal", MES), ("IPC total del último mes", "=INDEXACION!B7", '0.00'),
         ("Mes base (última actualización)", "=MesBase", MES), ("Variación acumulada Acueducto/Alcantarillado", "=VarAcuAlc", PCT),
         ("Variación acumulada Aseo", "=VarAseo", PCT), ("¿Se puede actualizar?", "=INDEXACION!D12", None),
         ("Metodología vigente para la fecha de aplicación", "=PARAMETROS!B19", None), ("Segmento CRA 1038/2026", "=PARAMETROS!B11", None),
         ("Validaciones con alerta (hoja VALIDACION)", f'=COUNTIF(VALIDACION!D5:D{last_check},"REVISAR*")+COUNTIF(VALIDACION!D5:D{last_check},"NO *")', '0')]
for i, (a, f, fm) in enumerate(panel):
    rr = 5 + i; txt(ws0.cell(rr, 1), a, bold=True); fx(ws0.cell(rr, 2), f, fm, link=True); ws0.merge_cells(start_row=rr, start_column=2, end_row=rr, end_column=4)
okfmt(ws0, "B10:B10")
txt(ws0.cell(15, 1), "PROCEDIMIENTO MENSUAL (5 pasos)", bold=True, fill=LBLUE); ws0.merge_cells("A15:D15")
pasos = ["1. Cuando el DANE publique el IPC (≈ día 8), escríbalo en la hoja IPC o ejecute la macro ActualizarIPC.",
         "2. Mire el PANEL: si la variación acumulada es menor al 3%, no se hace nada más ese mes.",
         "3. Si llega al 3%: revise la hoja VALIDACION (todo en OK) y las columnas proyectadas de ACUEDUCTO, ALCANTARILLADO, ASEO y AFORADOS.",
         "4. Copie las tablas de la hoja RESOLUCION a la resolución de Junta Directiva y ejecute AplicarActualizacion.",
         "5. Informe a la CRA y a la SSPD, publique las nuevas tarifas antes de aplicarlas, cárguelas en SINFA y repórtelas en el SUI."]
for i, p in enumerate(pasos): txt(ws0.cell(16 + i, 1), p, wrap=True); ws0.merge_cells(start_row=16 + i, start_column=1, end_row=16 + i, end_column=4); ws0.row_dimensions[16 + i].height = 28
txt(ws0.cell(22, 1), "CONTENIDO", bold=True, fill=LBLUE); ws0.merge_cells("A22:D22")
idx = [("PARAMETROS", "Datos del prestador, consumo básico, mes base, límites legales"), ("IPC", "Serie oficial DANE (total y sin alimentos ni regulados)"),
       ("INDEXACION", "Factor de actualización y umbral del 3%"), ("ACUEDUCTO", "Costo vs. tarifa, factores del Acuerdo, proyección"),
       ("ALCANTARILLADO", "Costo vs. tarifa, factores del Acuerdo, proyección"), ("ASEO", "14 categorías con subsidio/contribución y límites legales"),
       ("AFORADOS", "Aseo industrial por tonelada + VIAT y registro de viajes"), ("SIMULADOR", "Factura de un suscriptor por tramos"),
       ("VALIDACION", "Chequeos de rigor normativo y conciliación con la resolución"), ("RESOLUCION", "Tablas ACTUAL / INCREMENTO / FINAL para la Junta"),
       ("NORMATIVA", "Normas, fórmulas, hallazgos y cronograma"), ("HISTORICO", "Registro de actualizaciones"), ("MACRO", "Código VBA e instalación")]
for i, (s, d) in enumerate(idx):
    rr = 23 + i; c = ws0.cell(rr, 1, s); c.hyperlink = f"#'{s}'!A1"; st(c, bold=True, color="0563C1")
    txt(ws0.cell(rr, 2), d); ws0.merge_cells(start_row=rr, start_column=2, end_row=rr, end_column=4)
txt(ws0.cell(37, 1), "CONVENCIONES DE COLOR", bold=True, fill=LBLUE); ws0.merge_cells("A37:D37")
for i, (t, col, fl) in enumerate([("Texto azul: dato que usted escribe", "0000FF", None), ("Fondo amarillo: dato clave por revisar", "0000FF", YEL),
                                  ("Texto negro: fórmula (no modificar)", "000000", None), ("Texto verde: viene de otra hoja", "008000", None)]):
    c = ws0.cell(38 + i, 1, t); st(c, color=col, fill=fl); ws0.merge_cells(start_row=38 + i, start_column=1, end_row=38 + i, end_column=2)
txt(ws0.cell(43, 1), "Fuentes: Res. CRA 1038/2026, 943/2021, 853/2018, 750/2016 (normas.cra.gov.co); Concepto CRA 49981/2024; IPC DANE vía Banco de la República; documentos de Riveli Consultores (Manual básico, Consolidado jul-2026, Costo vs. Tarifa); proyecto de Resolución de Junta 2026; archivo Macro_Facturacion_Aforados.", italic=True, color="404040", border=False, size=9)
ws0.merge_cells("A43:D45"); ws0["A43"].alignment = Alignment(wrap_text=True, vertical="top")
widths(ws0, {"A": 46, "B": 30, "C": 30, "D": 30})
for w in wb.worksheets:
    w.sheet_view.showGridLines = False
wb.save(OUT); print("saved", OUT)
