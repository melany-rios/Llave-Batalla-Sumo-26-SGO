import streamlit as st
import pandas as pd
import os

st.title("🤖 Torneo Robot Sumo - Registro de Equipos")

archivo_csv = "equipos.csv"

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

# Inicializar valores por defecto
if "institucion" not in st.session_state:
    st.session_state.institucion = ""
    st.session_state.robot = ""
    st.session_state.categoria = "Autónomos"
    st.session_state.peso = 0.0
    st.session_state.capitan = ""

st.header("📋 Registro y Homologación")

institucion = st.text_input("🏫 Institución", key="institucion")
robot = st.text_input("🤖 Nombre del Robot", key="robot")
categoria = st.selectbox(
    "🏁 Categoría",
    ["Autónomos", "Radio Controlados", "Libre"],
    key="categoria"
)
peso = st.number_input(
    "⚖️ Peso del robot (kg)",
    min_value=0.0,
    max_value=5.0,
    step=0.1,
    key="peso"
)
capitan = st.text_input("🧑‍✈️ Capitán del equipo", key="capitan")

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
            st.error("❌ Equipo registrado pero NO homologado")

        # 🔥 RESET DE CAMPOS
        st.session_state.institucion = ""
        st.session_state.robot = ""
        st.session_state.categoria = "Autónomos"
        st.session_state.peso = 0.0
        st.session_state.capitan = ""

        st.rerun()  # refresca la app

# Mostrar tabla
df = pd.read_csv(archivo_csv)

st.header("📊 Equipos registrados")
st.dataframe(df, use_container_width=True)
