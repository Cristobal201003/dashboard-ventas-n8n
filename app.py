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

# --- ESTILOS PERSONALIZADOS ---
st.markdown("""
<style>
.metric-card {
    background-color: #f9fafb;
    padding: 20px;
    border-radius: 16px;
    box-shadow: 0px 4px 12px rgba(0,0,0,0.05);
    text-align: center;
}
.metric-title {
    font-size: 18px;
    color: #6b7280;
}
.metric-value {
    font-size: 36px;
    font-weight: bold;
}
.section-title {
    font-size: 26px;
    font-weight: 700;
    margin-top: 20px;
}
</style>
""", unsafe_allow_html=True)

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

    st.title("📊 Monitor Inteligente de Leads")
    st.markdown("---")

    # ===== TARJETAS RESUMEN =====
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Total de Leads</div>
            <div class="metric-value">{len(df)}</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        hot_count = (df["clasificacion_ia"] == "Hot").sum()
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Leads Hot 🔥</div>
            <div class="metric-value">{hot_count}</div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        sin_asignar = df["vendedor_asignado"].isna().sum()
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Sin Vendedor</div>
            <div class="metric-value">{sin_asignar}</div>
        </div>
        """, unsafe_allow_html=True)

    st.divider()

    # ===== SECCIÓN 1: LEADS RECIENTES =====
    st.markdown('<div class="section-title">📋 Leads Recientes</div>', unsafe_allow_html=True)

    df_display = df.rename(columns={
        "resumen_ia": "Resumen del proceso",
        "clasificacion_ia": "Clasificación IA"
    })

    st.dataframe(
        df_display,
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

    st.divider()

    # ===== SECCIÓN 2: LEADS POR ESTADO =====
    st.markdown('<div class="section-title">📌 Leads por Estado</div>', unsafe_allow_html=True)

    df_estado = (
        df.groupby("status_step")
        .size()
        .reset_index(name="Total")
        .sort_values("Total", ascending=False)
    )

    st.dataframe(df_estado, hide_index=True, use_container_width=True)

    st.divider()

    # ===== SECCIÓN 3: LEADS POR VENDEDOR =====
    st.markdown('<div class="section-title">👤 Leads por Vendedor</div>', unsafe_allow_html=True)

    df_vendedor = (
        df.fillna({"vendedor_asignado": "Sin asignar"})
        .groupby("vendedor_asignado")
        .size()
        .reset_index(name="Total")
        .sort_values("Total", ascending=False)
    )

    st.dataframe(df_vendedor, hide_index=True, use_container_width=True)

    st.divider()

    # ===== SECCIÓN 4: CLASIFICACIÓN IA =====
    st.markdown('<div class="section-title">🔥 Clasificación IA</div>', unsafe_allow_html=True)

    df_clasificacion = (
        df.groupby("clasificacion_ia")
        .size()
        .reset_index(name="Total")
        .sort_values("Total", ascending=False)
    )

    st.dataframe(df_clasificacion, hide_index=True, use_container_width=True)

# --- AUTO REFRESH ---
time.sleep(5)
st.rerun()
