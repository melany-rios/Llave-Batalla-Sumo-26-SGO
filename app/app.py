import streamlit as st
import pandas as pd
import os
import random
st.set_page_config(layout="wide")

def mostrar_combate(equipoA, equipoB):

    col1, col2, col3 = st.columns([5,1,5])

    with col1:
        st.markdown(f"""
        <div style='
            padding:30px;
            border-radius:15px;
            border:3px solid #00ADB5;
            text-align:center;
            font-size:28px;
            font-weight:bold;
        '>
        🤖 {equipoA}
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("<h2 style='text-align:center;'>VS</h2>", unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div style='
            padding:30px;
            border-radius:15px;
            border:3px solid #FF5722;
            text-align:center;
            font-size:28px;
            font-weight:bold;
        '>
        🤖 {equipoB}
        </div>
        """, unsafe_allow_html=True)

st.title("Torneo Robot Sumo - Registro de Equipos")

archivo_csv = "equipos.csv"

# =========================
# CREAR CSV SI NO EXISTE
# =========================
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

# =========================
# CARGAR DATOS
# =========================
df = pd.read_csv(archivo_csv)

if "Seleccionar" not in df.columns:
    df.insert(0, "Seleccionar", False)

# =========================
# FORMULARIO
# =========================
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
            st.warning("⚠️ Completá todos los campos")
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
            st.rerun()

# =========================
# TABLA EDITABLE
# =========================
st.header("📊 Gestión de Equipos")

edited_df = st.data_editor(
    df,
    num_rows="dynamic",
    use_container_width=True
)

# Recalcular homologación
edited_df["Homologado"] = edited_df["Peso"].apply(
    lambda x: "Sí" if float(x) <= 3.5 else "No"
)

if st.button("💾 Guardar cambios"):
    edited_df.to_csv(archivo_csv, index=False)
    st.success("Cambios guardados")
    st.rerun()

# =========================
# ELIMINAR
# =========================
st.subheader("🗑️ Eliminar equipos")

seleccionados = edited_df[edited_df["Seleccionar"] == True]

if not seleccionados.empty:
    st.warning(f"Eliminar {len(seleccionados)} equipo(s)")

    if st.checkbox("Confirmar eliminación"):
        if st.button("Eliminar"):
            df_filtrado = edited_df[edited_df["Seleccionar"] == False]
            df_filtrado.to_csv(archivo_csv, index=False)
            st.success("Eliminados correctamente")
            st.rerun()

# =========================
# GRUPOS
# =========================
def generar_grupos_balanceados(equipos):
    random.shuffle(equipos)
    total = len(equipos)

    if total <= 4:
        return [equipos]

    num_grupos = total // 4
    resto = total % 4

    if resto == 1:
        num_grupos -= 1
        resto += 4

    grupos = []
    inicio = 0

    for i in range(num_grupos):
        size = 4
        if resto > 0:
            size -= 1
            resto -= 1

        grupos.append(equipos[inicio:inicio+size])
        inicio += size

    if inicio < total:
        grupos.append(equipos[inicio:])

    return grupos

st.header("🏆 Generar Grupos")

if st.button("🎯 Generar grupos"):

    df = pd.read_csv(archivo_csv)
    df_validos = df[df["Homologado"] == "Sí"]

    if df_validos.empty:
        st.warning("No hay equipos homologados")
    else:
        grupos_generados = {}

        for categoria in df_validos["Categoria"].unique():

            equipos = df_validos[df_validos["Categoria"] == categoria].to_dict("records")
            grupos = generar_grupos_balanceados(equipos)

            grupos_generados[categoria] = grupos

        st.session_state.grupos = grupos_generados

        # 🔥 limpiar fixtures viejos
        st.session_state.pop("fixtures", None)

        st.success("Grupos generados")

# Mostrar grupos
if "grupos" in st.session_state:

    st.header("📊 Grupos")

    for categoria, grupos in st.session_state.grupos.items():

        st.subheader(categoria)

        for i, grupo in enumerate(grupos):
            st.markdown(f"**Grupo {i+1}**")

            for equipo in grupo:
                st.write(f"- {equipo['Robot']}")

# =========================
# FIXTURE ROUND ROBIN
# =========================
def generar_fixture(grupo):
    equipos = grupo.copy()

    if len(equipos) % 2 != 0:
        equipos.append(None)

    n = len(equipos)
    rondas = []

    for i in range(n - 1):
        ronda = []

        for j in range(n // 2):
            a = equipos[j]
            b = equipos[n - 1 - j]

            if a and b:
                ronda.append({
                    "equipoA": a,
                    "equipoB": b,
                    "resultado": None
                })

        rondas.append(ronda)

        equipos = [equipos[0]] + [equipos[-1]] + equipos[1:-1]

    return rondas

# =========================
# GENERAR FIXTURE
# =========================
st.header("🥊 Fixture")

if "grupos" in st.session_state:

    if st.button("⚔️ Generar combates"):

        fixtures = {}

        for categoria, grupos in st.session_state.grupos.items():

            fixtures[categoria] = []

            for i, grupo in enumerate(grupos):

                rondas = generar_fixture(grupo)

                fixtures[categoria].append({
                    "grupo": i+1,
                    "rondas": rondas
                })

        st.session_state.fixtures = fixtures

        st.success("Fixture generado")

# =========================
# MOSTRAR FIXTURE
# =========================
if "fixtures" in st.session_state:

    st.header("📺 Combates + Resultados")

    for categoria, grupos in st.session_state.fixtures.items():

        st.subheader(f"🏁 {categoria}")

        for g_idx, grupo in enumerate(grupos):

            st.markdown(f"## Grupo {grupo['grupo']}")

            for r_idx, ronda in enumerate(grupo["rondas"]):

                st.markdown(f"### 🔵 Ronda {r_idx+1}")

                for c_idx, combate in enumerate(ronda):

                    equipoA = combate.get("equipoA")
                    equipoB = combate.get("equipoB")
                
                    if not equipoA or not equipoB:
                        continue
                
                    # 🔥 asegurar estructura
                    if "resultado" not in combate:
                        combate["resultado"] = None
                
                    nombreA = equipoA["Robot"]
                    nombreB = equipoB["Robot"]
                
                    mostrar_combate(nombreA, nombreB)
                
                    key = f"{categoria}_{g_idx}_{r_idx}_{c_idx}"
                
                    opciones = ["Equipo A", "Equipo B", "Empate"]
                    resultado_actual = combate.get("resultado")
                
                    index = opciones.index(resultado_actual) if resultado_actual in opciones else 0
                
                    resultado = st.radio(
                        "Resultado",
                        opciones,
                        index=index,
                        key=key,
                        horizontal=True
                    )
                
                    st.session_state.fixtures[categoria][g_idx]["rondas"][r_idx][c_idx]["resultado"] = resultado
                
                    st.markdown("---")

if st.button("💾 Guardar resultados"):
    st.success("Resultados guardados en memoria")

def mostrar_combate(equipoA, equipoB):

    col1, col2, col3 = st.columns([5,1,5])

    with col1:
        st.markdown(f"""
        <div style='
            padding:30px;
            border-radius:15px;
            border:3px solid #00ADB5;
            text-align:center;
            font-size:28px;
            font-weight:bold;
        '>
        🤖 {equipoA}
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("<h2 style='text-align:center;'>VS</h2>", unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div style='
            padding:30px;
            border-radius:15px;
            border:3px solid #FF5722;
            text-align:center;
            font-size:28px;
            font-weight:bold;
        '>
        🤖 {equipoB}
        </div>
        """, unsafe_allow_html=True)

def calcular_tabla(grupo):

    stats = {}

    # Inicializar equipos
    for equipo in grupo:
        nombre = equipo["Robot"]

        stats[nombre] = {
            "Equipo": nombre,
            "PJ": 0,
            "PG": 0,
            "PE": 0,
            "PP": 0,
            "PTS": 0
        }

    # Recorrer combates
    for ronda in grupo:
        for combate in ronda:

            equipoA = combate.get("equipoA")
            equipoB = combate.get("equipoB")
            resultado = combate.get("resultado")

            if not equipoA or not equipoB or not resultado:
                continue

            A = equipoA["Robot"]
            B = equipoB["Robot"]

            stats[A]["PJ"] += 1
            stats[B]["PJ"] += 1

            if resultado == "Equipo A":
                stats[A]["PG"] += 1
                stats[A]["PTS"] += 3
                stats[B]["PP"] += 1

            elif resultado == "Equipo B":
                stats[B]["PG"] += 1
                stats[B]["PTS"] += 3
                stats[A]["PP"] += 1

            elif resultado == "Empate":
                stats[A]["PE"] += 1
                stats[B]["PE"] += 1
                stats[A]["PTS"] += 1
                stats[B]["PTS"] += 1

    df_tabla = pd.DataFrame(stats.values())

    # Ordenar
    df_tabla = df_tabla.sort_values(
        by=["PTS", "PG"],
        ascending=False
    ).reset_index(drop=True)

    return df_tabla

st.header("📊 Tabla de posiciones")

if "fixtures" in st.session_state:

    for categoria, grupos in st.session_state.fixtures.items():

        st.subheader(f"🏁 {categoria}")

        for grupo in grupos:

            st.markdown(f"### Grupo {grupo['grupo']}")

            tabla = calcular_tabla(grupo["rondas"])

            st.dataframe(tabla, use_container_width=True)

def resaltar_top(df):
    return ['background-color: #00FFAA' if i < 2 else '' for i in range(len(df))]

st.dataframe(tabla.style.apply(resaltar_top, axis=0))
