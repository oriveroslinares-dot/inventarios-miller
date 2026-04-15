import streamlit as st
import pandas as pd
from datetime import datetime

# -----------------------------
# INICIALIZACIÓN DE DATOS
# -----------------------------
if "productos" not in st.session_state:
    st.session_state.productos = pd.DataFrame(columns=[
        "id", "nombre", "categoria", "unidad",
        "costo_promedio", "precio_sugerido"
    ])

if "proveedores" not in st.session_state:
    st.session_state.proveedores = pd.DataFrame(columns=[
        "id", "nombre", "nit"
    ])

if "kardex" not in st.session_state:
    st.session_state.kardex = pd.DataFrame(columns=[
        "fecha", "producto_id", "tipo",
        "unidades", "costo_unitario",
        "costo_total", "proveedor",
        "factura", "establecimiento"
    ])

if "stock" not in st.session_state:
    st.session_state.stock = pd.DataFrame(columns=[
        "producto_id", "establecimiento", "unidades"
    ])

# -----------------------------
# FUNCIONES
# -----------------------------

def obtener_costo_promedio(producto_id):
    movimientos = st.session_state.kardex[
        (st.session_state.kardex["producto_id"] == producto_id) &
        (st.session_state.kardex["tipo"] == "entrada")
    ]

    total_unidades = movimientos["unidades"].sum()
    total_costos = movimientos["costo_total"].sum()

    if total_unidades == 0:
        return 0

    return total_costos / total_unidades


def actualizar_stock(producto_id, establecimiento, unidades):
    df = st.session_state.stock

    filtro = (df["producto_id"] == producto_id) & (df["establecimiento"] == establecimiento)

    if filtro.any():
        st.session_state.stock.loc[filtro, "unidades"] += unidades
    else:
        nuevo = pd.DataFrame([{
            "producto_id": producto_id,
            "establecimiento": establecimiento,
            "unidades": unidades
        }])
        st.session_state.stock = pd.concat([df, nuevo], ignore_index=True)


# -----------------------------
# UI
# -----------------------------
st.title("📦 Sistema de Inventarios - PASRA / Electromiller")

menu = st.sidebar.selectbox("Menú", [
    "Productos",
    "Proveedores",
    "Entradas",
    "Salidas (Referencial)",
    "Kardex",
    "Reportes"
])

# -----------------------------
# PRODUCTOS
# -----------------------------
if menu == "Productos":
    st.header("📦 Crear Producto")

    with st.form("form_producto"):
        nombre = st.text_input("Nombre")
        categoria = st.text_input("Categoría")
        unidad = st.text_input("Unidad")
        precio = st.number_input("Precio sugerido", min_value=0.0)

        if st.form_submit_button("Guardar"):
            nuevo = pd.DataFrame([{
                "id": len(st.session_state.productos) + 1,
                "nombre": nombre,
                "categoria": categoria,
                "unidad": unidad,
                "costo_promedio": 0,
                "precio_sugerido": precio
            }])

            st.session_state.productos = pd.concat(
                [st.session_state.productos, nuevo],
                ignore_index=True
            )

    st.dataframe(st.session_state.productos)


# -----------------------------
# PROVEEDORES
# -----------------------------
elif menu == "Proveedores":
    st.header("🏢 Crear Proveedor")

    with st.form("form_proveedor"):
        nombre = st.text_input("Razón social")
        nit = st.text_input("NIT")

        if st.form_submit_button("Guardar"):
            nuevo = pd.DataFrame([{
                "id": len(st.session_state.proveedores) + 1,
                "nombre": nombre,
                "nit": nit
            }])

            st.session_state.proveedores = pd.concat(
                [st.session_state.proveedores, nuevo],
                ignore_index=True
            )

    st.dataframe(st.session_state.proveedores)


# -----------------------------
# ENTRADAS
# -----------------------------
elif menu == "Entradas":
    st.header("📥 Entrada de Inventario")

    productos = st.session_state.productos
    proveedores = st.session_state.proveedores

    if productos.empty or proveedores.empty:
        st.warning("Debe crear productos y proveedores primero.")
    else:
        producto = st.selectbox("Producto", productos["id"])
        proveedor = st.selectbox("Proveedor", proveedores["nombre"])

        unidades = st.number_input("Unidades", min_value=1)
        costo_unitario = st.number_input("Costo unitario", min_value=0.0)
        factura = st.text_input("Factura")
        fecha = st.date_input("Fecha", datetime.today())

        establecimiento = st.selectbox("Destino", [
            "PASRA", "Electromiller", "Ambos"
        ])

        if st.button("Registrar entrada"):
            costo_total = unidades * costo_unitario

            nuevo = pd.DataFrame([{
                "fecha": fecha,
                "producto_id": producto,
                "tipo": "entrada",
                "unidades": unidades,
                "costo_unitario": costo_unitario,
                "costo_total": costo_total,
                "proveedor": proveedor,
                "factura": factura,
                "establecimiento": establecimiento
            }])

            st.session_state.kardex = pd.concat(
                [st.session_state.kardex, nuevo],
                ignore_index=True
            )

            # actualizar stock
            if establecimiento == "Ambos":
                actualizar_stock(producto, "PASRA", unidades)
                actualizar_stock(producto, "Electromiller", unidades)
            else:
                actualizar_stock(producto, establecimiento, unidades)

            # actualizar costo promedio
            nuevo_costo = obtener_costo_promedio(producto)
            st.session_state.productos.loc[
                st.session_state.productos["id"] == producto,
                "costo_promedio"
            ] = nuevo_costo

            st.success("Entrada registrada")


# -----------------------------
# SALIDAS (REFERENCIAL)
# -----------------------------
elif menu == "Salidas (Referencial)":
    st.header("📤 Salidas (NO afectan costo)")

    producto = st.selectbox("Producto", st.session_state.productos["id"])
    unidades = st.number_input("Unidades", min_value=1)
    establecimiento = st.selectbox("Establecimiento", ["PASRA", "Electromiller"])

    if st.button("Registrar salida"):
        nuevo = pd.DataFrame([{
            "fecha": datetime.today(),
            "producto_id": producto,
            "tipo": "salida",
            "unidades": unidades,
            "costo_unitario": 0,
            "costo_total": 0,
            "proveedor": "",
            "factura": "",
            "establecimiento": establecimiento
        }])

        st.session_state.kardex = pd.concat(
            [st.session_state.kardex, nuevo],
            ignore_index=True
        )

        actualizar_stock(producto, establecimiento, -unidades)

        st.success("Salida registrada (no afecta costo)")


# -----------------------------
# KARDEX
# -----------------------------
elif menu == "Kardex":
    st.header("📊 Kardex por producto")

    producto = st.selectbox("Producto", st.session_state.productos["id"])

    df = st.session_state.kardex[
        st.session_state.kardex["producto_id"] == producto
    ]

    st.dataframe(df)


# -----------------------------
# REPORTES
# -----------------------------
elif menu == "Reportes":
    st.header("📈 Reportes")

    st.subheader("Stock por establecimiento")
    st.dataframe(st.session_state.stock)

    st.subheader("Costos promedio")
    st.dataframe(st.session_state.productos[[
        "nombre", "costo_promedio"
    ]])

    st.subheader("Entradas por proveedor")
    df = st.session_state.kardex[
        st.session_state.kardex["tipo"] == "entrada"
    ]

    st.dataframe(df.groupby("proveedor")["costo_total"].sum().reset_index())