import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
import os
import time

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(
    page_title="Dashboard Leads",
    layout="wide",
    page_icon="📊"
)

# --- CONEXIÓN A BASE DE DATOS ---
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    st.error("No se encontró DATABASE_URL")
    st.stop()

engine = create_engine(DATABASE_URL)

# --- ESTADO DE SESIÓN ---
if "last_row_count" not in st.session_state:
    st.session_state.last_row_count = 0

placeholder = st.empty()

# --- CONSULTA ---
query = """
SELECT
    nombre,
    telefono,
    correo,
    empresa,
    estado_validacion,
    clasificacion_ia,
    resumen_ia,
    accion_recomendada,
    vendedor_asignado,
    status_step,
    progress
FROM leads
ORDER BY created_at DESC
"""

df = pd.read_sql(query, engine)
current_count = len(df)

# --- SIMULACIÓN DE CORREO ENTRANTE ---
if current_count > st.session_state.last_row_count:
    with placeholder.container():
        st.markdown(
            """
            <div style="text-align:center; padding:60px;">
                <h1 style="font-size:70px;">📨</h1>
                <h2>Recibiendo nuevo correo...</h2>
            </div>
            """,
            unsafe_allow_html=True
        )
        time.sleep(3)

    st.session_state.last_row_count = current_count

# --- DASHBOARD ---
with placeholder.container():

    st.title("📊 Monitor de Leads")
    st.markdown("---")

    # ===== SECCIÓN 1: LEADS POR ESTADO =====
    st.subheader("📌 Leads por Estado")

    df_estado = (
        df.groupby("status_step")
        .size()
        .reset_index(name="Total")
        .sort_values("Total", ascending=False)
    )

    st.dataframe(df_estado, hide_index=True, use_container_width=True)

    st.divider()

    # ===== SECCIÓN 2: LEADS POR VENDEDOR =====
    st.subheader("👤 Leads por Vendedor")

    df_vendedor = (
        df.fillna({"vendedor_asignado": "Sin asignar"})
        .groupby("vendedor_asignado")
        .size()
        .reset_index(name="Total")
        .sort_values("Total", ascending=False)
    )

    st.dataframe(df_vendedor, hide_index=True, use_container_width=True)

    st.divider()

    # ===== SECCIÓN 3: HOT / WARM / COLD =====
    st.subheader("🔥 Clasificación IA")

    df_clasificacion = (
        df.groupby("clasificacion_ia")
        .size()
        .reset_index(name="Total")
        .sort_values("Total", ascending=False)
    )

    st.dataframe(df_clasificacion, hide_index=True, use_container_width=True)

    st.divider()

    # ===== TABLA DETALLADA (SIN ID NI CREATED_AT) =====
    st.subheader("📋 Leads Recientes")

    st.dataframe(
        df,
        column_config={
            "progress": st.column_config.ProgressColumn(
                "Progreso",
                min_value=0,
                max_value=100,
                format="%d%%"
            )
        },
        use_container_width=True,
        hide_index=True
    )

# --- AUTO REFRESH ---
time.sleep(5)
st.experimental_rerun()

