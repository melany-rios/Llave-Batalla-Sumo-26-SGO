import streamlit as st
import pandas as pd
import os

st.title("🤖 Torneo Robot Sumo - Registro de Equipos")

archivo_csv = "equipos.csv"

# Crear archivo si no existe
if not os.path.exists(archivo_csv):
    df = pd.DataFrame(columns=[
        "Seleccionar",
        "Institucion",
        "Robot",
        "Categoria",
        "Peso",
        "Capitan",
        "Homologado"
    ])
    df.to_csv(archivo_csv, index=False)

# Cargar datos
df = pd.read_csv(archivo_csv)

# Si no existe la columna Seleccionar, agregarla
if "Seleccionar" not in df.columns:
    df.insert(0, "Seleccionar", False)

# FORMULARIO
st.header("📋 Registro y Homologación")

with st.form("form_registro", clear_on_submit=True):

    institucion = st.text_input("🏫 Institución")
    robot = st.text_input("🤖 Nombre del Robot")

    categoria = st.selectbox(
        "🏁 Categoría",
        ["Autónomos", "Radio Controlados", "Libre"]
    )

    peso = st.number_input(
        "⚖️ Peso del robot (kg)",
        min_value=0.0,
        max_value=5.0,
        step=0.001,
        format="%.3f"
    )

    capitan = st.text_input("🧑‍✈️ Capitán del equipo")

    submit = st.form_submit_button("Registrar equipo")

    if submit:
        if not institucion or not robot or not capitan:
            st.warning("⚠️ Completá todos los campos obligatorios")
        else:
            homologado = peso <= 3.5

            nuevo = pd.DataFrame([{
                "Seleccionar": False,
                "Institucion": institucion,
                "Robot": robot,
                "Categoria": categoria,
                "Peso": peso,
                "Capitan": capitan,
                "Homologado": "Sí" if homologado else "No"
            }])

            df = pd.concat([df, nuevo], ignore_index=True)
            df.to_csv(archivo_csv, index=False)

            st.success("✅ Equipo registrado")

# 🔄 Editor interactivo
st.header("📊 Gestión de Equipos")

edited_df = st.data_editor(
    df,
    num_rows="dynamic",
    use_container_width=True,
    key="editor"
)

# 🔁 Recalcular homologación si editan peso
edited_df["Homologado"] = edited_df["Peso"].apply(
    lambda x: "Sí" if float(x) <= 3.5 else "No"
)

# 💾 Guardar cambios
if st.button("💾 Guardar cambios"):
    edited_df.to_csv(archivo_csv, index=False)
    st.success("Cambios guardados correctamente")
    st.rerun()

# 🗑️ Eliminar con confirmación
st.subheader("🗑️ Eliminar equipos seleccionados")

seleccionados = edited_df[edited_df["Seleccionar"] == True]

if not seleccionados.empty:
    st.warning(f"⚠️ Vas a eliminar {len(seleccionados)} equipo(s)")

    confirmar = st.checkbox("Confirmar eliminación")

    if confirmar:
        if st.button("❌ Eliminar definitivamente"):
            df_filtrado = edited_df[edited_df["Seleccionar"] == False]
            df_filtrado.to_csv(archivo_csv, index=False)

            st.success("Equipos eliminados correctamente")
            st.rerun()
else:
    st.info("No hay equipos seleccionados")
