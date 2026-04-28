import streamlit as st
import pandas as pd
import os

st.title("🤖 Batalla Robot Sumo 2026 - Registro de Equipos")

archivo_csv = "equipos2026.csv"

# Crear archivo si no existe
if not os.path.exists(archivo_csv):
    df = pd.DataFrame(columns=[
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

st.header("📋 Registro y Homologación")

institucion = st.text_input("🏫 Institución")
robot = st.text_input("🤖 Nombre del Robot")
categoria = st.selectbox(
    "🏁 Categoría",
    ["Autónomos", "Radio Controlados", "Libre"]
)
peso = st.number_input("⚖️ Peso del robot (kg)", min_value=0.0, max_value=5.0, step=0.1)
capitan = st.text_input("🧑‍✈️ Capitán del equipo")

if st.button("Registrar equipo"):
    if not institucion or not robot or not capitan:
        st.warning("⚠️ Completá todos los campos obligatorios")
    else:
        homologado = peso <= 3.5

        nuevo_equipo = pd.DataFrame([{
            "Institucion": institucion,
            "Robot": robot,
            "Categoria": categoria,
            "Peso": peso,
            "Capitan": capitan,
            "Homologado": "Sí" if homologado else "No"
        }])

        nuevo_equipo.to_csv(archivo_csv, mode='a', header=False, index=False)

        if homologado:
            st.success("✅ Equipo registrado y homologado")
        else:
            st.error("❌ Equipo registrado pero NO homologado (excede 3.5 kg)")

# Recargar datos actualizados
df = pd.read_csv(archivo_csv)

st.header("📊 Equipos registrados")

st.dataframe(df, use_container_width=True)
