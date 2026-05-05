import streamlit as st
import pandas as pd
import os

st.title("Torneo Robot Sumo - Registro de Equipos")

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

import random

def generar_grupos_balanceados(equipos, max_por_grupo=4):
    total = len(equipos)

    if total <= 4:
        return [equipos]

    # calcular cantidad de grupos
    num_grupos = total // max_por_grupo
    resto = total % max_por_grupo

    # si sobra 1 → redistribuir para evitar grupo de 1
    if resto == 1:
        num_grupos -= 1
        resto += max_por_grupo

    grupos = []
    inicio = 0

    for i in range(num_grupos):
        size = max_por_grupo
        if resto > 0:
            size -= 1
            resto -= 1

        grupos.append(equipos[inicio:inicio+size])
        inicio += size

    # agregar últimos si quedan
    if inicio < total:
        grupos.append(equipos[inicio:])

    return grupos

st.header("🏆 Generación de Grupos")

if st.button("🎯 Generar grupos por categoría"):

    df = pd.read_csv(archivo_csv)

    # Solo homologados
    df_validos = df[df["Homologado"] == "Sí"]

    if df_validos.empty:
        st.warning("No hay equipos homologados")
    else:
        grupos_generados = {}

        categorias = df_validos["Categoria"].unique()

        for categoria in categorias:
            equipos_cat = df_validos[df_validos["Categoria"] == categoria]
            equipos_lista = equipos_cat.to_dict("records")

            random.shuffle(equipos_lista)

            grupos = generar_grupos_balanceados(equipos_lista)

            grupos_generados[categoria] = grupos

        st.session_state.grupos = grupos_generados

        st.success("✅ Grupos generados correctamente")

if "grupos" in st.session_state:

    st.header("📊 Grupos generados")

    for categoria, grupos in st.session_state.grupos.items():

        st.subheader(f"🏁 Categoría: {categoria}")

        for i, grupo in enumerate(grupos):
            st.markdown(f"**Grupo {i+1}**")

            for equipo in grupo:
                st.write(f"- {equipo['Robot']} ({equipo['Institucion']})")

def generar_fixture_round_robin(grupo):
    equipos = grupo.copy()

    # Si es impar, agregamos descanso (bye)
    if len(equipos) % 2 != 0:
        equipos.append(None)

    n = len(equipos)
    rondas = []

    for i in range(n - 1):
        ronda = []

        for j in range(n // 2):
            equipoA = equipos[j]
            equipoB = equipos[n - 1 - j]

            if equipoA and equipoB:
                ronda.append({
                    "equipoA": equipoA,
                    "equipoB": equipoB,
                    "resultado": None
                })

        rondas.append(ronda)

        # Rotación (algoritmo clásico)
        equipos = [equipos[0]] + [equipos[-1]] + equipos[1:-1]

    return rondas

st.header("🥊 Generar Fixture")

if "grupos" in st.session_state:

    if st.button("⚔️ Generar combates (Round Robin)"):

        fixtures = {}

        for categoria, grupos in st.session_state.grupos.items():

            fixtures[categoria] = []

            for i, grupo in enumerate(grupos):

                fixture_grupo = generar_fixture_round_robin(grupo)

                fixtures[categoria].append({
                    "grupo": i + 1,
                    "combates": fixture_grupo
                })

        st.session_state.fixtures = fixtures

        st.success("✅ Fixture generado correctamente")

if "fixtures" in st.session_state:

    st.header("📅 Combates por rondas")

    for categoria, grupos in st.session_state.fixtures.items():

        st.subheader(f"🏁 Categoría: {categoria}")

        for grupo in grupos:

            st.markdown(f"**Grupo {grupo['grupo']}**")

            for i, ronda in enumerate(grupo["combates"]):
                st.markdown(f"🔵 Ronda {i+1}")

                for combate in ronda:
                    st.write(
                        f"🥊 {combate['equipoA']['Robot']} vs {combate['equipoB']['Robot']}"
                    )
