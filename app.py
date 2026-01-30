import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
import os
import time

#  CONFIGURACIÓN DE PÁGINA 
st.set_page_config(
    page_title="Dashboard de Leads",
    layout="wide",
    page_icon="📊"
)

#  ESTILOS 
st.markdown("""
<style>
.metric-card {
    background-color: #ffffff;
    padding: 24px;
    border-radius: 18px;
    box-shadow: 0 8px 20px rgba(0,0,0,0.06);
    text-align: center;
}
.metric-title {
    font-size: 16px;
    color: #6b7280;
}
.metric-value {
    font-size: 40px;
    font-weight: 700;
}
.section-title {
    font-size: 26px;
    font-weight: 700;
    margin: 25px 0 10px 0;
}
</style>
""", unsafe_allow_html=True)

# CONEXIÓN DB 
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    st.error("DATABASE_URL no encontrada")
    st.stop()

engine = create_engine(DATABASE_URL)

#  CONSULTA 
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

#  DASHBOARD 
st.title("📊 Monitor Inteligente de Leads")
st.caption("Actualización automática cada 5 segundos")
st.divider()

#  MÉTRICAS 
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
        <div class="metric-title">Leads Calientes 🔥</div>
        <div class="metric-value">{hot_count}</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    sin_asignar = df["vendedor_asignado"].isna().sum()
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">Sin Vendedor Asignado</div>
        <div class="metric-value">{sin_asignar}</div>
    </div>
    """, unsafe_allow_html=True)

#  TABLA PRINCIPAL 
st.markdown('<div class="section-title">📋 Leads Recientes</div>', unsafe_allow_html=True)

df_display = df.rename(columns={
    "nombre": "Nombre",
    "telefono": "Teléfono",
    "correo": "Correo Electrónico",
    "empresa": "Empresa",
    "estado_validacion": "Estado de Validación",
    "clasificacion_ia": "Clasificación IA",
    "resumen_ia": "Resumen del Proceso",
    "accion_recomendada": "Acción Recomendada",
    "vendedor_asignado": "Vendedor Asignado",
    "status_step": "Etapa del Proceso",
    "progress": "Avance"
})

st.dataframe(
    df_display,
    column_config={
        "Avance": st.column_config.ProgressColumn(
            "Avance",
            min_value=0,
            max_value=100,
            format="%d%%"
        )
    },
    use_container_width=True,
    hide_index=True
)

# AGRUPACIONES 
st.divider()
st.markdown('<div class="section-title">📌 Leads por Etapa</div>', unsafe_allow_html=True)

df_estado = (
    df.groupby("status_step")
    .size()
    .reset_index(name="Total")
    .rename(columns={
        "status_step": "Etapa del Proceso"
    })
    .sort_values("Total", ascending=False)
)

st.dataframe(df_estado, hide_index=True, use_container_width=True)

st.divider()
st.markdown('<div class="section-title">👤 Leads por Vendedor</div>', unsafe_allow_html=True)

df_vendedor = (
    df.fillna({"vendedor_asignado": "Sin asignar"})
    .groupby("vendedor_asignado")
    .size()
    .reset_index(name="Total")
    .rename(columns={
        "vendedor_asignado": "Vendedor"
    })
    .sort_values("Total", ascending=False)
)

st.dataframe(df_vendedor, hide_index=True, use_container_width=True)

st.divider()
st.markdown('<div class="section-title">🔥 Clasificación IA</div>', unsafe_allow_html=True)

df_clasificacion = (
    df.groupby("clasificacion_ia")
    .size()
    .reset_index(name="Total")
    .rename(columns={
        "clasificacion_ia": "Clasificación"
    })
    .sort_values("Total", ascending=False)
)

st.dataframe(df_clasificacion, hide_index=True, use_container_width=True)

# AUTO REFRESH 
time.sleep(5)
st.rerun()


