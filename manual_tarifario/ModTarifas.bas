Attribute VB_Name = "ModTarifas"
Option Explicit
'==========================================================================
' MANUAL TARIFARIO INTEGRAL - TRIPLE A DEL BARRIO CARTAGENA (Facatativa)
' Macros:
'   ActualizarIPC          -> agrega el IPC del mes siguiente (intenta DANE,
'                             si no puede, lo pide por teclado)
'   AplicarActualizacion   -> si el IPC acumulado >= 3% (Ley 142 art.125),
'                             archiva las tarifas vigentes, pasa las
'                             proyectadas a vigentes y reinicia el mes base
'   ExportarResolucionPDF  -> guarda la hoja RESOLUCION en PDF
' Todo el libro funciona con formulas; las macros solo automatizan pasos.
'==========================================================================

Private Function NombreMes(ByVal m As Integer) As String
    NombreMes = Choose(m, "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", _
                "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre")
End Function

Private Function MesCorto(ByVal m As Integer) As String
    MesCorto = Choose(m, "ene", "feb", "mar", "abr", "may", "jun", "jul", "ago", "sep", "oct", "nov", "dic")
End Function

Private Function FinDeMes(ByVal d As Date) As Date
    FinDeMes = DateSerial(Year(d), Month(d) + 1, 0)
End Function

'--- Intenta leer el indice IPC del anexo oficial del DANE -----------------
Private Function DescargarIPCDane(ByVal mes As Date) As Variant
    Dim url As String, tmp As String, http As Object, stm As Object
    Dim wb As Workbook, sh As Worksheet, cMes As Range, r As Long, c As Long
    Dim etiqueta As String
    DescargarIPCDane = Empty
    On Error GoTo Falla
    etiqueta = MesCorto(Month(mes)) & Year(mes)
    url = "https://www.dane.gov.co/files/operaciones/IPC/" & etiqueta & _
          "/anex-IPC-Indices-" & etiqueta & ".xlsx"
    Set http = CreateObject("MSXML2.XMLHTTP")
    http.Open "GET", url, False
    http.send
    If http.Status <> 200 Then GoTo Falla
    tmp = Environ$("TEMP") & "\ipc_dane_" & etiqueta & ".xlsx"
    Set stm = CreateObject("ADODB.Stream")
    stm.Type = 1: stm.Open: stm.Write http.responseBody
    stm.SaveToFile tmp, 2: stm.Close
    Application.ScreenUpdating = False
    Set wb = Workbooks.Open(tmp, ReadOnly:=True)
    For Each sh In wb.Worksheets
        Set cMes = sh.UsedRange.Find(What:=NombreMes(Month(mes)), LookAt:=xlWhole, MatchCase:=False)
        If Not cMes Is Nothing Then
            For r = cMes.Row - 1 To Application.Max(1, cMes.Row - 40) Step -1
                For c = 1 To sh.UsedRange.Columns.Count + sh.UsedRange.Column
                    If sh.Cells(r, c).Value = Year(mes) Then
                        If IsNumeric(sh.Cells(cMes.Row, c).Value) Then
                            If sh.Cells(cMes.Row, c).Value > 50 And sh.Cells(cMes.Row, c).Value < 1000 Then
                                DescargarIPCDane = Round(sh.Cells(cMes.Row, c).Value, 2)
                                wb.Close False
                                Application.ScreenUpdating = True
                                Exit Function
                            End If
                        End If
                    End If
                Next c
            Next r
        End If
    Next sh
    wb.Close False
Falla:
    Application.ScreenUpdating = True
End Function

Public Sub ActualizarIPC()
    Dim ws As Worksheet, fila As Long, mes As Date, v As Variant, vSar As Variant
    Set ws = ThisWorkbook.Worksheets("IPC")
    fila = 5
    Do While ws.Cells(fila, 2).Value <> ""
        fila = fila + 1
    Loop
    If ws.Cells(fila, 1).Value = "" Then
        ws.Cells(fila, 1).Value = FinDeMes(DateSerial(Year(ws.Cells(fila - 1, 1).Value), Month(ws.Cells(fila - 1, 1).Value) + 1, 1))
        ws.Range(ws.Cells(fila - 1, 4), ws.Cells(fila - 1, 8)).Copy ws.Cells(fila, 4)
    End If
    mes = ws.Cells(fila, 1).Value

    v = DescargarIPCDane(mes)
    If IsEmpty(v) Then
        v = InputBox("No se pudo descargar el anexo del DANE para " & NombreMes(Month(mes)) & " " & Year(mes) & "." & vbCrLf & _
            "Escriba el INDICE IPC total (base dic-2018=100), tal como aparece en el boletin del DANE " & _
            "(https://www.dane.gov.co > IPC). Use coma o punto decimal.", "IPC total " & MesCorto(Month(mes)) & "-" & Year(mes))
        If v = "" Then Exit Sub
        v = CDbl(Replace(v, ".", Application.International(xlDecimalSeparator)))
    End If
    vSar = InputBox("Indice IPC SIN ALIMENTOS NI REGULADOS de " & NombreMes(Month(mes)) & " " & Year(mes) & vbCrLf & _
        "(Banco de la Republica, serie 'IPC sin alimentos ni regulados', base dic-2018=100)." & vbCrLf & _
        "Lo exige la Res. CRA 1038/2026 desde 2027. Deje vacio si aun no lo tiene.", "IPC sin alimentos ni regulados")
    ws.Cells(fila, 2).Value = Round(v, 2)
    If vSar <> "" Then ws.Cells(fila, 3).Value = Round(CDbl(Replace(vSar, ".", Application.International(xlDecimalSeparator))), 2)
    ws.Cells(fila, 7).Value = "Registrado " & Format(Now, "dd/mm/yyyy hh:nn")
    Application.Calculate
    MsgBox "IPC de " & NombreMes(Month(mes)) & " " & Year(mes) & " registrado: " & ws.Cells(fila, 2).Value & vbCrLf & _
        "Variacion acumulada desde el mes base (acueducto/alcantarillado): " & Format(Range("VarAcuAlc").Value, "0.00%") & vbCrLf & _
        "Variacion acumulada desde el mes base (aseo): " & Format(Range("VarAseo").Value, "0.00%") & vbCrLf & _
        "Umbral Ley 142 art. 125: " & Format(Range("Umbral").Value, "0.00%"), vbInformation, "IPC actualizado"
End Sub

Private Sub Archivar(ByVal titulo As String)
    Dim sh As Worksheet, nombre As String, r As Long
    nombre = "ARCH_" & Format(Now, "yyyymmdd_hhnn")
    Set sh = ThisWorkbook.Worksheets.Add(After:=ThisWorkbook.Worksheets(ThisWorkbook.Worksheets.Count))
    sh.Name = nombre
    sh.Range("A1").Value = titulo
    r = 3
    sh.Cells(r, 1).Value = "ACUEDUCTO (vigente antes de actualizar)": r = r + 1
    ThisWorkbook.Worksheets("ACUEDUCTO").Range("A5:I10").Copy
    sh.Cells(r, 1).PasteSpecial xlPasteValuesAndNumberFormats: r = r + 8
    sh.Cells(r, 1).Value = "ALCANTARILLADO (vigente antes de actualizar)": r = r + 1
    ThisWorkbook.Worksheets("ALCANTARILLADO").Range("A5:I10").Copy
    sh.Cells(r, 1).PasteSpecial xlPasteValuesAndNumberFormats: r = r + 8
    sh.Cells(r, 1).Value = "ASEO (vigente antes de actualizar)": r = r + 1
    ThisWorkbook.Worksheets("ASEO").Range("A5:D19").Copy
    sh.Cells(r, 1).PasteSpecial xlPasteValuesAndNumberFormats
    Application.CutCopyMode = False
End Sub

Private Sub RegistrarHistorico(ByVal servicio As String, ByVal mBase As Date, ByVal mFinal As Date, _
                               ByVal indice As String, ByVal fa As Double)
    Dim ws As Worksheet, f As Long
    Set ws = ThisWorkbook.Worksheets("HISTORICO")
    f = ws.Cells(ws.Rows.Count, 1).End(xlUp).Row + 1
    ws.Cells(f, 1).Value = Date
    ws.Cells(f, 2).Value = servicio
    ws.Cells(f, 3).Value = mBase
    ws.Cells(f, 4).Value = mFinal
    ws.Cells(f, 5).Value = indice
    ws.Cells(f, 6).Value = fa
    ws.Cells(f, 7).Value = fa - 1
    ws.Cells(f, 8).Value = "Aplicado con macro AplicarActualizacion"
End Sub

Public Sub AplicarActualizacion()
    Dim okAA As Boolean, okAs As Boolean, msg As String, mFinal As Date
    Application.Calculate
    okAA = (Range("VarAcuAlc").Value >= Range("Umbral").Value - 0.000001)
    okAs = (Range("VarAseo").Value >= Range("Umbral").Value - 0.000001)
    mFinal = Range("MesFinal").Value
    If Not okAA And Not okAs Then
        MsgBox "Todavia NO se puede actualizar." & vbCrLf & _
            "Acumulado acueducto/alcantarillado: " & Format(Range("VarAcuAlc").Value, "0.00%") & vbCrLf & _
            "Acumulado aseo: " & Format(Range("VarAseo").Value, "0.00%") & vbCrLf & _
            "Se requiere al menos " & Format(Range("Umbral").Value, "0.00%") & " (Ley 142/1994 art. 125).", vbExclamation
        Exit Sub
    End If
    msg = "Se aplicara la actualizacion tarifaria con mes final " & Format(mFinal, "mmm-yyyy") & ":" & vbCrLf
    If okAA Then msg = msg & " - Acueducto y Alcantarillado: factor " & Format(Range("FA_AA_CF").Value, "0.0000") & vbCrLf
    If okAs Then msg = msg & " - Aseo y Aforados: factor " & Format(Range("FA_Aseo").Value, "0.0000") & vbCrLf
    msg = msg & vbCrLf & "Las tarifas vigentes se archivan en una hoja ARCH_ y las proyectadas pasan a ser vigentes. Continuar?"
    If MsgBox(msg, vbYesNo + vbQuestion, "Aplicar actualizacion") <> vbYes Then Exit Sub

    Archivar "Tarifas vigentes archivadas el " & Format(Now, "dd/mm/yyyy hh:nn") & " antes de actualizar a " & Format(mFinal, "mmm-yyyy")
    If okAA Then
        Range("Acu_Vig").Value = Range("Acu_Proy").Value
        Range("Alc_Vig").Value = Range("Alc_Proy").Value
        RegistrarHistorico "Acueducto y Alcantarillado", Range("MesBase").Value, mFinal, Range("IndiceAA").Value, Range("FA_AA_CF").Value
        Range("MesBase").Value = mFinal
    End If
    If okAs Then
        Range("Aseo_Vig").Value = Range("Aseo_Proy").Value
        Range("Afo_Vig").Value = Range("Afo_Proy").Value
        RegistrarHistorico "Aseo y Aforados", Range("MesBaseAseo").Value, mFinal, "IPC total", Range("FA_Aseo").Value
        Range("MesBaseAseo").Value = mFinal
    End If
    Range("MesFinalManual").ClearContents
    Application.Calculate
    MsgBox "Actualizacion aplicada. Revise la hoja VALIDACION, imprima la hoja RESOLUCION e informe a la CRA y a la SSPD " & _
           "y publique las tarifas antes de facturar.", vbInformation
End Sub

Public Sub ExportarResolucionPDF()
    Dim ruta As String
    ruta = ThisWorkbook.Path & Application.PathSeparator & "Resolucion_Tarifaria_" & Format(Date, "yyyymmdd") & ".pdf"
    ThisWorkbook.Worksheets("RESOLUCION").ExportAsFixedFormat Type:=xlTypePDF, Filename:=ruta, OpenAfterPublish:=True
End Sub
